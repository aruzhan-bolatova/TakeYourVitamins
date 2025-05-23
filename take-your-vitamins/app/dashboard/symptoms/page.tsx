"use client"

import { useState, useEffect, useCallback, useMemo } from "react"
import { format } from "date-fns"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Activity, Loader2, RefreshCw } from "lucide-react"
import { useTracker, type SymptomLog, type Symptom } from "@/contexts/tracker-context"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { CategorySymptomLogger } from "@/components/category-symptom-logger"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

export default function SymptomsPage() {
  const { symptomLogs, getSymptomLogsForDate, getDatesWithSymptoms, formatLocalDate, getTodayLocalDate } = useTracker()
  const [selectedDate, setSelectedDate] = useState<Date>(new Date())
  const [datesWithSymptoms, setDatesWithSymptoms] = useState<Date[]>([])
  const [logsForSelectedDate, setLogsForSelectedDate] = useState<SymptomLog[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshKey, setRefreshKey] = useState(0) // Add a refresh key to force re-renders

  // Dialog open states
  const [symptomsDialogOpen, setSymptomsDialogOpen] = useState(false)

  // Get date string for the selected date
  const dateString = format(selectedDate, "yyyy-MM-dd")

  // Format the date for display with better error handling
  const formattedDate = useMemo(() => {
    try {
      return formatLocalDate(dateString);
    } catch (error) {
      console.error("Error formatting date:", error);
      return format(selectedDate, "EEEE, MMMM d, yyyy");
    }
  }, [dateString, formatLocalDate]);

  // Check if selected date is in the future
  const isDisabled = useMemo(() => {
    try {
      const today = getTodayLocalDate();
      return dateString > today;
    } catch (error) {
      console.error("Error checking date:", error);
      // Fallback to simple JS comparison if our utility fails
      return new Date(dateString) > new Date();
    }
  }, [dateString, getTodayLocalDate]);

  // Memoized function to fetch logs for the selected date
  const fetchLogsForDate = useCallback(
    async (date: string, forceRefresh = false) => {
      setLoading(true)
      try {
        console.log("Fetching logs for date:", date, "Force refresh:", forceRefresh)
        const logs = await getSymptomLogsForDate(date, forceRefresh)
        console.log("Fetched logs for date:", date, logs)
        setLogsForSelectedDate(logs)
        return logs
      } catch (error) {
        console.error("Error fetching logs:", error)
        return []
      } finally {
        setLoading(false)
      }
    },
    [getSymptomLogsForDate],
  )

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

  // Fetch logs when the selected date changes
  useEffect(() => {
    fetchLogsForDate(dateString)
  }, [dateString, fetchLogsForDate, refreshKey]) // Add refreshKey to dependencies

  // Fetch dates with symptoms on initial load and when dialog closes
  useEffect(() => {
    fetchDatesWithSymptoms()
  }, [fetchDatesWithSymptoms, symptomsDialogOpen, refreshKey]) // Add refreshKey to dependencies

  // Handle completion of symptom logging
  const handleSymptomLogComplete = async () => {
    try {
      // First fetch the updated logs - force refresh to bypass cache
      setLoading(true)
      const updatedLogs = await fetchLogsForDate(dateString, true)
      console.log("Updated logs after logging:", updatedLogs)
      
      // Explicitly update the logs for the selected date
      setLogsForSelectedDate(updatedLogs)
      
      // Refresh the dates with symptoms
      await fetchDatesWithSymptoms()
      
      // Force a refresh with the new data
      setRefreshKey((prev) => prev + 1)
    } catch (error) {
      console.error("Error refreshing logs after symptom logging:", error)
    } finally {
      // Close the dialog after data is updated
      setSymptomsDialogOpen(false)
      setLoading(false)
    }
  }

  // Manual refresh function
  const handleManualRefresh = async () => {
    setLoading(true)
    try {
      // Fetch and update logs for the current date - force refresh
      const updatedLogs = await fetchLogsForDate(dateString, true)
      setLogsForSelectedDate(updatedLogs)
      
      // Refresh the dates with symptoms
      await fetchDatesWithSymptoms()
      
      // Force a re-render
      setRefreshKey((prev) => prev + 1)
    } catch (error) {
      console.error("Error during manual refresh:", error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Health Tracker</h1>
      <div className="flex grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Calendar</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center">
            <Calendar
              mode="single"
              selected={selectedDate}
              onSelect={(date) => date && setSelectedDate(date)}
              className="rounded-md border mx-auto"
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

            <p className="text-center my-4">
              Selected date: <strong>{formattedDate}</strong>
            </p>

            <div className="flex items-center justify-center gap-4">
              <Dialog open={symptomsDialogOpen} onOpenChange={setSymptomsDialogOpen}>
                <DialogTrigger asChild>
                  <Button className="flex items-center gap-2"
                  disabled={isDisabled}>
                    <Activity className="h-4 w-4" />
                    Log Symptoms
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-[500px]">
                  <DialogHeader>
                    <DialogTitle>Log Symptoms for {formattedDate}</DialogTitle>
                  </DialogHeader>
                  <CategorySymptomLogger date={dateString} onComplete={handleSymptomLogComplete} />
                </DialogContent>
              </Dialog>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Symptoms Summary</CardTitle>
            <Button
              variant="outline"
              size="icon"
              onClick={handleManualRefresh}
              disabled={loading}
              title="Refresh symptoms"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            </Button>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex items-center justify-center h-40">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
                <span className="ml-2">Loading symptoms...</span>
              </div>
            ) : (
              <SymptomSummary
                date={dateString}
                logs={logsForSelectedDate}
                key={`summary-${dateString}-${JSON.stringify(logsForSelectedDate)}-${refreshKey}`}
              />
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

// Update the SymptomSummary component to use the correct property names
function SymptomSummary({ date, logs }: { date: string; logs: SymptomLog[] }) {
  const { symptoms, fetchSymptoms } = useTracker()
  const [activeSymptomLogs, setActiveSymptomLogs] = useState<SymptomLog[]>([])
  const [availableSymptoms, setAvailableSymptoms] = useState<Symptom[]>(symptoms)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Fetch symptoms if needed
  useEffect(() => {
    const getSymptoms = async () => {
      if (symptoms.length === 0) {
        setLoading(true)
        try {
          const fetchedSymptoms = await fetchSymptoms()
          setAvailableSymptoms(fetchedSymptoms)
        } catch (err) {
          console.error("Error fetching symptoms:", err)
          setError("Failed to fetch symptoms")
        } finally {
          setLoading(false)
        }
      } else {
        setAvailableSymptoms(symptoms)
      }
    }

    getSymptoms()
  }, [symptoms, fetchSymptoms])

  // Process logs when they change
  useEffect(() => {
    try {
      console.log("Processing logs in SymptomSummary:", logs)
      // Filter active symptoms (severity not "none")
      const activeLogs = logs.filter((log) => log.severity !== "none")
      setActiveSymptomLogs(activeLogs)
      console.log("Active symptom logs:", activeLogs)
    } catch (err) {
      console.error("Error processing logs:", err)
      setError("Failed to process symptom logs")
    }
  }, [logs])

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-40">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <span className="ml-2">Loading symptoms...</span>
      </div>
    )
  }

  if (activeSymptomLogs.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No symptoms logged for this day</p>
      </div>
    )
  }

  // Define categories and their colors
  const categories = [
    { id: "general", name: "General", color: "border-purple-300", icon: "🔍" },
    { id: "mood", name: "Mood", color: "border-orange-300", icon: "😊" },
    { id: "sleep", name: "Sleep", color: "border-blue-300", icon: "😴" },
    { id: "digestive", name: "Digestive", color: "border-pink-300", icon: "🍽️" },
    { id: "appetite", name: "Appetite", color: "border-yellow-300", icon: "🥑" },
    { id: "activity", name: "Physical Activity", color: "border-green-300", icon: "🏃‍♀️" },
  ]

  // Group symptoms by category
  const symptomsByCategory: Record<string, Array<Symptom>> = {}

  // Initialize categories
  categories.forEach((category) => {
    symptomsByCategory[category.id] = []
  })

  // Group active symptoms by their categories
  activeSymptomLogs.forEach((log) => {
    const symptom = availableSymptoms.find((s) => s.id === log.symptom_id)
    if (symptom) {
      console.log("Found symptom for log:", symptom, log)

      // Determine the category
      let categoryId = "general" // Default category

      if (symptom.categoryName) {
        const categoryName = symptom.categoryName.toLowerCase()
        if (categoryName.includes("general")) categoryId = "general"
        else if (categoryName.includes("mood")) categoryId = "mood"
        else if (categoryName.includes("sleep")) categoryId = "sleep"
        else if (categoryName.includes("digestive")) categoryId = "digestive"
        else if (categoryName.includes("appetite")) categoryId = "appetite"
        else if (categoryName.includes("activity") || categoryName.includes("physical")) categoryId = "activity"
      }

      // Add to the appropriate category if not already there
      if (!symptomsByCategory[categoryId].some((s) => s.id === symptom.id)) {
        symptomsByCategory[categoryId].push(symptom)
      }
    } else {
      console.warn("Could not find symptom for log:", log)
    }
  })

    // Get unique notes from all logs
    const allNotes = Array.from(
        new Set(
            activeSymptomLogs
                .filter((log) => log.notes && log.notes.trim() !== "")
                .map((log) => log.notes)
        )
    ).join("\n\n")

  return (
    <div className="space-y-2">
      {categories.map((category) => {
        const categorySymptoms = symptomsByCategory[category.id]

        // Skip empty categories
        if (!categorySymptoms || categorySymptoms.length === 0) return null

        return (
          <div key={category.id} className={`rounded-lg border p-2 ${category.color}`}>
            <div className="flex items-center gap-2">
              <span className="text-xl">{category.icon}</span>
              <h3 className="font-medium">{category.name}</h3>
            </div>

            <div className="grid grid-cols-2 gap-2">
              {categorySymptoms.map((symptom) => (
                <div key={symptom.id} className="rounded-md px-3 py-2 flex items-center">
                  {symptom.icon && <span className="mr-2 text-lg">{symptom.icon}</span>}
                  <span>{symptom.name}</span>
                </div>
              ))}
            </div>
          </div>
        )
      })}

      {allNotes && (
        <div className="mt-6 bg-gray-50 rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xl">📝</span>
            <h3 className="font-medium">Notes</h3>
          </div>
          <p className="text-gray-700 italic whitespace-pre-line">{allNotes}</p>
        </div>
      )}
    </div>
  )
}

