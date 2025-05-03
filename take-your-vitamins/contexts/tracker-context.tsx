"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import { useAuth } from "./auth-context"
import type { Supplement } from "@/lib/types"
import { getSupplementById } from "@/lib/supplements"

export type TrackedSupplement = {
  id: string
  supplementId: string
  supplementName: string
  dosage: string
  unit: string
  frequency: string
  startDate: string
  endDate?: string
  notes?: string
}

// Implement IntakeLog type based on the backend response
export type IntakeLog = {
  id: string
  tracked_supplement_id: string
  supplement_name: string
  intake_date: string
  intake_time: string
  dosage_taken: number
  unit: string
  notes?: string
  created_at: string
  updated_at: string
}

// Mock symptom tracking types
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
  symptomName: string
  severity: "none" | "mild" | "average" | "severe"
  notes?: string
  created_at: string
}

// Define interaction type for clarity
type Interaction = {
  supplementId: string
  supplementName: string
  description: string
  recommendation: string
}

type TrackerContextType = {
  trackedSupplements: TrackedSupplement[]
  intakeLogs: IntakeLog[]
  symptoms: Symptom[]
  symptomLogs: SymptomLog[]
  
  addTrackedSupplement: (
    data: Omit<TrackedSupplement, "id">,
  ) => Promise<{ success: boolean; warnings: string[] }>
  removeTrackedSupplement: (id: string) => Promise<boolean>
  updateTrackedSupplement: (
    id: string, 
    data: Partial<Omit<TrackedSupplement, "id">>
  ) => Promise<boolean>
  
  // Intake log functions to interact with the backend
  logIntake: (
    tracked_supplement_id: string,
    intake_date: string,
    dosage_taken: number,
    unit: string,
    notes?: string
  ) => Promise<boolean>
  getIntakeLogsForDate: (date: string) => Promise<IntakeLog[]>
  getTodayIntakeLogs: () => Promise<IntakeLog[]>
  getIntakeLogById: (id: string) => Promise<IntakeLog | null>
  updateIntakeLog: (id: string, data: Partial<Omit<IntakeLog, "id">>) => Promise<boolean>
  deleteIntakeLog: (id: string) => Promise<boolean>
  
  // Check for interactions
  checkInteractions: (supplementId: string) => Promise<string[]>

  // Mock symptom tracking functions
  logSymptom: (
    symptomId: string,
    date: string,
    severity: "none" | "mild" | "average" | "severe",
    notes?: string,
  ) => void
  getSymptomLogsForDate: (date: string) => SymptomLog[]
  getSymptomsForCategory: (category: string) => Symptom[]
  addSymptom: (name: string, category?: string, icon?: string) => void
}

const TrackerContext = createContext<TrackerContextType | undefined>(undefined)

