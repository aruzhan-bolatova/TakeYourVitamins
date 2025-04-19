"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import { useAuth } from "./auth-context"
import type { Supplement } from "@/lib/types"
import { getSupplementById } from "@/lib/supplements"
import { useNotification } from "@/contexts/notification-context"
import { handleError } from "@/lib/error-handler"
import { tryCatch } from "@/lib/error-handling"

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
  const notification = useNotification()
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

  // Update addTrackedSupplement to use notification for success and error notifications
  const addTrackedSupplement = async (data: Omit<TrackedSupplement, "id" | "userId" | "supplement">) => {
    if (!user) {
      notification.notifyError("You must be logged in to track supplements");
      return { success: false, warnings: [] };
    }

    try {
      // Check for interactions
      const warnings = await checkInteractions(data.supplementId);
      
      // Show warnings as notification if there are any
      if (warnings.length > 0) {
        notification.notifyWarning(`Potential interactions detected: ${warnings.length} warning(s)`);
      }

      // Get the supplement details
      const [supplement, error] = await tryCatch(async () => getSupplementById(data.supplementId));
      
      if (error || !supplement) {
        notification.notifyError("Supplement not found");
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
      notification.notifySuccess("Supplement added to tracking successfully");
      return { success: true, warnings };
    } catch (error) {
      notification.handleApiError(error, "Failed to add supplement");
      return { success: false, warnings: [] };
    }
  };

  // Update removeTrackedSupplement to use notification
  const removeTrackedSupplement = (id: string) => {
    try {
      setTrackedSupplements((prev) => prev.filter((item) => item.id !== id));
      // Also remove any intake logs for this supplement
      setIntakeLogs((prev) => prev.filter((log) => log.trackedSupplementId !== id));
      notification.notifySuccess("Supplement removed from tracking");
    } catch (error) {
      notification.handleApiError(error, "Failed to remove supplement");
    }
  };

  // Update logIntake to use notification
  const logIntake = (trackedSupplementId: string, taken: boolean, date?: string, notes?: string) => {
    if (!user) {
      notification.notifyError("You must be logged in to log supplement intake");
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

      // If there's already a log, update it
      if (existingLogIndex !== -1) {
        // Create a new array with the updated log
        const updatedLogs = [...intakeLogs];
        updatedLogs[existingLogIndex] = {
          ...updatedLogs[existingLogIndex],
          taken: taken,
          notes: notes || updatedLogs[existingLogIndex].notes,
        };
        setIntakeLogs(updatedLogs);
      } else {
        // Otherwise, create a new log
        const newLog: IntakeLog = {
          id: `il-${Date.now()}`,
          userId: user.id,
          trackedSupplementId,
          timestamp,
          taken,
          notes,
        };
        setIntakeLogs((prev) => [...prev, newLog]);
      }

      // Only show notifications on explicit take/skip actions (not initial state)
      if (taken) {
        notification.notifySuccess(`${supplementName} marked as taken`);
      }
    } catch (error) {
      notification.handleApiError(error, "Failed to log supplement intake");
    }
  };

  // Function to get intake logs for a specific date
  const getIntakeLogsForDate = (date: string) => {
    return intakeLogs.filter((log) => {
      const logDate = new Date(log.timestamp).toISOString().split("T")[0];
      return logDate === date;
    });
  };

  // Function to check for interactions between supplements
  const checkInteractions = async (supplementId: string) => {
    if (!supplementId || !user) {
      return [];
    }

    try {
      // Create a list of currently tracked supplements
      const currentlyTakingIds = trackedSupplements.map((item) => item.supplementId);
      
      // If we're not adding a new supplement, return no warnings
      if (currentlyTakingIds.includes(supplementId)) {
        return [];
      }
      
      // Get the supplement details
      const [newSupplement, error] = await tryCatch(async () => getSupplementById(supplementId));
      
      if (error || !newSupplement) {
        notification.notifyError("Failed to check interactions: Supplement not found");
        return [];
      }
      
      // Check against each existing supplement
      const warnings: string[] = [];
      
      for (const currentId of currentlyTakingIds) {
        // Get the current supplement
        const [currentSupplement, currentError] = await tryCatch(async () => getSupplementById(currentId));
        
        if (currentError || !currentSupplement) continue;

        // For this example, we'll just compare categories
        // In a real app, you would have a more sophisticated interaction checker
        if (
          currentSupplement.category === newSupplement.category &&
          currentSupplement.name !== newSupplement.name
        ) {
          warnings.push(
            `You are already taking ${currentSupplement.name} which is in the same category (${currentSupplement.category}) as ${newSupplement.name}. Consider consulting with a healthcare provider.`
          );
        }
        
        // Check for known bad interactions (simplified example)
        const badInteractions: Record<string, string[]> = {
          "vitamin-k": ["warfarin", "blood-thinner"],
          "st-johns-wort": ["ssri", "antidepressant", "birth-control"],
          "iron": ["calcium", "zinc", "magnesium"],
        };
        
        // Use ID or name as keys for checking interactions
        const newKey = newSupplement.supplementId.toLowerCase();
        const currentKey = currentSupplement.supplementId.toLowerCase();
        
        // Check both directions of potential interactions
        if (badInteractions[newKey]?.includes(currentKey)) {
          warnings.push(
            `${newSupplement.name} may interact with ${currentSupplement.name}. This combination can be potentially dangerous. Please consult with a healthcare provider.`
          );
        } else if (badInteractions[currentKey]?.includes(newKey)) {
          warnings.push(
            `${currentSupplement.name} may interact with ${newSupplement.name}. This combination can be potentially dangerous. Please consult with a healthcare provider.`
          );
        }
      }
      
      return warnings;
    } catch (error) {
      notification.handleApiError(error, "Failed to check interactions");
      return [];
    }
  };

  // Function to log symptoms
  const logSymptom = (
    symptomId: string,
    date: string,
    severity: "none" | "mild" | "average" | "severe",
    notes?: string,
  ) => {
    if (!user) {
      notification.notifyError("You must be logged in to log symptoms");
      return;
    }

    try {
      // Check if there's already a log for this symptom on this date
      const existingLogIndex = symptomLogs.findIndex(
        (log) => log.userId === user.id && log.symptomId === symptomId && log.date === date
      );

      // Get the symptom name for notifications
      const symptom = symptoms.find(s => s.id === symptomId);
      const symptomName = symptom ? symptom.name : "Symptom";

      // If there's already a log, update it
      if (existingLogIndex !== -1) {
        // Create a new array with the updated log
        const updatedLogs = [...symptomLogs];
        updatedLogs[existingLogIndex] = {
          ...updatedLogs[existingLogIndex],
          severity,
          // Only update notes if they're provided
          ...(notes !== undefined && { notes }),
        };
        setSymptomLogs(updatedLogs);
      } else {
        // Otherwise, create a new log
        const newLog: SymptomLog = {
          id: `sl-${Date.now()}-${symptomId}`,
          userId: user.id,
          date,
          symptomId,
          severity,
          notes,
        };
        setSymptomLogs((prev) => [...prev, newLog]);
      }

      // Only notify for significant changes (not for automatic updates or "none" severity)
      if (severity !== "none") {
        notification.notifySuccess(`Symptom logged: ${symptomName}`);
      }
    } catch (error) {
      notification.handleApiError(error, "Failed to log symptom");
    }
  };

  // Function to get symptom logs for a specific date
  const getSymptomLogsForDate = (date: string) => {
    if (!user) return [];
    
    return symptomLogs.filter((log) => {
      return log.userId === user.id && log.date === date;
    });
  };

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

