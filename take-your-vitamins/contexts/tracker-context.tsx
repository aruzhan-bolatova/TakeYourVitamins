"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import { useAuth } from "./auth-context"
import { warn } from "console"
import { getTodayLocalDate, formatLocalDate, localToUTC } from "@/lib/date-utils"

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

// Symptom tracking types based on backend implementation
export type Symptom = {
  id: string
  name: string
  icon?: string
  categoryId?: string
  categoryName?: string
  categoryIcon?: string
}

export type SymptomLog = {
  id: string
  user_id: string
  symptom_id: string
  date: string
  severity: "none" | "mild" | "average" | "severe"
  notes?: string
  created_at: string
  updated_at?: string
}

export type SymptomCategory = {
  id: string
  name: string
  icon: string
  symptoms: Array<{
    id: string
    name: string
    icon: string
    severity: string
  }>
}

export type SymptomSummary = {
  categories: SymptomCategory[]
  notes: string
  date: string
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

  addTrackedSupplement: (data: Omit<TrackedSupplement, "id">) => Promise<{ success: boolean; warnings: string[] }>
  removeTrackedSupplement: (id: string) => Promise<boolean>
  updateTrackedSupplement: (id: string, data: Partial<Omit<TrackedSupplement, "id">>) => Promise<boolean>

  // Intake log functions
  logIntake: (
    tracked_supplement_id: string,
    intake_date: string,
    dosage_taken: number,
    unit: string,
    notes?: string,
  ) => Promise<boolean>
  getIntakeLogsForDate: (date: string) => Promise<IntakeLog[]>
  getTodayIntakeLogs: () => Promise<IntakeLog[]>
  getIntakeLogById: (id: string) => Promise<IntakeLog | null>
  updateIntakeLog: (id: string, data: Partial<Omit<IntakeLog, "id">>) => Promise<boolean>
  deleteIntakeLog: (id: string) => Promise<boolean>

  // Check for interactions
  checkInteractions: (supplementId: string) => Promise<string[]>

  // Updated symptom tracking functions based on backend implementation
  logSymptom: (
    symptom_id: string,
    date: string,
    severity: "none" | "mild" | "average" | "severe",
    notes?: string,
  ) => Promise<boolean>
  getSymptomLogsForDate: (date: string, forceRefresh?: boolean) => Promise<SymptomLog[]>
  getSymptomsForCategory: (category_id: string) => Promise<Symptom[]>
  addSymptom: (name: string, category_id: string, icon?: string) => Promise<boolean>
  fetchSymptoms: () => Promise<Symptom[]>
  fetchSymptomCategories: () => Promise<Record<string, SymptomCategory>>
  getSymptomSummaryForDate: (date: string) => Promise<SymptomSummary | null>
  deleteSymptomLog: (log_id: string) => Promise<boolean>
  getDatesWithSymptoms: () => Promise<string[]>

  // Additional utility functions
  formatLocalDate: (date: string) => string
  getTodayLocalDate: () => string
}

const TrackerContext = createContext<TrackerContextType | undefined>(undefined)

