"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import { useAuth } from "./auth-context"
import type { Supplement } from "@/lib/types"
import { getSupplementById } from "@/lib/supplements"
import { toast } from "@/components/ui/use-toast"
import { handleError } from "@/lib/error-handler"

export type TrackedSupplement = {
  id: string
  userId: string
  supplementId: string
  supplement: Supplement
  startDate: string
  endDate?: string
  dosage: string
  frequency: string
  notes?: string
}

export type IntakeLog = {
  id: string
  userId: string
  trackedSupplementId: string
  timestamp: string
  taken: boolean
  notes?: string
}

// Add these new types for symptom tracking
export type Symptom = {
  id: string
  name: string
  icon?: string
  category?: string
}

export type SymptomLog = {
  id: string
  userId: string
  date: string
  symptomId: string
  severity: "none" | "mild" | "average" | "severe"
  notes?: string
}

type TrackerContextType = {
  trackedSupplements: TrackedSupplement[]
  intakeLogs: IntakeLog[]
  addTrackedSupplement: (
    data: Omit<TrackedSupplement, "id" | "userId" | "supplement">,
  ) => Promise<{ success: boolean; warnings: string[] }>
  removeTrackedSupplement: (id: string) => void
  logIntake: (trackedSupplementId: string, taken: boolean, date?: string, notes?: string) => void
  getIntakeLogsForDate: (date: string) => IntakeLog[]
  checkInteractions: (supplementId: string) => Promise<string[]>
  symptoms: Symptom[]
  symptomLogs: SymptomLog[]
  logSymptom: (
    symptomId: string,
    date: string,
    severity: "none" | "mild" | "average" | "severe",
    notes?: string,
  ) => void
  getSymptomLogsForDate: (date: string) => SymptomLog[]
}

const TrackerContext = createContext<TrackerContextType | undefined>(undefined)

