import jsPDF from 'jspdf';
import { format, subDays } from 'date-fns';
import { TrackedSupplement, IntakeLog, SymptomLog } from '@/contexts/tracker-context';

type ProgressData = {
  date: string;
  consistency: number;
  taken: number;
  total: number;
};

export type ProgressReportData = {
  userName: string;
  trackedSupplements: TrackedSupplement[];
  intakeLogs: IntakeLog[];
  symptomLogs: SymptomLog[];
  streak: number;
  improvement: number;
  progressData: ProgressData[];
  generatedDate: string;
};

export async function generateProgressReport(reportData: ProgressReportData): Promise<void> {
  // Create a new jsPDF instance
  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4'
  });
  
  // PDF dimensions
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 10;
  
  // Add header with logo and title
  pdf.setFontSize(20);
  pdf.setTextColor(180, 134, 0); // Gold color
  pdf.text('Take Your Vitamins', margin, margin + 10);
  pdf.setFontSize(16);
  pdf.text('Progress Report', margin, margin + 18);
  
  // Add generation info
  pdf.setFontSize(10);
  pdf.setTextColor(100, 100, 100);
  pdf.text(`Generated for: ${reportData.userName}`, margin, margin + 28);
  pdf.text(`Date: ${reportData.generatedDate}`, margin, margin + 34);
  
  // Add summary section
  pdf.setFontSize(14);
  pdf.setTextColor(0, 0, 0);
  pdf.text('Summary', margin, margin + 45);
  
  pdf.setFontSize(11);
  pdf.setTextColor(60, 60, 60);
  pdf.text(`Current Streak: ${reportData.streak} days`, margin, margin + 52);
  pdf.text(`Weekly Improvement: +${reportData.improvement}%`, margin, margin + 58);
  pdf.text(`Total Supplements Tracked: ${reportData.trackedSupplements.length}`, margin, margin + 64);
  
  // Add supplements section
  pdf.setFontSize(14);
  pdf.setTextColor(0, 0, 0);
  pdf.text('Tracked Supplements', margin, margin + 75);
  
  // List supplements
  let yPos = margin + 82;
  reportData.trackedSupplements.forEach((supplement, index) => {
    if (yPos > pageHeight - margin) {
      pdf.addPage();
      yPos = margin + 10;
    }
    
    pdf.setFontSize(12);
    pdf.setTextColor(0, 0, 0);
    pdf.text(`${index + 1}. ${supplement.supplementName}`, margin, yPos);
    
    pdf.setFontSize(10);
    pdf.setTextColor(80, 80, 80);
    pdf.text(`Dosage: ${supplement.dosage} ${supplement.unit || 'units'}`, margin + 5, yPos + 6);
    pdf.text(`Frequency: ${supplement.frequency || 'Daily'}`, margin + 5, yPos + 12);
    if (supplement.notes) {
      pdf.text(`Notes: ${supplement.notes}`, margin + 5, yPos + 18);
      yPos += 24;
    } else {
      yPos += 18;
    }
  });
  
  // Add consistency chart section
  pdf.addPage();
  pdf.setFontSize(14);
  pdf.setTextColor(0, 0, 0);
  pdf.text('Consistency Chart (Last 14 Days)', margin, margin + 10);
  
  // Create a bar chart image using canvas
  if (reportData.progressData.length > 0) {
    // Draw the chart
    const chartData = reportData.progressData;
    const chartWidth = pageWidth - (margin * 2);
    const chartHeight = 50;
    const barWidth = chartWidth / chartData.length * 0.8;
    const spacing = chartWidth / chartData.length * 0.2;
    const maxPercentage = 100;
    
    // Create in-memory canvas for chart
    const canvas = document.createElement('canvas');
    canvas.width = chartWidth * 5; // Multiply by 5 for high resolution
    canvas.height = chartHeight * 5;
    const ctx = canvas.getContext('2d');
    
    if (ctx) {
      ctx.scale(5, 5); // Scale for high resolution
      
      // Draw chart background
      ctx.fillStyle = '#f8f8f8';
      ctx.fillRect(0, 0, chartWidth, chartHeight);
      
      // Draw horizontal grid lines
      ctx.strokeStyle = '#dddddd';
      ctx.lineWidth = 0.2;
      for (let i = 0; i <= 10; i++) {
        const y = chartHeight - (i * chartHeight / 10);
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(chartWidth, y);
        ctx.stroke();
      }
      
      // Draw bars
      chartData.forEach((data, index) => {
        const x = (index * (barWidth + spacing)) + spacing / 2;
        const barHeight = (data.consistency / maxPercentage) * chartHeight;
        const y = chartHeight - barHeight;
        
        // Bar
        ctx.fillStyle = '#f59e0b';
        ctx.fillRect(x, y, barWidth, barHeight);
        
        // Date label
        ctx.fillStyle = '#000000';
        ctx.font = '5px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(data.date.toString(), x + barWidth / 2, chartHeight - 2);
        
        // Percentage label
        if (data.consistency > 0) {
          ctx.fillStyle = '#000000';
          ctx.font = '6px Arial';
          ctx.textAlign = 'center';
          ctx.fillText(`${data.consistency}%`, x + barWidth / 2, y - 2);
        }
      });
      
      // Convert canvas to image
      const chartImg = canvas.toDataURL('image/png');
      pdf.addImage(chartImg, 'PNG', margin, margin + 15, chartWidth, chartHeight);
    }
  }
  
  // Add recent activity section
  pdf.setFontSize(14);
  pdf.text('Recent Activity', margin, margin + 75);
  
  // Recent intake logs (last 7 days)
  const today = new Date();
  const sevenDaysAgo = subDays(today, 7);
  const recentLogs = reportData.intakeLogs.filter(log => {
    const logDate = new Date(log.intake_date);
    return logDate >= sevenDaysAgo && logDate <= today;
  });
  
  if (recentLogs.length > 0) {
    pdf.setFontSize(12);
    pdf.text('Recent Supplement Intake', margin, margin + 85);
    
    let yPos = margin + 95;
    recentLogs.forEach((log) => {
      if (yPos > pageHeight - margin) {
        pdf.addPage();
        yPos = margin + 10;
      }
      
      // Find supplement name
      const supplement = reportData.trackedSupplements.find(s => s.id === log.tracked_supplement_id);
      const supplementName = supplement ? supplement.supplementName : 'Unknown';
      
      pdf.setFontSize(10);
      pdf.setTextColor(0, 0, 0);
      pdf.text(`${log.intake_date} - ${supplementName}`, margin, yPos);
      
      if (log.notes) {
        pdf.setFontSize(9);
        pdf.setTextColor(100, 100, 100);
        pdf.text(`Notes: ${log.notes}`, margin + 5, yPos + 5);
        yPos += 10;
      } else {
        yPos += 6;
      }
    });
  } else {
    pdf.setFontSize(10);
    pdf.text('No recent supplement intake recorded in the last 7 days.', margin, margin + 85);
  }
  
  // Add symptoms section if available
  if (reportData.symptomLogs.length > 0) {
    if (yPos > pageHeight - margin - 30) {
      pdf.addPage();
      yPos = margin + 10;
    } else {
      yPos += 10;
    }
    
    pdf.setFontSize(12);
    pdf.setTextColor(0, 0, 0);
    pdf.text('Recent Symptoms', margin, yPos);
    yPos += 10;
    
    // Recent symptom logs (last 7 days)
    const recentSymptoms = reportData.symptomLogs.filter(log => {
      const logDate = new Date(log.date);
      return logDate >= sevenDaysAgo && logDate <= today;
    });
    
    if (recentSymptoms.length > 0) {
      recentSymptoms.forEach((symptom) => {
        if (yPos > pageHeight - margin) {
          pdf.addPage();
          yPos = margin + 10;
        }
        
        pdf.setFontSize(10);
        pdf.setTextColor(0, 0, 0);
        pdf.text(`${symptom.date} - ${symptom.symptomName} (Severity: ${symptom.severity})`, margin, yPos);
        
        if (symptom.notes) {
          pdf.setFontSize(9);
          pdf.setTextColor(100, 100, 100);
          pdf.text(`Notes: ${symptom.notes}`, margin + 5, yPos + 5);
          yPos += 10;
        } else {
          yPos += 6;
        }
      });
    } else {
      pdf.setFontSize(10);
      pdf.text('No symptoms recorded in the last 7 days.', margin, yPos);
    }
  }
  
  // Add footer
  pdf.setFontSize(8);
  pdf.setTextColor(150, 150, 150);
  const totalPages = pdf.getNumberOfPages();
  
  for (let i = 1; i <= totalPages; i++) {
    pdf.setPage(i);
    pdf.text(`Page ${i} of ${totalPages}`, pageWidth - margin - 20, pageHeight - margin);
    pdf.text('Take Your Vitamins - Health Progress Report', margin, pageHeight - margin);
  }
  
  // Save PDF
  pdf.save(`TYV_Progress_Report_${format(new Date(), 'yyyy-MM-dd')}.pdf`);
} 