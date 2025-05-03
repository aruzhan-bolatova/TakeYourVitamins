"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { format } from "date-fns"
import { TrackedSupplement, useTracker, type IntakeLog } from "@/contexts/tracker-context"
import { Check, X, Loader2 } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { useMemo } from "react"

export default function DailyLogPage() {
  const [selectedDate, setSelectedDate] = useState<Date>(new Date())
  const [isLoading, setIsLoading] = useState(true)
  const [dateIntakeLogs, setDateIntakeLogs] = useState<IntakeLog[]>([])
  const [dosageInputs, setDosageInputs] = useState<Record<string, number>>({})
  const [notes, setNotes] = useState<Record<string, string>>({})
  // Add states to track button action feedback
  const [activeButtons, setActiveButtons] = useState<Record<string, {action: string, timestamp: number}>>({})

  const {
    trackedSupplements,
    logIntake,
    getIntakeLogsForDate,
    updateIntakeLog,
    deleteIntakeLog,
    formatLocalDate,
    getTodayLocalDate
  } = useTracker()

  // Format date for display and API
  const formattedDate = formatLocalDate(format(selectedDate, "yyyy-MM-dd"))
  const dateString = format(selectedDate, "yyyy-MM-dd")

  // Memoize the fetch logs function to avoid recreation on every render
  const fetchLogs = useCallback(async () => {
    setIsLoading(true)
    try {
      const logs = await getIntakeLogsForDate(dateString)
      setDateIntakeLogs(logs)

      // Initialize dosage inputs based on supplements
      const initialDosages: Record<string, number> = {}
      const initialNotes: Record<string, string> = {}

      trackedSupplements.forEach(supplement => {
        // Find if there's a log for this supplement
        const log = logs.find(log => log.tracked_supplement_id === supplement.id)

        if (log) {
          initialDosages[supplement.id] = log.dosage_taken
          initialNotes[supplement.id] = log.notes || ''
        } else {
          // Default to the recommended dosage
          initialDosages[supplement.id] = parseFloat(supplement.dosage) || 0
          initialNotes[supplement.id] = ''
        }
      })

      setDosageInputs(initialDosages)
      setNotes(initialNotes)
    } finally {
      setIsLoading(false)
    }
  }, [dateString, trackedSupplements, getIntakeLogsForDate]) // Remove getIntakeLogsForDate from dependencies

  // Fetch logs for selected date
  useEffect(() => {
    fetchLogs()
  }, [fetchLogs]) // Only depend on the memoized function

    // Add effect to clear active buttons after a delay
    useEffect(() => {
      const now = Date.now()
      const buttonsToRemove = Object.entries(activeButtons)
        .filter(([_, data]) => now - data.timestamp > 2000) // Clear after 2 seconds
        .map(([id]) => id)
      
      if (buttonsToRemove.length > 0) {
        setActiveButtons(prev => {
          const newState = {...prev}
          buttonsToRemove.forEach(id => delete newState[id])
          return newState
        })
      }
      
      // Setup interval to check every second
      const interval = setInterval(() => {
        const now = Date.now()
        setActiveButtons(prev => {
          const newState = {...prev}
          let changed = false
          
          Object.entries(prev).forEach(([id, data]) => {
            if (now - data.timestamp > 2000) {
              delete newState[id]
              changed = true
            }
          })
          
          return changed ? newState : prev
        })
      }, 1000)
      
      return () => clearInterval(interval)
    }, [activeButtons])

  // Create a map of tracked supplement IDs to their intake logs
  const supplementLogMap = useMemo(() => {
    const map = new Map<string, IntakeLog>()
    dateIntakeLogs.forEach(log => {
      map.set(log.tracked_supplement_id, log)
    })
    return map
  }, [dateIntakeLogs])

  const handleDosageChange = (supplementId: string, value: string) => {
    const dosage = parseFloat(value) || 0
    setDosageInputs(prev => ({ ...prev, [supplementId]: dosage }))
  }

  const handleNotesChange = (supplementId: string, value: string) => {
    setNotes(prev => ({ ...prev, [supplementId]: value }))
  }

  const handleLogIntake = async (tracked_supplement: TrackedSupplement) => {
    // Check if selected date is in the future
    const today = getTodayLocalDate()
    const isFutureDate = dateString > today
    // Define trackerStartDate or remove this line if unnecessary
    const trackerStartDate = tracked_supplement.startDate; // Example: Replace with the actual start date
    const isBeforeStartDate = dateString < new Date(trackerStartDate).toISOString().split('T')[0]

    if (isFutureDate) {
      alert("You cannot log for a future date.")
      return
    }

    if (isBeforeStartDate) {
      alert("You cannot log for a date before your tracking start date.")
      return
    }
    try {
      setIsLoading(true)
      const supplement = trackedSupplements.find(s => s.id === tracked_supplement.id)
      if (!supplement) return

      const dosage = dosageInputs[supplement.id] || parseFloat(supplement.dosage) || 0
      const noteText = notes[supplement.id] || ''
      const existingLog = supplementLogMap.get(supplement.id)

      if (existingLog) {
        await updateIntakeLog(existingLog.id, {
          dosage_taken: dosage,
          notes: noteText
        })
        console.log("Updated log:", existingLog.id)
      } else {
        await logIntake(
          supplement.id,
          dateString,
          dosage,
          supplement.unit || 'mg',
          noteText
        )
      }

      await fetchLogs()
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteLog = async (supplementId: string) => {
    try {
      setIsLoading(true)
      const existingLog = supplementLogMap.get(supplementId)

      if (existingLog) {
        await deleteIntakeLog(existingLog.id)
        // Refresh logs using our memoized function
        await fetchLogs()
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Daily Supplement Log</h1>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Select Date</CardTitle>
            <CardDescription>Choose a date to view or log your supplement intake</CardDescription>
          </CardHeader>
          <CardContent>
            <Calendar
              mode="single"
              selected={selectedDate}
              onSelect={(date) => date && setSelectedDate(date)}
              className="rounded-md border"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Supplement Log for {formattedDate}</CardTitle>
            <CardDescription>Track which supplements you've taken today</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              </div>
            ) : trackedSupplements.length === 0 ? (
              <div className="text-center py-6">
                <p className="text-muted-foreground">No supplements being tracked.</p>
                <Button className="mt-2" asChild>
                  <a href="/dashboard/tracker/add">Add a supplement</a>
                </Button>
              </div>
            ) : (
              <div className="space-y-6">
                {trackedSupplements.map((supplement) => {
                  const existingLog = supplementLogMap.get(supplement.id)
                  const hasLoggedToday = !!existingLog

                  return (
                    <div key={supplement.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-medium text-lg">{supplement.supplementName}</h3>
                        {hasLoggedToday && (
                          <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                            Logged
                          </Badge>
                        )}
                      </div>

                      <div className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label htmlFor={`dosage-${supplement.id}`}>Dosage ({supplement.unit || 'mg'})</Label>
                            <Input
                              id={`dosage-${supplement.id}`}
                              type="number"
                              value={dosageInputs[supplement.id] || ''}
                              onChange={(e) => handleDosageChange(supplement.id, e.target.value)}
                              placeholder={supplement.dosage}
                            />
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor={`notes-${supplement.id}`}>Notes (optional)</Label>
                            <Input
                              id={`notes-${supplement.id}`}
                              value={notes[supplement.id] || ''}
                              onChange={(e) => handleNotesChange(supplement.id, e.target.value)}
                              placeholder="Add notes..."
                            />
                          </div>
                        </div>

                        <div className="flex justify-end gap-3">
                          {hasLoggedToday && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleDeleteLog(supplement.id)}
                              disabled={isLoading}
                            >
                              <X className="h-4 w-4 mr-1" />
                              Remove Log
                            </Button>
                          )}
                          <Button
                            size="sm"
                            onClick={() => handleLogIntake(supplement)}
                            disabled={isLoading}
                          >
                            <Check className="h-4 w-4 mr-1" />
                            {hasLoggedToday ? 'Update Log' : 'Log Intake'}
                          </Button>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}