export function TrackerProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth()
  const [trackedSupplements, setTrackedSupplements] = useState<TrackedSupplement[]>([])
  const [intakeLogs, setIntakeLogs] = useState<IntakeLog[]>([])
  
  // Add a cache for intake logs by date
  const [intakeLogsCache, setIntakeLogsCache] = useState<Record<string, IntakeLog[]>>({})
  
  // Mock symptom tracking states
  const [symptoms, setSymptoms] = useState<Symptom[]>([
    // General
    { id: "fine", name: "Everything is fine", category: "general", icon: "👍" },
    { id: "acne", name: "Skin issues", category: "general", icon: "🤡" },
    { id: "fatigue", name: "Fatigue", category: "general", icon: "🫠" },
    { id: "headache", name: "Headache", category: "general", icon: "🤕" },
    { id: "abdominal-pain", name: "Abdominal Pain", category: "general", icon: "😣" },
    { id: "dizziness", name: "Dizziness", category: "general", icon: "😵‍💫" },
    
    // Mood
    { id: "calm", name: "Calm", category: "mood", icon: "😌" },
    { id: "mood-swings", name: "Mood swings", category: "mood", icon: "🔄" },
    { id: "happy", name: "Happy", category: "mood", icon: "😊" },
    { id: "energetic", name: "Energetic", category: "mood", icon: "⚡" },
    { id: "irritated", name: "Irritated", category: "mood", icon: "🥴" },
    { id: "depressed", name: "Depressed", category: "mood", icon: "😓" },
    { id: "low-energy", name: "Low energy", category: "mood", icon: "🥱" },
    { id: "anxious", name: "Anxious", category: "mood", icon: "😰" },
    
    // Sleep
    { id: "insomnia", name: "Insomnia", category: "sleep", icon: "😳" },
    { id: "good-sleep", name: "Good sleep", category: "sleep", icon: "😴" },
    { id: "restless", name: "Restless", category: "sleep", icon: "🔄" },
    { id: "tired", name: "Tired", category: "sleep", icon: "🥱" },
    
    // Digestive
    { id: "bloating", name: "Bloating", category: "digestive", icon: "🎈" },
    { id: "nausea", name: "Nausea", category: "digestive", icon: "🤢" },
    { id: "constipation", name: "Constipation", category: "digestive", icon: "⏸️" },
    { id: "diarrhea", name: "Diarrhea", category: "digestive", icon: "⏩" },
    
    // Appetite
    { id: "low", name: "Low", category: "appetite", icon: "🫢" },
    { id: "normal", name: "Normal", category: "appetite", icon: "🍽️" },
    { id: "high", name: "High", category: "appetite", icon: "🍔" },
    
    // Physical Activity
    { id: "no-activity", name: "Didn't exercise", category: "activity", icon: "⭕️" },
    { id: "yoga", name: "Yoga", category: "activity", icon: "🧘‍♀️" },
    { id: "gym", name: "Gym", category: "activity", icon: "🏋️" },
    { id: "swimming", name: "Swimming", category: "activity", icon: "🏊‍♀️" },
    { id: "running", name: "Running", category: "activity", icon: "🏃" },
    { id: "cycling", name: "Cycling", category: "activity", icon: "🚴‍♀️" },
    { id: "team-sports", name: "Team Sports", category: "activity", icon: "⛹️‍♀️" },
    { id: "dancing", name: "Aerobics/Dancing", category: "activity", icon: "💃" },
  ])
  const [symptomLogs, setSymptomLogs] = useState<SymptomLog[]>([])

