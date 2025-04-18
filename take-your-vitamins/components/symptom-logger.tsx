"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useTracker } from "@/contexts/tracker-context"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface SymptomLoggerProps {
  date: string
}

export function SymptomLogger({ date }: SymptomLoggerProps) {
  const { symptoms, symptomLogs, logSymptom, getSymptomLogsForDate } = useTracker()
  const [notes, setNotes] = useState("")

  // Get existing logs for this date
  const logsForDate = getSymptomLogsForDate(date)

  // Create a map of symptom IDs to their severity
  const symptomSeverityMap = new Map()
  logsForDate.forEach((log) => {
    symptomSeverityMap.set(log.symptomId, log.severity)
  })

  // Find notes for this date (assuming one notes field per day)
  const existingNotes = logsForDate.find((log) => log.notes)?.notes || ""

  // Set initial notes state from existing notes
  useEffect(() => {
    setNotes(existingNotes)
  }, [date, existingNotes])

  // Handle severity change
  const handleSeverityChange = (symptomId: string, severity: "none" | "mild" | "average" | "severe") => {
    logSymptom(symptomId, date, severity, notes)
  }

  // Handle notes change
  const handleNotesChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newNotes = e.target.value
    setNotes(newNotes)

    // Update all symptom logs for this date with the new notes
    symptoms.forEach((symptom) => {
      const severity = symptomSeverityMap.get(symptom.id) || "none"
      logSymptom(symptom.id, date, severity, newNotes)
    })
  }

  // Get severity button class
  const getSeverityButtonClass = (isActive: boolean, severity: string) => {
    const baseClass = "flex-1 py-1 text-xs rounded-md transition-colors"

    if (!isActive) return cn(baseClass, "bg-gray-100 text-gray-500 hover:bg-gray-200")

    switch (severity) {
      case "mild":
        return cn(baseClass, "bg-yellow-100 text-yellow-800 border-yellow-300")
      case "average":
        return cn(baseClass, "bg-orange-100 text-orange-800 border-orange-300")
      case "severe":
        return cn(baseClass, "bg-red-100 text-red-800 border-red-300")
      default:
        return cn(baseClass, "bg-gray-100 text-gray-500")
    }
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-3">
        {symptoms.map((symptom) => {
          const currentSeverity = symptomSeverityMap.get(symptom.id) || "none"

          return (
            <Card key={symptom.id} className="p-3">
              <div>
                <Label className="text-sm font-medium">{symptom.name}</Label>
              </div>

              <div className="grid grid-cols-4 gap-1">
                <Button
                  type="button"
                  onClick={() => handleSeverityChange(symptom.id, "none")}
                  className={getSeverityButtonClass(currentSeverity === "none", "none")}
                  variant="ghost"
                >
                  None
                </Button>
                <Button
                  type="button"
                  onClick={() => handleSeverityChange(symptom.id, "mild")}
                  className={getSeverityButtonClass(currentSeverity === "mild", "mild")}
                  variant="ghost"
                >
                  Mild
                </Button>
                <Button
                  type="button"
                  onClick={() => handleSeverityChange(symptom.id, "average")}
                  className={getSeverityButtonClass(currentSeverity === "average", "average")}
                  variant="ghost"
                >
                  Medium
                </Button>
                <Button
                  type="button"
                  onClick={() => handleSeverityChange(symptom.id, "severe")}
                  className={getSeverityButtonClass(currentSeverity === "severe", "severe")}
                  variant="ghost"
                >
                  Severe
                </Button>
              </div>
            </Card>
          )
        })}
      </div>

      <div className="mt-4">
        <Label htmlFor="symptom-notes" className="text-sm font-medium">
          Notes
        </Label>
        <Textarea
          id="symptom-notes"
          placeholder="How are you feeling today?"
          value={notes}
          onChange={handleNotesChange}
          className="mt-1 min-h-[80px]"
        />
      </div>
    </div>
  )
}

