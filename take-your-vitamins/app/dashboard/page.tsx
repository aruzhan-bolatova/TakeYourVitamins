"use client"

import { useState, useEffect } from "react"
import { useAuth } from "@/contexts/auth-context"
import { useTracker, type TrackedSupplement, type IntakeLog } from "@/contexts/tracker-context"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { Pill, Search, TrendingUp, Activity, FileDown, Award } from "lucide-react"
import { format, startOfWeek, addDays, subDays, isAfter, parseISO } from "date-fns"
import { Calendar } from "@/components/ui/calendar"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { CategorySymptomLogger } from "@/components/category-symptom-logger"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { generateProgressReport } from "@/lib/pdf-generator"
import { toast } from "@/components/ui/use-toast"
import { useMemo, useCallback } from "react"

export default function DashboardPage() {
    const { user } = useAuth()
    const {
        trackedSupplements,
        deleteIntakeLog,
        intakeLogs,
        logIntake,
        getIntakeLogsForDate,
        symptomLogs,
        formatLocalDate,
        getTodayLocalDate,
        getDatesWithSymptoms
    } = useTracker()

    const [selectedDate, setSelectedDate] = useState(new Date());
    const [weekStartDate, setWeekStartDate] = useState(
        startOfWeek(new Date(), { weekStartsOn: 1 })
    );
    const [datesWithSymptoms, setDatesWithSymptoms] = useState<Date[]>([]);
    const [symptomsDialogOpen, setSymptomsDialogOpen] = useState(false);
    const [supplementsTaken, setSupplementsTaken] = useState<
        Record<string, Record<number, boolean>>
    >({});

    const formattedDate = useMemo(
        () => format(selectedDate, 'EEEE, MMMM d, yyyy'),
        [selectedDate]
    );
    const dateString = useMemo(
        () => format(selectedDate, 'yyyy-MM-dd'),
        [selectedDate]
    );

    const weekdays = useMemo(() => ['M', 'T', 'W', 'T', 'F', 'S', 'S'], []);

    // Calculate streak and progress
    const [streak, setStreak] = useState(0)
    const [improvement, setImprovement] = useState(0)
    const [daysToNextAchievement, setDaysToNextAchievement] = useState(0)
    const [progressData, setProgressData] = useState<Array<{ date: string; consistency: number; taken: number; total: number }>>([])

    // Update dates with symptoms whenever symptomLogs changes
    useEffect(() => {
        // Get unique dates with symptoms
        const uniqueDates = new Set<string>()
        symptomLogs.forEach((log) => {
            if (log.severity !== "none") {
                uniqueDates.add(log.date)
            }
        })

        // Convert to Date objects
        const dates = Array.from(uniqueDates).map((dateStr) => new Date(dateStr))

        setDatesWithSymptoms(dates)

    }, [symptomLogs])

    // Memoized function to fetch dates with symptoms
    const fetchDatesWithSymptoms = useCallback(async () => {
        try {
            // Get all symptom logs to determine which dates have symptoms
            const allDates = await getDatesWithSymptoms()
            console.log("Dates with symptoms:", allDates)

            // Convert string dates to Date objects
            const dateObjects = allDates.map((dateStr) => new Date(dateStr))
            setDatesWithSymptoms(dateObjects)
        } catch (error) {
            console.error("Error fetching dates with symptoms:", error)
        }
    }, [getDatesWithSymptoms])

    useEffect(() => {
        if (trackedSupplements.length === 0) return;

        const calculateStreak = async () => {
            // Fetch all logs for the past 30 days at once instead of one by one
            const today = new Date();
            const dates = Array.from({ length: 30 }, (_, i) => {
                const date = subDays(today, i);
                return format(date, "yyyy-MM-dd");
            });

            // Create a map of date -> logs
            const logsMap: Record<string, IntakeLog[]> = {};
            for (const date of dates) {
                logsMap[date] = await getIntakeLogsForDate(date);
            }

            // Calculate streak
            let currentStreak = 0;
            for (let i = 1; i < dates.length; i++) { // Start from yesterday (index 1)
                const dateStr = dates[i];
                const logs = logsMap[dateStr];

                // Check if all supplements were taken on this day
                const allSupplementsTaken = trackedSupplements.every((supplement) => {
                    return logs.some((log) => log.tracked_supplement_id === supplement.id);
                });

                if (allSupplementsTaken) {
                    currentStreak++;
                } else {
                    break;
                }
            }

            setStreak(currentStreak);

            // Calculate days to next achievement
            const nextAchievement = 10;
            setDaysToNextAchievement(Math.max(0, nextAchievement - currentStreak));

            // Calculate improvement (mock data for now)
            setImprovement(15);

            // Generate progress chart data
            generateProgressData(logsMap, dates);
        };

        calculateStreak();
    }, [trackedSupplements]); // Remove getIntakeLogsForDate from dependencies

    // Generate data for the progress chart
    const generateProgressData = (logsMap: Record<string, IntakeLog[]>, dates: string[]) => {
        const chartData = [];

        // Process the last 14 days for the chart
        const recentDates = dates.slice(0, 14).reverse();

        for (const dateStr of recentDates) {
            const logs = logsMap[dateStr];
            const totalSupplements = trackedSupplements.length;
            const takenSupplements = trackedSupplements.filter(supplement =>
                logs.some(log => log.tracked_supplement_id === supplement.id)
            ).length;

            const consistency = totalSupplements > 0
                ? Math.round((takenSupplements / totalSupplements) * 100)
                : 0;

            chartData.push({
                date: formatLocalDate(dateStr),
                consistency: consistency,
                taken: takenSupplements,
                total: totalSupplements
            });
        }

        setProgressData(chartData);
    };

    // Handle supplement intake logging
    const handleLogIntake = async (supplement: TrackedSupplement, dayIndex: number) => {
        const date = addDays(weekStartDate, dayIndex)
        const dateStr = format(date, "yyyy-MM-dd")

        // Check if already logged
        const logs = await getIntakeLogsForDate(dateStr)
        const existingLog = logs.find((log: IntakeLog) => log.tracked_supplement_id === supplement.id)

        try {
            // Toggle the taken status - if exists, delete it; if not, create it
            if (existingLog) {
                // If log exists, delete it
                await deleteIntakeLog(existingLog.id)
            } else {
                // If log doesn't exist, create it
                // Using the supplement's dosage as dosage_taken
                const dosage = parseFloat(supplement.dosage) || 1
                await logIntake(supplement.id, dateStr, dosage, supplement.unit || "pill", "")
            }

            // Reload supplement status after logging
            await loadSupplementStatus()
        } catch (error) {
            console.error("Error logging intake:", error)
        }
    }

    // Load supplement status
    const loadSupplementStatus = async () => {
        // Get dates for the week
        const dates = Array.from({ length: 7 }, (_, i) => {
            const date = addDays(weekStartDate, i);
            return format(date, "yyyy-MM-dd");
        });

        // Fetch logs for all dates at once to populate cache
        const logsPromises = dates.map(date => getIntakeLogsForDate(date));
        await Promise.all(logsPromises);

        // Now build the status map (this will use cached results)
        const supplementStatusMap: Record<string, Record<number, boolean>> = {};

        for (const supplement of trackedSupplements) {
            supplementStatusMap[supplement.id] = {};

            for (let i = 0; i < 7; i++) {
                const date = addDays(weekStartDate, i);
                const dateStr = format(date, "yyyy-MM-dd");
                const logs = await getIntakeLogsForDate(dateStr); // Will use cache
                supplementStatusMap[supplement.id][i] = logs.some(log => log.tracked_supplement_id === supplement.id);
            }
        }

        setSupplementsTaken(supplementStatusMap);
    };

    // Effect for initial loading and whenever weekStartDate or trackedSupplements change
    useEffect(() => {
        if (trackedSupplements.length > 0) {
            loadSupplementStatus();
        }
        fetchDatesWithSymptoms();
    }, [fetchDatesWithSymptoms, trackedSupplements, weekStartDate]);

    // Handle logging intake with state update
    const handleLogIntakeWithState = useCallback(
        async (supplement: TrackedSupplement, dayIndex: number) => {
            const date = addDays(weekStartDate, dayIndex);
            const dateStr = format(date, 'yyyy-MM-dd');

            const logs = await getIntakeLogsForDate(dateStr);
            const existingLog = logs.find(
                (log) => log.tracked_supplement_id === supplement.id
            );

            if (existingLog) {
                await deleteIntakeLog(existingLog.id);
            } else {
                const dosage = parseFloat(supplement.dosage) || 1;
                await logIntake(
                    supplement.id,
                    dateStr,
                    dosage,
                    supplement.unit || 'pill',
                    ''
                );
            }

            setSupplementsTaken((prev) => ({
                ...prev,
                [supplement.id]: {
                    ...prev[supplement.id],
                    [dayIndex]: !prev[supplement.id]?.[dayIndex],
                },
            }));
        },
        [weekStartDate, getIntakeLogsForDate, deleteIntakeLog, logIntake]
    );

    // Add a function to handle exporting progress as PDF
    const handleExportProgress = async () => {
        try {
            // Check if there's data to export
            if (trackedSupplements.length === 0) {
                toast({
                    title: "No data to export",
                    description: "Start tracking supplements to generate a progress report.",
                    variant: "destructive"
                });
                return;
            }

            // Prepare data for report
            const reportData = {
                userName: user?.name || "User",
                trackedSupplements,
                intakeLogs,
                symptomLogs,
                streak,
                improvement,
                progressData,
                generatedDate: new Date().toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })
            };

            // Show loading toast
            toast({
                title: "Generating report",
                description: "Please wait while we generate your progress report...",
            });

            // Generate PDF report
            await generateProgressReport(reportData);

            // Show success toast
            toast({
                title: "Report generated",
                description: "Your progress report has been downloaded.",
                variant: "default",
            });
        } catch (error) {
            console.error("Error generating report:", error);
            toast({
                title: "Error generating report",
                description: "Please try again later.",
                variant: "destructive"
            });
        }
    };

    // Function to validate if a date is in the future
    const isFutureDate = (date: Date): boolean => {
        const today = new Date(getTodayLocalDate())
        return date > today
    }

    return (
        <div className="space-y-6 px-4 sm:px-6 py-4">
            <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-golden">Dashboard</h1>

            <div className="grid gap-6 sm:grid-cols-1 md:grid-cols-3">
                {/* Daily Supplement Log */}
                <Card className="border-golden">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 pt-2 bg-golden-light rounded-t-lg">
                        <CardTitle className="text-sm sm:text-base md:text-lg text-golden">Daily Supplement Log</CardTitle>
                        <Button variant="outline" size="sm" asChild className="btn-full-tracker">
                            <Link href="/dashboard/tracker/log" className="text-xs flex items-center">
                                <Activity className="mr-1 h-3 w-3 sm:h-4 sm:w-4" />
                                <span className="hidden sm:inline">Full Tracker</span>
                                <span className="sm:hidden">Full</span>
                            </Link>
                        </Button>
                    </CardHeader>
                    <CardContent className="pt-4">
                        {trackedSupplements.length > 0 ? (
                            <div className="space-y-6">
                                {trackedSupplements.map((supplement) => (
                                    <div key={supplement.id} className="space-y-2">
                                        <h3 className="font-medium">{supplement.supplementName}</h3>
                                        <div className="flex justify-between">
                                            {weekdays.map((day, index) => {
                                                const logDate = addDays(weekStartDate, index)
                                                const isFutureDate = isAfter(logDate, parseISO(getTodayLocalDate())) // Compare to local today

                                                return (
                                                    <div key={index} className="flex flex-col items-center">
                                                        <button
                                                            onClick={() => {
                                                                if (!isFutureDate) {
                                                                    handleLogIntakeWithState(supplement, index)
                                                                }
                                                            }}
                                                            disabled={isFutureDate}
                                                            className={`w-8 h-8 rounded-full border-2 flex items-center justify-center transition-colors 
                    ${isFutureDate
                                                                    ? 'bg-white-600 border-gray-300 text-gray-400 cursor-not-allowed'
                                                                    : supplementsTaken[supplement.id]?.[index]
                                                                        ? 'bg-yellow-500 border-yellow-600 text-white'
                                                                        : 'bg-background border-gray-300 hover:border-gray-400'
                                                                }`}
                                                            aria-label={
                                                                isFutureDate
                                                                    ? `Cannot log for ${format(logDate, 'EEEE')} (future date)`
                                                                    : `${supplementsTaken[supplement.id]?.[index]
                                                                        ? 'Taken'
                                                                        : 'Not taken'
                                                                    } on ${format(logDate, 'EEEE')}`
                                                            }
                                                        >
                                                            {supplementsTaken[supplement.id]?.[index] && !isFutureDate ? '✓' : ''}
                                                        </button>
                                                        <span className="text-xs mt-1">{day}</span>
                                                    </div>
                                                )
                                            })}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-6">
                                <p className="text-muted-foreground">No supplements being tracked.</p>
                                <Button className="mt-2 btn-yellow" asChild>
                                    <Link href="/dashboard/tracker/add">Add a supplement</Link>
                                </Button>
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Daily Symptom Log Card */}
                <Card className="border-golden">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 pt-2 bg-golden-light rounded-t-lg">
                        <CardTitle className="text-sm sm:text-base md:text-lg text-golden">Daily Symptom Log</CardTitle>
                        <Button variant="outline" size="sm" asChild className="btn-full-tracker">
                            <Link href="/dashboard/symptoms" className="text-xs flex items-center">
                                <Activity className="mr-1 h-3 w-3 sm:h-4 sm:w-4" />
                                <span className="hidden sm:inline">Full Tracker</span>
                                <span className="sm:hidden">Full</span>
                            </Link>
                        </Button>
                    </CardHeader>
                    <CardContent>
                        <div className="flex flex-col items-center">
                            <Calendar
                                mode="single"
                                selected={selectedDate}
                                onSelect={(date) => date && setSelectedDate(date)}
                                className="rounded-md border mx-auto mb-4 w-full max-w-[300px]"
                                modifiers={{
                                    withSymptoms: datesWithSymptoms,
                                }}
                                modifiersClassNames={{
                                    withSymptoms: "has-symptoms",
                                }}
                            />

                            <style jsx global>{`
                .has-symptoms::after {
                  content: "";
                  position: absolute;
                  bottom: 4px;
                  width: 5px;
                  height: 5px;
                  border-radius: 50%;
                  background-color: #ef4444;
                }
                
              `}</style>

                            <p className="text-center mb-4">
                                Selected date: <strong>{formattedDate}</strong>
                            </p>

                            <div className="flex items-center justify-center gap-4">
                                <Dialog open={symptomsDialogOpen} onOpenChange={setSymptomsDialogOpen}>
                                    <DialogTrigger asChild>
                                        <Button className="flex items-center gap-2 btn-yellow"
                                            disabled={dateString > getTodayLocalDate()}
                                        >
                                            <Activity className="h-4 w-4" />
                                            Log Symptoms
                                        </Button>
                                    </DialogTrigger>
                                    <DialogContent className="sm:max-w-[500px]">
                                        <DialogHeader>
                                            <DialogTitle>Log Symptoms for {formattedDate}</DialogTitle>
                                        </DialogHeader>
                                        <CategorySymptomLogger date={dateString} onComplete={() => setSymptomsDialogOpen(false)} />
                                    </DialogContent>
                                </Dialog>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Quick Actions */}
                <Card className="border-golden">
                    <CardHeader className="bg-golden-light pt-2 pb-2 rounded-t-lg">
                        <CardTitle className="text-sm sm:text-base md:text-lg text-golden">Quick Actions</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3 pt-4">
                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-1 gap-3">
                            <Button asChild className="w-full justify-start btn-yellow text-sm">
                                <Link href="/dashboard/tracker">
                                    <Pill className="mr-2 h-4 w-4" />
                                    <span className="truncate">View Tracked Supplements</span>
                                </Link>
                            </Button>
                            <Button asChild className="w-full justify-start btn-yellow text-sm">
                                <Link href="/dashboard/tracker/add">
                                    <Pill className="mr-2 h-4 w-4" />
                                    <span className="truncate">Add New Supplement</span>
                                </Link>
                            </Button>
                            <Button asChild className="w-full justify-start btn-yellow text-sm">
                                <Link href="/dashboard/symptoms">
                                    <Activity className="mr-2 h-4 w-4" />
                                    <span className="truncate">Symptom Tracker</span>
                                </Link>
                            </Button>
                            <Button asChild className="w-full justify-start btn-yellow text-sm">
                                <Link href="/">
                                    <Search className="mr-2 h-4 w-4" />
                                    <span className="truncate">Search Supplements</span>
                                </Link>
                            </Button>
                            <Button
                                className="w-full justify-start btn-yellow text-sm"
                                onClick={(e) => {
                                    e.preventDefault();
                                    handleExportProgress();
                                }}
                            >
                                <FileDown className="mr-2 h-4 w-4" />
                                <span className="truncate">Export Progress</span>
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Progress Insights */}
            <Card className="bg-golden border-golden">
                <CardContent className="pt-6">
                    <div className="flex items-center gap-2 mb-6">
                        <TrendingUp className="h-5 w-5 md:h-6 md:w-6 text-yellow-500" />
                        <h2 className="text-lg md:text-xl font-bold text-yellow-800">Progress Insights</h2>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="md:col-span-2">
                            <h3 className="text-base md:text-lg font-semibold mb-4 text-yellow-800">Consistency Over Time</h3>
                            <div className="h-[250px] md:h-64 w-full">
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart
                                        data={progressData}
                                        margin={{ top: 5, right: 5, left: 0, bottom: 5 }}
                                    >
                                        <CartesianGrid strokeDasharray="3 3" className="chart-grid" />
                                        <XAxis
                                            dataKey="date"
                                            className="chart-axis"
                                            tick={{ fontSize: 10 }}
                                            interval="preserveStartEnd"
                                        />
                                        <YAxis
                                            className="chart-axis"
                                            domain={[0, 100]}
                                            tick={{ fontSize: 10 }}
                                            width={30}
                                            label={{
                                                value: 'Consistency %',
                                                angle: -90,
                                                position: 'insideLeft',
                                                style: { fill: '#000000', fontWeight: 'bold', fontSize: '0.8rem' }
                                            }}
                                        />
                                        <Tooltip
                                            contentStyle={{
                                                backgroundColor: '#ffffff',
                                                borderColor: '#000000',
                                                color: '#000000',
                                                fontWeight: 'bold'
                                            }}
                                            labelStyle={{ color: '#000000' }}
                                        />
                                        <Legend />
                                        <Line
                                            type="monotone"
                                            dataKey="consistency"
                                            name="Consistency %"
                                            className="chart-line"
                                            strokeWidth={3}
                                            activeDot={{ r: 8, className: "chart-point" }}
                                        />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        <div className="space-y-4">
                            <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                                <div className="flex items-center gap-2 mb-2">
                                    <Award className="h-4 w-4 md:h-5 md:w-5 text-yellow-600" />
                                    <h3 className="text-sm md:text-base font-semibold text-yellow-800 truncate">Weekly Improvement</h3>
                                </div>
                                <p className="text-base md:text-lg font-bold text-yellow-600">+{improvement}%</p>
                                <p className="text-xs md:text-sm text-yellow-700">from last week</p>
                            </div>

                            <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                                <div className="flex items-center gap-2 mb-2">
                                    <TrendingUp className="h-4 w-4 md:h-5 md:w-5 text-yellow-600" />
                                    <h3 className="text-sm md:text-base font-semibold text-yellow-800">Current Streak</h3>
                                </div>
                                <p className="text-base md:text-lg font-bold text-yellow-600">{streak} days</p>
                                {daysToNextAchievement > 0 &&
                                    <p className="text-xs md:text-sm text-yellow-700">
                                        {daysToNextAchievement} days until next achievement
                                    </p>
                                }
                            </div>

                            <div className="mt-4">
                                <Button className="w-full btn-yellow" asChild>
                                    <Link href="/dashboard/tracker">
                                        View Detailed Progress
                                    </Link>
                                </Button>
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}