export function TrackerProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth()
  const [trackedSupplements, setTrackedSupplements] = useState<TrackedSupplement[]>([])
  const [intakeLogs, setIntakeLogs] = useState<IntakeLog[]>([])

  // Add a cache for intake logs by date
  const [intakeLogsCache, setIntakeLogsCache] = useState<Record<string, IntakeLog[]>>({})

  // Symptom tracking states
  const [symptoms, setSymptoms] = useState<Symptom[]>([])
  const [symptomCategories, setSymptomCategories] = useState<Record<string, SymptomCategory>>({})
  const [symptomLogs, setSymptomLogs] = useState<SymptomLog[]>([])
  const [symptomLogsCache, setSymptomLogsCache] = useState<Record<string, SymptomLog[]>>({})

  // Check interactions for a given supplement
  const checkInteractions = async (supplementId: string): Promise<string[]> => {
    if (!supplementId.trim()) return []

    try {
      // Fetch interactions for the supplement from the backend
      const response = await fetch(`http://localhost:5001/api/supplements/by-supplement/${supplementId}`)

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
            if (
              trackedSupplementIds.includes(interactingSupplement.supplementId) &&
              interactingSupplement.supplementId !== supplementId
            ) {
              const interactingSupplementName =
                interactingSupplement.name ||
                trackedSupplements.find((s) => s.supplementId === interactingSupplement.supplementId)?.supplementName ||
                "Unknown supplement"

              const description = interaction.description || "No description provided."
              const recommendation = interaction.recommendation || "No recommendation provided."

              warnings.push(`Interaction with ${interactingSupplementName}: ${description}`)
              warnings.push("Recommendation: " + recommendation)
            }
          })
        })
      }

      // Process supplement-food interactions (if applicable)
      if (data.supplementFoodInteractions) {
        data.supplementFoodInteractions.forEach((interaction: any) => {
          const description = interaction.description || "No description provided."
          const recommendation = interaction.recommendation || "No recommendation provided."
          warnings.push(`Food Interaction: ${description}`)
          warnings.push("Recommendation: " + recommendation)
        })
      }
      console.log("Warnings:", warnings)
      return warnings
    } catch (error) {
      console.error("Error while fetching interactions for supplement ID:", error)
      return []
    }
  }

  // Add a tracked supplement
  const addTrackedSupplement = async (
    data: Omit<TrackedSupplement, "id">,
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
      const newSupplement = result.tracked_supplements?.find((s: any) => s.supplementId === data.supplementId)

      if (newSupplement) {
        setTrackedSupplements((prev) => [
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
            notes: newSupplement.notes,
          },
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
    notes?: string,
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
          notes,
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
        updated_at: result.updated_at,
      }

      // Update both the global state and the cache
      setIntakeLogs((prev) => [...prev, newLog])

      // Also update the cache for this date
      const dateStr = intake_date
      setIntakeLogsCache((prevCache) => {
        const updatedCache = { ...prevCache }
        if (updatedCache[dateStr]) {
          updatedCache[dateStr] = [...updatedCache[dateStr], newLog]
        } else {
          updatedCache[dateStr] = [newLog]
        }
        return updatedCache
      })

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
      const response = await fetch(`http://localhost:5001/api/intake_logs/?start_date=${date}&end_date=${date}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      })

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
        updated_at: log.updated_at,
      }))

      // Update state with the fetched logs
      setIntakeLogs(logs)

      // Store in cache
      setIntakeLogsCache((prevCache) => ({
        ...prevCache,
        [date]: logs,
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

      const today = getTodayLocalDate() // Use local today's date instead of UTC

      // Check if today's logs are already in cache
      if (intakeLogsCache[today]) {
        return intakeLogsCache[today]
      }

      const response = await fetch("http://localhost:5001/api/intake_logs/today", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      })

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
        updated_at: log.updated_at,
      }))

      // Update state with today's logs
      setIntakeLogs(logs)

      // Store in cache
      setIntakeLogsCache((prevCache) => ({
        ...prevCache,
        [today]: logs,
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
        const log = intakeLogsCache[date].find((log) => log.id === id)
        if (log) {
          return log
        }
      }

      // If not found in cache, fetch from API
      const response = await fetch(`http://localhost:5001/api/intake_logs/${id}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      })

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
        updated_at: log.updated_at,
      }
    } catch (error) {
      console.error("Error fetching intake log:", error)
      return null
    }
  }

  // Update an intake log
  const updateIntakeLog = async (id: string, data: Partial<Omit<IntakeLog, "id">>): Promise<boolean> => {
    try {
      if (!user) {
        throw new Error("User not authenticated")
      }

      const response = await fetch(`http://localhost:5001/api/intake_logs/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        throw new Error("Failed to update intake log.")
      }

      const updatedLog = await response.json()

      // Update the log in state
      setIntakeLogs((prev) =>
        prev.map((log) =>
          log.id === id
            ? {
              ...log,
              ...data,
              updated_at: updatedLog.updated_at,
            }
            : log,
        ),
      )

      // Also update in cache if it exists there
      setIntakeLogsCache((prevCache) => {
        const newCache = { ...prevCache }
        for (const date in newCache) {
          newCache[date] = newCache[date].map((log) =>
            log.id === id
              ? {
                ...log,
                ...data,
                updated_at: updatedLog.updated_at,
              }
              : log,
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

      const response = await fetch(`http://localhost:5001/api/intake_logs/${id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      })

      if (!response.ok) {
        throw new Error("Failed to delete intake log.")
      }

      // Remove the log from state
      setIntakeLogs((prev) => prev.filter((log) => log.id !== id))

      // Also remove from cache
      setIntakeLogsCache((prevCache) => {
        const newCache = { ...prevCache }
        for (const date in newCache) {
          newCache[date] = newCache[date].filter((log) => log.id !== id)
        }
        return newCache
      })

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

      console.log("User ID:", user._id)
      console.log("Removing tracked supplement:", id)

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
    data: Partial<Omit<TrackedSupplement, "id">>,
  ): Promise<boolean> => {
    try {
      if (!user) {
        throw new Error("User not authenticated")
      }

      const supplement = trackedSupplements.find((s) => s.id === id)
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

      setTrackedSupplements((prev) => prev.map((item) => (item.id === id ? { ...item, ...data } : item)))

      return true
    } catch (error) {
      console.error("Error updating tracked supplement:", error)
      return false
    }
  }

  // Fetch all available symptoms
  const fetchSymptoms = async (): Promise<Symptom[]> => {
    try {
      if (!user) return []

      console.log("Fetching symptoms from API...")
      const response = await fetch("http://localhost:5001/api/symptom-logs/symptoms", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      })

      if (!response.ok) {
        throw new Error(`Failed to fetch symptoms: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()
      console.log("Raw symptoms data:", data)

      // Access the symptoms array from the response
      const symptomsArray = data.symptoms || []

      // Map the response to our Symptom type
      const mappedSymptoms: Symptom[] = Array.isArray(symptomsArray)
        ? symptomsArray.map((symptom: any) => ({
          id: symptom._id,
          name: symptom.name,
          icon: symptom.icon,
          categoryId: symptom.categoryId,
          categoryName: symptom.categoryName,
          categoryIcon: symptom.categoryIcon,
        }))
        : []

      console.log("Mapped symptoms:", mappedSymptoms)
      setSymptoms(mappedSymptoms)
      return mappedSymptoms
    } catch (error) {
      console.error("Error fetching symptoms:", error)
      return []
    }
  }

  // Fetch symptom categories
  const fetchSymptomCategories = async (): Promise<Record<string, SymptomCategory>> => {
    try {
      if (!user) return {}

      // Since there's no direct endpoint for categories, we'll extract them from symptoms
      const symptomsData = await fetchSymptoms()

      // Group symptoms by category
      const categoriesMap: Record<string, SymptomCategory> = {}

      symptomsData.forEach((symptom) => {
        if (symptom.categoryId && symptom.categoryName) {
          if (!categoriesMap[symptom.categoryId]) {
            categoriesMap[symptom.categoryId] = {
              id: symptom.categoryId,
              name: symptom.categoryName,
              icon: symptom.categoryIcon || "❓",
              symptoms: [],
            }
          }

          // Add symptom to category
          categoriesMap[symptom.categoryId].symptoms.push({
            id: symptom.id,
            name: symptom.name,
            icon: symptom.icon || "❓",
            severity: "none", // Default severity
          })
        }
      })

      setSymptomCategories(categoriesMap)
      return categoriesMap
    } catch (error) {
      console.error("Error creating symptom categories:", error)
      return {}
    }
  }

  // Log a symptom
  const logSymptom = async (
    symptom_id: string,
    date: string,
    severity: "none" | "mild" | "average" | "severe",
    notes?: string,
  ): Promise<boolean> => {
    try {
      if (!user) {
        throw new Error("User not authenticated")
      }

      const response = await fetch("http://localhost:5001/api/symptom-logs/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({
          symptom_id,
          date,
          severity,
          notes: notes || "",
        }),
      })

      if (!response.ok) {
        throw new Error("Failed to log symptom")
      }

      const result = await response.json()

      // Update the symptom logs cache for this date
      await getSymptomLogsForDate(date)

      return true
    } catch (error) {
      console.error("Error logging symptom:", error)
      return false
    }
  }

  // Get symptom logs for a given date
  const getSymptomLogsForDate = async (date: string, forceRefresh = false): Promise<SymptomLog[]> => {
    if (!user) return []

    // Return cached logs if available and not forcing refresh
    if (symptomLogsCache[date] && !forceRefresh) {
      console.log("Returning cached logs for date:", date, symptomLogsCache[date])
      return symptomLogsCache[date]
    }

    try {
      const response = await fetch(`http://localhost:5001/api/symptom-logs/date/${date}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      })

      if (!response.ok) {
        throw new Error("Failed to fetch symptom logs")
      }

      const data = await response.json()
      const logs = data.logs || []
      console.log("API returned symptom logs for date:", date, logs)

      // Update the cache with the fetched logs
      setSymptomLogsCache((prevCache) => ({
        ...prevCache,
        [date]: logs,
      }))

      // Update the symptomLogs state as well
      setSymptomLogs((prevLogs) => {
        // Remove existing logs for this date
        const filteredLogs = prevLogs.filter((log) => log.date !== date)
        // Add new logs for this date
        return [...filteredLogs, ...logs]
      })

      return logs
    } catch (error) {
      console.error("Error fetching symptom logs:", error)
      return []
    }
  }

  // Get symptoms for a specific category
  const getSymptomsForCategory = async (category_id: string): Promise<Symptom[]> => {
    try {
      if (!user) return []

      // Since there's no direct endpoint for this, we'll filter from all symptoms
      const allSymptoms = await fetchSymptoms()
      return allSymptoms.filter((symptom) => symptom.categoryId === category_id)
    } catch (error) {
      console.error("Error fetching symptoms by category:", error)
      return []
    }
  }

  // Get symptom summary for a date
  const getSymptomSummaryForDate = async (date: string): Promise<SymptomSummary | null> => {
    try {
      if (!user) return null

      const response = await fetch(`http://localhost:5001/api/symptom-logs/summary/${date}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      })

      if (!response.ok) {
        throw new Error("Failed to fetch symptom summary")
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error("Error fetching symptom summary:", error)
      return null
    }
  }

  // Add a new custom symptom
  const addSymptom = async (name: string, category_id: string, icon?: string): Promise<boolean> => {
    try {
      if (!user) {
        throw new Error("User not authenticated")
      }

      // Note: This endpoint doesn't exist in the provided backend code
      // You would need to implement it on the backend
      console.error("Add symptom endpoint not implemented in backend")
      return false

      /* Implementation if endpoint existed:
      const response = await fetch("http://localhost:5001/api/symptoms/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({
          name,
          categoryId: category_id,
          icon: icon || "❓",
        }),
      })

      if (!response.ok) {
        throw new Error("Failed to add symptom")
      }

      // Update the symptoms list
      await fetchSymptoms()

      return true
      */
    } catch (error) {
      console.error("Error adding symptom:", error)
      return false
    }
  }

  // Delete a symptom log
  const deleteSymptomLog = async (log_id: string): Promise<boolean> => {
    try {
      if (!user) {
        throw new Error("User not authenticated")
      }

      const response = await fetch(`http://localhost:5001/api/symptom-logs/${log_id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      })

      if (!response.ok) {
        throw new Error("Failed to delete symptom log")
      }

      // Update the symptom logs state
      setSymptomLogs((prev) => prev.filter((log) => log.id !== log_id))

      // Also update the cache
      setSymptomLogsCache((prevCache) => {
        const newCache = { ...prevCache }
        for (const date in newCache) {
          newCache[date] = newCache[date].filter((log) => log.id !== log_id)
        }
        return newCache
      })

      return true
    } catch (error) {
      console.error("Error deleting symptom log:", error)
      return false
    }
  }

  // Get dates with symptoms
  const getDatesWithSymptoms = async (): Promise<string[]> => {
    try {
      if (!user) return []

      const response = await fetch("http://localhost:5001/api/symptom-logs/dates-with-symptoms", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      })

      if (!response.ok) {
        throw new Error("Failed to fetch dates with symptoms")
      }

      const data = await response.json()
      return data.dates || []
    } catch (error) {
      console.error("Error fetching dates with symptoms:", error)
      return []
    }
  }

  // Get tracked supplements that should be taken today
  const getTodayTrackedSupplements = async (): Promise<TrackedSupplement[]> => {
    try {
      if (!user) {
        console.warn("User not authenticated, cannot fetch tracked supplements")
        return []
      }

      // Use local date for today instead of UTC
      const today = getTodayLocalDate()
      
      // Get all tracked supplements
      const allSupplements = await getTrackedSupplements()
      
      // Filter supplements that are active today (started before or on today, and either not ended or ended after today)
      return allSupplements.filter(supp => {
        const startDate = supp.startDate.split('T')[0] // Extract just the date part
        const endDate = supp.endDate ? supp.endDate.split('T')[0] : undefined
        
        const hasStarted = startDate <= today
        const hasNotEnded = !endDate || endDate >= today
        
        return hasStarted && hasNotEnded
      })
    } catch (error) {
      console.error("Error fetching today's tracked supplements:", error)
      return []
    }
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
          method: "GET",
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
            notes: s.notes,
          }))

          setTrackedSupplements(supplements)
          console.log("Fetched tracked supplements:", supplements)
        }

        // Fetch today's intake logs
        await getTodayIntakeLogs()

        // Fetch symptoms and categories
        await fetchSymptoms()
        await fetchSymptomCategories()

        // Fetch today's symptom logs
        const today = new Date().toISOString().split("T")[0]
        await getSymptomLogsForDate(today)
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

        // Updated symptom tracking functions
        symptoms,
        symptomLogs,
        logSymptom,
        getSymptomLogsForDate,
        getSymptomsForCategory,
        addSymptom,
        fetchSymptoms,
        fetchSymptomCategories,
        getSymptomSummaryForDate,
        deleteSymptomLog,
        getDatesWithSymptoms,

        // Additional utility functions
        formatLocalDate,
        getTodayLocalDate,
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

export type UseTracker = ReturnType<typeof useTracker>