export function TrackerProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth()
  const [trackedSupplements, setTrackedSupplements] = useState<TrackedSupplement[]>([])
  const [intakeLogs, setIntakeLogs] = useState<IntakeLog[]>([])

  // Updated symptom list to match our new categories
  const [symptoms, setSymptoms] = useState<Symptom[]>([
    // General symptoms
    { id: "fine", name: "Everything is fine", category: "general" },
    { id: "acne", name: "Skin issues", category: "general" },
    { id: "fatigue", name: "Fatigue", category: "general" },
    { id: "headache", name: "Headache", category: "general" },
    { id: "abdominal-pain", name: "Abdominal Pain", category: "general" },
    { id: "dizziness", name: "Dizziness", category: "general" },

    //Appetite
    { id: "low", name: "Low", category: "appetite" },    
    { id: "normal", name: "Normal", category: "appetite" },    
    { id: "high", name: "High", category: "appetite" },    

    // Mood symptoms
    { id: "calm", name: "Calm", category: "mood" },
    { id: "mood-swings", name: "Mood swings", category: "mood" },
    { id: "happy", name: "Happy", category: "mood" },
    { id: "energetic", name: "Energetic", category: "mood" },
    { id: "irritated", name: "Irritated", category: "mood" },
    { id: "depressed", name: "Depressed", category: "mood" },
    { id: "low-energy", name: "Low energy", category: "mood" },
    { id: "anxious", name: "Anxious", category: "mood" },

    // Sleep symptoms
    { id: "insomnia", name: "Insomnia", category: "sleep" },
    { id: "good-sleep", name: "Good sleep", category: "sleep" },
    { id: "restless", name: "Restless", category: "sleep" },
    { id: "tired", name: "Tired", category: "sleep" },

    // Digestive symptoms
    { id: "bloating", name: "Bloating", category: "digestive" },
    { id: "nausea", name: "Nausea", category: "digestive" },
    { id: "constipation", name: "Constipation", category: "digestive" },
    { id: "diarrhea", name: "Diarrhea", category: "digestive" },

    // Physical activity
    { id: "no-activity", name: "Didn't exercise", category: "activity" },
    { id: "yoga", name: "Yoga", category: "activity" },
    { id: "gym", name: "Gym", category: "activity" },
    { id: "swimming", name: "Swimming", category: "activity" },
    { id: "running", name: "Running", category: "activity" },
    { id: "cycling", name: "Cycling", category: "activity" },
    { id: "team-sports", name: "Team Sports", category: "activity" },
    { id: "dancing", name: "Aerobics/Dancing", category: "activity" },
  ])
  const [symptomLogs, setSymptomLogs] = useState<SymptomLog[]>([])

  // Load tracked supplements and intake logs from localStorage on initial render
  useEffect(() => {
    if (user) {
      const storedSupplements = localStorage.getItem("trackedSupplements")
      if (storedSupplements) {
        setTrackedSupplements(JSON.parse(storedSupplements))
      }

      const storedLogs = localStorage.getItem("intakeLogs")
      if (storedLogs) {
        setIntakeLogs(JSON.parse(storedLogs))
      }
      // Add this to the useEffect that loads data from localStorage
      const storedSymptomLogs = localStorage.getItem("symptomLogs")
      if (storedSymptomLogs) {
        setSymptomLogs(JSON.parse(storedSymptomLogs))
      }
    } else {
      setTrackedSupplements([])
      setIntakeLogs([])
      setSymptomLogs([])
    }
  }, [user])

  // Save tracked supplements to localStorage whenever they change
  useEffect(() => {
    if (user && trackedSupplements.length > 0) {
      localStorage.setItem("trackedSupplements", JSON.stringify(trackedSupplements))
    }
  }, [trackedSupplements, user])

  // Save intake logs to localStorage whenever they change
  useEffect(() => {
    if (user && intakeLogs.length > 0) {
      localStorage.setItem("intakeLogs", JSON.stringify(intakeLogs))
    }
    // Add this to the useEffect that saves data to localStorage
    if (user && symptomLogs.length > 0) {
      localStorage.setItem("symptomLogs", JSON.stringify(symptomLogs))
    }
  }, [intakeLogs, user, symptomLogs])

  // Update addTrackedSupplement to use toast for success and error notifications
  const addTrackedSupplement = async (data: Omit<TrackedSupplement, "id" | "userId" | "supplement">) => {
    if (!user) {
      toast.error("You must be logged in to track supplements");
      return { success: false, warnings: [] };
    }

    try {
      // Check for interactions
      const warnings = await checkInteractions(data.supplementId);
      
      // Show warnings as toast if there are any
      if (warnings.length > 0) {
        toast.warning(`Potential interactions detected: ${warnings.length} warning(s)`, {
          action: {
            label: "View",
            onClick: () => window.scrollTo(0, 0), // Scroll to top where the warnings are displayed
          }
        });
      }

      // Get the supplement details
      const supplement = await getSupplementById(data.supplementId);
      if (!supplement) {
        toast.error("Supplement not found");
        return { success: false, warnings };
      }

      const newTrackedSupplement: TrackedSupplement = {
        id: `ts-${Date.now()}`,
        userId: user.id,
        supplementId: data.supplementId,
        supplement,
        startDate: data.startDate,
        endDate: data.endDate,
        dosage: data.dosage,
        frequency: data.frequency,
        notes: data.notes,
      };

      setTrackedSupplements((prev) => [...prev, newTrackedSupplement]);
      return { success: true, warnings };
    } catch (error) {
      handleError(error, {
        defaultMessage: "Failed to add supplement"
      });
      return { success: false, warnings: [] };
    }
  };

  // Update removeTrackedSupplement to use toast
  const removeTrackedSupplement = (id: string) => {
    try {
      setTrackedSupplements((prev) => prev.filter((item) => item.id !== id));
      // Also remove any intake logs for this supplement
      setIntakeLogs((prev) => prev.filter((log) => log.trackedSupplementId !== id));
      toast.success("Supplement removed from tracking");
    } catch (error) {
      handleError(error, {
        defaultMessage: "Failed to remove supplement"
      });
    }
  };

  // Update logIntake to use toast
  const logIntake = (trackedSupplementId: string, taken: boolean, date?: string, notes?: string) => {
    if (!user) {
      toast.error("You must be logged in to log supplement intake");
      return;
    }

    try {
      const timestamp = date ? new Date(`${date}T12:00:00`).toISOString() : new Date().toISOString();
      
      // Find the supplement name for the success message
      const supplement = trackedSupplements.find(s => s.id === trackedSupplementId);
      const supplementName = supplement ? supplement.supplement.name : "Supplement";

      // Check if there's already a log for this supplement on this date
      const existingLogIndex = intakeLogs.findIndex((log) => {
        const logDate = new Date(log.timestamp).toISOString().split("T")[0];
        const targetDate = new Date(timestamp).toISOString().split("T")[0];
        return log.trackedSupplementId === trackedSupplementId && logDate === targetDate;
      });

      if (existingLogIndex >= 0) {
        // Update existing log
        const updatedLogs = [...intakeLogs];
        updatedLogs[existingLogIndex] = {
          ...updatedLogs[existingLogIndex],
          taken,
          notes,
          timestamp, // Update timestamp to ensure it's consistent
        };
        setIntakeLogs(updatedLogs);
        
        toast.success(`Updated log for ${supplementName}`);
      } else {
        // Create new log
        const newLog: IntakeLog = {
          id: `log-${Date.now()}`,
          userId: user.id,
          trackedSupplementId,
          timestamp,
          taken,
          notes,
        };

        setIntakeLogs((prev) => [...prev, newLog]);
        
        toast.success(`${taken ? "Logged" : "Skipped"} ${supplementName}`);
      }
    } catch (error) {
      handleError(error, {
        defaultMessage: "Failed to log supplement intake"
      });
    }
  };

  // Get intake logs for a specific date
  const getIntakeLogsForDate = (date: string) => {
    const startDate = new Date(date)
    startDate.setHours(0, 0, 0, 0)

    const endDate = new Date(date)
    endDate.setHours(23, 59, 59, 999)

    return intakeLogs.filter((log) => {
      const logDate = new Date(log.timestamp)
      return logDate >= startDate && logDate <= endDate
    })
  }

  // Check for interactions with existing supplements
  const checkInteractions = async (supplementId: string) => {
    if (!user) return [];
    if (!supplementId) return [];

    try {
      // Show loading toast for interactions check
      const loadingToast = toast.info("Checking for interactions...", { 
        duration: 3000 
      });

      // If there are no tracked supplements, return empty array early
      if (trackedSupplements.length === 0) {
        toast.dismiss(loadingToast.id);
        return [];
      }

      const newSupplement = await getSupplementById(supplementId);
      if (!newSupplement) {
        toast.dismiss(loadingToast.id);
        toast.error("Could not find supplement information");
        return [];
      }

      const warnings: string[] = [];

      // Check each tracked supplement for interactions with the new one
      for (const tracked of trackedSupplements) {
        // Skip if it's the same supplement
        if (tracked.supplementId === supplementId) continue;

        // Check for interactions in the supplement data
        const interactions = tracked.supplement.supplementInteractions?.filter(
          (interaction) => interaction.supplementName === newSupplement.name,
        ) || [];

        // Add warnings for each interaction
        interactions.forEach((interaction) => {
          const severityText = 
            interaction.severity === "high"
              ? "This is a serious interaction."
              : interaction.severity === "medium"
                ? "Use caution when combining these supplements."
                : "This is a mild interaction.";
                
          warnings.push(
            `${tracked.supplement.name} + ${newSupplement.name}: ${interaction.effect}. ${severityText} ${interaction.recommendation || ""}`
          );
        });
      }

      // Dismiss loading toast
      toast.dismiss(loadingToast.id);

      // If interactions are found, show a warning toast
      if (warnings.length > 0) {
        toast.warning(`Found ${warnings.length} potential interaction${warnings.length > 1 ? 's' : ''}`, {
          action: {
            label: "View Details",
            onClick: () => {
              // Show a more detailed alert about interactions (could be improved with a modal in future)
              alert(`Potential Interactions:\n\n${warnings.join('\n\n')}`);
            }
          }
        });
      }

      return warnings;
    } catch (error) {
      handleError(error, {
        defaultMessage: "Error checking for interactions"
      });
      return [];
    }
  };

  // Update logSymptom to use toast
  const logSymptom = (
    symptomId: string,
    date: string,
    severity: "none" | "mild" | "average" | "severe",
    notes?: string,
  ) => {
    if (!user) {
      toast.error("You must be logged in to log symptoms");
      return;
    }
    
    try {
      // Find the symptom name for the toast
      const symptom = symptoms.find(s => s.id === symptomId);
      const symptomName = symptom ? symptom.name : "Symptom";

      // Check if there's already a log for this symptom on this date
      const existingLogIndex = symptomLogs.findIndex((log) => {
        return log.symptomId === symptomId && log.date === date;
      });

      if (existingLogIndex >= 0) {
        // Update existing log
        const updatedLogs = [...symptomLogs];
        updatedLogs[existingLogIndex] = {
          ...updatedLogs[existingLogIndex],
          severity,
          notes,
        };
        setSymptomLogs(updatedLogs);
        
        toast.success(`Updated log for ${symptomName}`);
      } else {
        // Create new log
        const newLog: SymptomLog = {
          id: `symptom-${Date.now()}`,
          userId: user.id,
          symptomId,
          date,
          severity,
          notes,
        };

        setSymptomLogs((prev) => [...prev, newLog]);
        
        toast.success(`Logged ${symptomName} as ${severity}`);
      }
    } catch (error) {
      handleError(error, {
        defaultMessage: "Failed to log symptom"
      });
    }
  };

  // Add this function to get symptom logs for a specific date
  const getSymptomLogsForDate = (date: string) => {
    return symptomLogs.filter((log) => log.date === date && log.userId === user?.id)
  }

  return (
    <TrackerContext.Provider
      value={{
        trackedSupplements,
        intakeLogs,
        addTrackedSupplement,
        removeTrackedSupplement,
        logIntake,
        getIntakeLogsForDate,
        checkInteractions,
        symptoms,
        symptomLogs,
        logSymptom,
        getSymptomLogsForDate,
      }}
    >
      {children}
    </TrackerContext.Provider>
  )
}

export function useTracker() {
  const context = useContext(TrackerContext)
  if (context === undefined) {
    throw new Error("useTracker must be used within a TrackerProvider")
  }
  return context
}