// Check interactions for a given supplement
const checkInteractions = async (supplementId: string): Promise<string[]> => {
  if (!supplementId.trim()) return []

  try {
    // Fetch interactions for the supplement from the backend
    const response = await fetch(
      `http://localhost:5001/api/supplements/by-supplement/${supplementId}`
    )

    if (!response.ok) {
      console.error("Failed to fetch interactions by supplement ID")
      return []
    }

    const data = await response.json()
    console.log("Fetched interactions:", data)

    // Extract and format interaction warnings
    const warnings: string[] = []

    // Get IDs of tracked supplements
    const trackedSupplementIds = trackedSupplements.map((s) => s.supplementId)
    console.log("Tracked supplement IDs:", trackedSupplementIds)

    // Process supplement-supplement interactions
    if (data.supplementSupplementInteractions) {
      data.supplementSupplementInteractions.forEach((interaction: any) => {
        // Check if the interacting supplement is already being tracked
        const interactingSupplements = interaction.supplements || []

        interactingSupplements.forEach((interactingSupplement: any) => {
          if (trackedSupplementIds.includes(interactingSupplement.supplementId) && interactingSupplement.supplementId !== supplementId) {
            const interactingSupplementName =
              interactingSupplement.name ||
              trackedSupplements.find((s) => s.supplementId === interactingSupplement.supplementId)
                ?.supplementName ||
              "Unknown supplement"

            const description = interaction.description || "No description provided."
            const recommendation = interaction.recommendation || "No recommendation provided."

            warnings.push(
              `Interaction with ${interactingSupplementName}: ${description}`
            )
            warnings.push('Recommendation: ' + recommendation)
          }
        })
      })
    }

    // Process supplement-food interactions (if applicable)
    if (data.supplementFoodInteractions) {
      data.supplementFoodInteractions.forEach((interaction: any) => {
        const description = interaction.description || "No description provided."
        const recommendation = interaction.recommendation || "No recommendation provided."
        warnings.push(
          `Food Interaction: ${description} Recommendation: ${recommendation}`
        )
      })
    }

    return warnings
  } catch (error) {
    console.error("Error while fetching interactions for supplement ID:", error)
    return []
  }
}

  // Add a tracked supplement
  const addTrackedSupplement = async (
    data: Omit<TrackedSupplement, "id">
  ): Promise<{ success: boolean; warnings: string[] }> => {
    try {

      console.log("Adding tracked supplement:", data)
      // Check for interactions with existing supplements
      const warnings = await checkInteractions(data.supplementId)
      if (warnings.length > 0) {
        console.warn("Interactions found:", warnings)
      }
      
      console.log("User ID:", user?._id)
      if (!user) {
        throw new Error("User not authenticated")
      }

      const response = await fetch(`http://localhost:5001/api/tracker_supplements_list/${user._id}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({
          supplementId: data.supplementId,
          supplementName: data.supplementName,
          dosage: data.dosage,
          unit: data.unit || "mg",
          frequency: data.frequency,
          startDate: data.startDate,
          endDate: data.endDate,
          notes: data.notes || "",
        }),
      })

      if (!response.ok) {
        throw new Error("Failed to add supplement to tracker.")
      }

      const result = await response.json()
      
      // Find the newly added supplement in the response
      const newSupplement = result.tracked_supplements?.find(
        (s: any) => s.supplementId === data.supplementId
      )
      
      if (newSupplement) {
        setTrackedSupplements(prev => [
          ...prev, 
          { 
            id: newSupplement._id,
            supplementId: newSupplement.supplementId,
            supplementName: newSupplement.supplementName,
            dosage: newSupplement.dosage,
            unit: newSupplement.unit,
            frequency: newSupplement.frequency,
            startDate: newSupplement.startDate,
            endDate: newSupplement.endDate,
            notes: newSupplement.notes
          }
        ])
      }
      
      return { success: true, warnings: warnings }
    } catch (error) {
      console.error("Error adding tracked supplement:", error)
      return { success: false, warnings: [] }
    }
  }

  // Log intake based on backend API
  const logIntake = async (
    tracked_supplement_id: string,
    intake_date: string,
    dosage_taken: number,
    unit: string,
    notes?: string
  ): Promise<boolean> => {
    try {
      console.log("User in logIntake:", user)
      if (!user) {
        throw new Error("User not authenticated")
      }
      console.log("Logging intake:", { tracked_supplement_id, intake_date, dosage_taken, unit, notes })

      const response = await fetch("http://localhost:5001/api/intake_logs/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({ 
          tracked_supplement_id, 
          intake_date, 
          dosage_taken, 
          unit, 
          notes 
        }),
      })

      console.log("Response for logging intake:", response)

      if (!response.ok) {
        throw new Error("Failed to log intake.")
      }

      const result = await response.json()
      
      // Add the new intake log to state
      const newLog: IntakeLog = {
        id: result._id,
        tracked_supplement_id: result.tracked_supplement_id,
        supplement_name: result.supplement_name,
        intake_date: result.intake_date,
        intake_time: result.intake_time,
        dosage_taken: result.dosage_taken,
        unit: result.unit,
        notes: result.notes,
        created_at: result.created_at,
        updated_at: result.updated_at
      }
      
      // Update both the global state and the cache
      setIntakeLogs(prev => {
        // Remove any existing log for the same supplement and date to avoid duplicates
        const filteredLogs = prev.filter(log => 
          !(log.tracked_supplement_id === tracked_supplement_id && log.intake_date === intake_date)
        );
        return [...filteredLogs, newLog];
      });
      
      // Also update the cache for this date
      const dateStr = intake_date
      setIntakeLogsCache(prevCache => {
        const updatedCache = { ...prevCache }
        
        if (updatedCache[dateStr]) {
          // Remove any existing log for the same supplement to avoid duplicates
          const filteredLogs = updatedCache[dateStr].filter(log => 
            !(log.tracked_supplement_id === tracked_supplement_id)
          );
          updatedCache[dateStr] = [...filteredLogs, newLog]
        } else {
          updatedCache[dateStr] = [newLog]
        }
        
        return updatedCache
      })
      
      // Invalid cache for today if it's not the same as the intake date
      const today = new Date().toISOString().split('T')[0]
      if (today !== intake_date && intakeLogsCache[today]) {
        // Force refresh of today's data next time it's requested
        setIntakeLogsCache(prev => {
          const updated = {...prev}
          delete updated[today];
          return updated;
        });
      }
      
      return true
    } catch (error) {
      console.error("Error logging intake:", error)
      return false
    }
  }

  // Get intake logs for a specific date (with caching)
  const getIntakeLogsForDate = async (date: string): Promise<IntakeLog[]> => {
    try {
      if (!user) {
        return []
      }

      // Check if we already have cached data for this date
      if (intakeLogsCache[date]) {
        return intakeLogsCache[date]
      }

      // If not in cache, fetch from API
      const response = await fetch(
        `http://localhost:5001/api/intake_logs/?start_date=${date}&end_date=${date}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      )

      if (!response.ok) {
        throw new Error("Failed to fetch intake logs.")
      }

      const logsData = await response.json()
      
      // Map the backend response to our IntakeLog type
      const logs: IntakeLog[] = logsData.map((log: any) => ({
        id: log._id,
        tracked_supplement_id: log.tracked_supplement_id,
        supplement_name: log.supplement_name,
        intake_date: log.intake_date,
        intake_time: log.intake_time,
        dosage_taken: log.dosage_taken,
        unit: log.unit,
        notes: log.notes,
        created_at: log.created_at,
        updated_at: log.updated_at
      }))
      
      // Update state with the fetched logs
      setIntakeLogs(logs)
      
      // Store in cache
      setIntakeLogsCache(prevCache => ({
        ...prevCache,
        [date]: logs
      }))
      
      return logs
    } catch (error) {
      console.error("Error fetching intake logs:", error)
      return []
    }
  }
  
  // Get today's intake logs using the dedicated endpoint
  const getTodayIntakeLogs = async (): Promise<IntakeLog[]> => {
    try {
      if (!user) {
        return []
      }

      const today = new Date().toISOString().split('T')[0] // Format as YYYY-MM-DD
      
      // Check if today's logs are already in cache
      if (intakeLogsCache[today]) {
        return intakeLogsCache[today]
      }

      const response = await fetch(
        "http://localhost:5001/api/intake_logs/today",
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      )

      if (!response.ok) {
        throw new Error("Failed to fetch today's intake logs.")
      }

      const logsData = await response.json()
      
      // Map the backend response to our IntakeLog type
      const logs: IntakeLog[] = logsData.map((log: any) => ({
        id: log._id,
        tracked_supplement_id: log.tracked_supplement_id,
        supplement_name: log.supplement_name,
        intake_date: log.intake_date,
        intake_time: log.intake_time,
        dosage_taken: log.dosage_taken,
        unit: log.unit,
        notes: log.notes,
        created_at: log.created_at,
        updated_at: log.updated_at
      }))
      
      // Update state with today's logs
      setIntakeLogs(logs)
      
      // Store in cache
      setIntakeLogsCache(prevCache => ({
        ...prevCache,
        [today]: logs
      }))
      
      return logs
    } catch (error) {
      console.error("Error fetching today's intake logs:", error)
      return []
    }
  }
  
  // Get a specific intake log by ID
  const getIntakeLogById = async (id: string): Promise<IntakeLog | null> => {
    try {
      if (!user) {
        return null
      }

      // Check if we can find the log in our cache first
      for (const date in intakeLogsCache) {
        const log = intakeLogsCache[date].find(log => log.id === id)
        if (log) {
          return log
        }
      }

      // If not found in cache, fetch from API
      const response = await fetch(
        `http://localhost:5001/api/intake_logs/${id}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      )

      if (!response.ok) {
        throw new Error("Failed to fetch intake log.")
      }

      const log = await response.json()
      
      return {
        id: log._id,
        tracked_supplement_id: log.tracked_supplement_id,
        supplement_name: log.supplement_name,
        intake_date: log.intake_date,
        intake_time: log.intake_time,
        dosage_taken: log.dosage_taken,
        unit: log.unit,
        notes: log.notes,
        created_at: log.created_at,
        updated_at: log.updated_at
      }
    } catch (error) {
      console.error("Error fetching intake log:", error)
      return null
    }
  }
  
  // Update an intake log
  const updateIntakeLog = async (
    id: string, 
    data: Partial<Omit<IntakeLog, "id">>
  ): Promise<boolean> => {
    try {
      if (!user) {
        throw new Error("User not authenticated")
      }

      const response = await fetch(
        `http://localhost:5001/api/intake_logs/${id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          body: JSON.stringify(data),
        }
      )

      if (!response.ok) {
        throw new Error("Failed to update intake log.")
      }

      const updatedLog = await response.json()
      
      // Update the log in state
      setIntakeLogs(prev => 
        prev.map(log => 
          log.id === id ? {
            ...log,
            ...data,
            updated_at: updatedLog.updated_at
          } : log
        )
      )
      
      // Also update in cache if it exists there
      setIntakeLogsCache(prevCache => {
        const newCache = { ...prevCache }
        for (const date in newCache) {
          newCache[date] = newCache[date].map(log => 
            log.id === id ? {
              ...log,
              ...data,
              updated_at: updatedLog.updated_at
            } : log
          )
        }
        return newCache
      })
      
      return true
    } catch (error) {
      console.error("Error updating intake log:", error)
      return false
    }
  }
  
  // Delete an intake log
  const deleteIntakeLog = async (id: string): Promise<boolean> => {
    try {
      if (!user) {
        throw new Error("User not authenticated")
      }

      // Find the log to get its date before deleting
      let logDate: string | null = null;
      let logSupplementId: string | null = null;
      
      // Look in the global state
      const logToDelete = intakeLogs.find(log => log.id === id);
      if (logToDelete) {
        logDate = logToDelete.intake_date;
        logSupplementId = logToDelete.tracked_supplement_id;
      } else {
        // Look in the cache
        for (const date in intakeLogsCache) {
          const log = intakeLogsCache[date].find(log => log.id === id);
          if (log) {
            logDate = log.intake_date;
            logSupplementId = log.tracked_supplement_id;
            break;
          }
        }
      }

      const response = await fetch(
        `http://localhost:5001/api/intake_logs/${id}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      )

      if (!response.ok) {
        throw new Error("Failed to delete intake log.")
      }

      // Remove the log from state
      setIntakeLogs(prev => prev.filter(log => log.id !== id))
      
      // Also remove from cache
      setIntakeLogsCache(prevCache => {
        const newCache = { ...prevCache }
        for (const date in newCache) {
          newCache[date] = newCache[date].filter(log => log.id !== id)
        }
        return newCache
      })
      
      // If logDate is different from today, invalidate today's cache
      if (logDate) {
        const today = new Date().toISOString().split('T')[0];
        if (today !== logDate && intakeLogsCache[today]) {
          // Force refresh of today's data next time it's requested
          setIntakeLogsCache(prev => {
            const updated = {...prev};
            delete updated[today];
            return updated;
          });
        }
      }
      
      return true
    } catch (error) {
      console.error("Error deleting intake log:", error)
      return false
    }
  }

  // Remove a tracked supplement
  const removeTrackedSupplement = async (id: string): Promise<boolean> => {
    try {
      if (!user) {
        throw new Error("User not authenticated")
      }

      const response = await fetch(`http://localhost:5001/api/tracker_supplements_list/${user._id}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({ _id: id }),
      })

      if (!response.ok) {
        throw new Error("Failed to remove supplement from tracker.")
      }

      setTrackedSupplements((prev) => prev.filter((item) => item.id !== id))
      return true
    } catch (error) {
      console.error("Error removing tracked supplement:", error)
      return false
    }
  }

  // Update a tracked supplement
  const updateTrackedSupplement = async (
    id: string,
    data: Partial<Omit<TrackedSupplement, "id">>
  ): Promise<boolean> => {
    try {
      if (!user) {
        throw new Error("User not authenticated")
      }

      const supplement = trackedSupplements.find(s => s.id === id)
      if (!supplement) {
        throw new Error("Supplement not found")
      }

      const updatedData = {
        _id: id,
        supplementId: data.supplementId || supplement.supplementId,
        supplementName: data.supplementName || supplement.supplementName,
        dosage: data.dosage || supplement.dosage,
        unit: data.unit || supplement.unit,
        frequency: data.frequency || supplement.frequency,
        startDate: data.startDate || supplement.startDate,
        endDate: data.endDate || supplement.endDate,
        notes: data.notes !== undefined ? data.notes : supplement.notes,
      }

      const response = await fetch(`http://localhost:5001/api/tracker_supplements_list/${user._id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify(updatedData),
      })

      if (!response.ok) {
        throw new Error("Failed to update supplement.")
      }

      setTrackedSupplements(prev => 
        prev.map(item => item.id === id ? { ...item, ...data } : item)
      )
      
      return true
    } catch (error) {
      console.error("Error updating tracked supplement:", error)
      return false
    }
  }

  // Modified function to log symptoms with localStorage persistence
  const logSymptom = (
    symptomId: string,
    date: string,
    severity: "none" | "mild" | "average" | "severe",
    notes?: string,
  ) => {
    if (!user) return

    // Find the symptom to get its name
    const symptom = symptoms.find(s => s.id === symptomId)
    if (!symptom) return

    // Check if a log already exists for this symptom and date
    const existingLogIndex = symptomLogs.findIndex(
      (log) => log.symptomId === symptomId && log.date === date && log.userId === user._id,
    )

    let updatedLogs: SymptomLog[] = [];

    if (existingLogIndex >= 0) {
      // Update existing log
      updatedLogs = [...symptomLogs]
      updatedLogs[existingLogIndex] = {
        ...updatedLogs[existingLogIndex],
        severity,
        notes,
        created_at: new Date().toISOString(),
      }
    } else {
      // Create new log
      const newLog: SymptomLog = {
        id: `symptom-log-${Date.now()}`,
        userId: user._id,
        date,
        symptomId,
        symptomName: symptom.name,
        severity,
        notes,
        created_at: new Date().toISOString(),
      }
      updatedLogs = [...symptomLogs, newLog]
    }
    
    // Update state
    setSymptomLogs(updatedLogs)
    
    // Persist to localStorage
    try {
      localStorage.setItem(`${user._id}-symptom-logs`, JSON.stringify(updatedLogs))
    } catch (error) {
      console.error("Failed to save symptom logs to localStorage:", error)
    }
  }

  // Mock function to get symptom logs for a specific date
  const getSymptomLogsForDate = (date: string) => {
    return symptomLogs.filter((log) => log.date === date && log.userId === user?._id)
  }
  
  // Mock function to get symptoms by category
  const getSymptomsForCategory = (category: string) => {
    return symptoms.filter(symptom => symptom.category === category)
  }
  
  // Mock function to add a new symptom
  const addSymptom = (name: string, category?: string, icon?: string) => {
    const newSymptom: Symptom = {
      id: `symptom-${Date.now()}`,
      name,
      category,
      icon
    }
    
    setSymptoms(prev => [...prev, newSymptom])
  }

  useEffect(() => {
    const fetchUserTrackerData = async () => {
      try {
        console.log(localStorage.getItem("token"))
        console.log("User in TrackerContext:", user)
        
        if (!user) {
          setTrackedSupplements([])
          setIntakeLogs([])
          setSymptomLogs([])
          return
        }
  
        // Fetch tracked supplements from backend
        const response = await fetch("http://localhost:5001/api/tracker_supplements_list/", {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          method: "GET"
        })
        
        if (!response.ok) {
          throw new Error("Failed to fetch tracker data")
        }
        
        const data = await response.json()
        console.log("Raw tracker data:", data)
        
        if (data && data.tracked_supplements) {
          const supplements = data.tracked_supplements.map((s: any) => ({
            id: s._id,
            supplementId: s.supplementId,
            supplementName: s.supplementName,
            dosage: s.dosage,
            unit: s.unit,
            frequency: s.frequency,
            startDate: s.startDate,
            endDate: s.endDate,
            notes: s.notes
          }))
          
          setTrackedSupplements(supplements)
          console.log("Fetched tracked supplements:", supplements)
        }
  
        // Fetch today's intake logs
        await getTodayIntakeLogs()
        
        // Load symptom logs from localStorage
        try {
          const savedSymptomLogs = localStorage.getItem(`${user._id}-symptom-logs`)
          if (savedSymptomLogs) {
            setSymptomLogs(JSON.parse(savedSymptomLogs))
          }
        } catch (error) {
          console.error("Failed to load symptom logs from localStorage:", error)
        }
      } catch (error) {
        console.error("Failed to fetch tracker data:", error)
      }
    }
  
    fetchUserTrackerData()
  }, [user])

  return (
    <TrackerContext.Provider
      value={{
        trackedSupplements,
        intakeLogs,
        addTrackedSupplement,
        removeTrackedSupplement,
        updateTrackedSupplement,
        logIntake,
        getIntakeLogsForDate,
        getTodayIntakeLogs,
        getIntakeLogById,
        updateIntakeLog,
        deleteIntakeLog,
        checkInteractions,
        symptoms,
        symptomLogs,
        logSymptom,
        getSymptomLogsForDate,
        getSymptomsForCategory,
        addSymptom,
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