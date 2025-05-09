"use client"

import type React from "react"
import { useState, useEffect, useCallback } from "react"
import { useTracker, type Symptom } from "@/contexts/tracker-context"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Check, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

interface CategorySymptomLoggerProps {
  date: string
  onComplete?: () => void
}

// Interface for grouped symptoms by category
interface SymptomCategory {
  id: string
  name: string
  icon: string
  symptoms: Symptom[]
}

export function CategorySymptomLogger({ date, onComplete }: CategorySymptomLoggerProps): React.ReactElement {
  const { logSymptom, getSymptomLogsForDate, symptoms, fetchSymptoms } = useTracker()
  const [notes, setNotes] = useState("")
  const [selectedSymptoms, setSelectedSymptoms] = useState<Record<string, boolean>>({})
  const [logsForDate, setLogsForDate] = useState<any[]>([])
  const [symptomCategories, setSymptomCategories] = useState<SymptomCategory[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Memoize the fetch function to prevent it from being recreated on each render
  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      console.log("Fetching data for CategorySymptomLogger...")

      // Use the symptoms from context if available, otherwise fetch them
      let allSymptoms = symptoms
      if (allSymptoms.length === 0) {
        allSymptoms = await fetchSymptoms()
      }

      console.log("Symptoms fetched:", allSymptoms)

      // Group symptoms by category
      const categoriesMap: Record<string, SymptomCategory> = {}

      allSymptoms.forEach((symptom) => {
        if (symptom.categoryId && symptom.categoryName) {
          if (!categoriesMap[symptom.categoryId]) {
            categoriesMap[symptom.categoryId] = {
              id: symptom.categoryId,
              name: symptom.categoryName,
              icon: symptom.categoryIcon || "❓",
              symptoms: [],
            }
          }

          categoriesMap[symptom.categoryId].symptoms.push(symptom)
        }
      })

      // Convert to array and sort categories
      const categoriesArray = Object.values(categoriesMap)
      console.log("Categories created:", categoriesArray)
      setSymptomCategories(categoriesArray)

      // Fetch logs for this date
      const logs = await getSymptomLogsForDate(date)
      console.log("Logs for date:", logs)
      setLogsForDate(logs)

      // Find notes for this date
      const existingNotes = logs.find((log) => log.notes)?.notes || ""
      setNotes(existingNotes)

      // Initialize selected symptoms
      const initialSelected: Record<string, boolean> = {}

      // Mark symptoms as selected if they exist in logs with severity not "none"
      logs.forEach((log) => {
        if (log.severity !== "none") {
          initialSelected[log.symptom_id] = true
        }
      })

      setSelectedSymptoms(initialSelected)
    } catch (err) {
      console.error("Error fetching data:", err)
      setError("Failed to load symptoms. Please try again.")
    } finally {
      setLoading(false)
    }
  }, [date, fetchSymptoms, getSymptomLogsForDate, symptoms])

  // Fetch symptoms and logs only once when the component mounts or date changes
  useEffect(() => {
    fetchData()
  }, [fetchData])

  // Toggle symptom selection
  const toggleSymptom = async (symptomId: string) => {
    const newState = !selectedSymptoms[symptomId]

    // Update local state
    setSelectedSymptoms((prev) => ({
      ...prev,
      [symptomId]: newState,
    }))

    try {
      // Log the symptom with appropriate severity
      await logSymptom(
        symptomId,
        date,
        newState ? "average" : "none", // Use "average" as default severity when selected, "none" to remove
        notes,
      )
    } catch (err) {
      console.error("Error logging symptom:", err)
      // Revert the state change if the API call fails
      setSelectedSymptoms((prev) => ({
        ...prev,
        [symptomId]: !newState,
      }))
    }
  }

  // Handle notes change
  const handleNotesChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newNotes = e.target.value
    setNotes(newNotes)

    // Update all selected symptom logs with the new notes
    // We'll do this when the user submits instead of on every change
  }

  // Handle form submission
  const handleSubmit = async () => {
    try {
      setLoading(true)
      console.log("Submitting symptom form with selected symptoms:", selectedSymptoms)

      // Get all symptoms to ensure we update everything appropriately
      const allSymptomIds = symptomCategories.flatMap(category => 
        category.symptoms.map(symptom => symptom.id)
      );

      // Create a promise for each symptom update
      const updatePromises = allSymptomIds.map(symptomId => {
        const isSelected = selectedSymptoms[symptomId] || false;
        // For selected symptoms, update with notes
        // For unselected symptoms, ensure they're marked as "none"
        return logSymptom(
          symptomId, 
          date, 
          isSelected ? "average" : "none", 
          isSelected ? notes : ""
        );
      });

      // Wait for all updates to complete
      await Promise.all(updatePromises);
      console.log("All symptom logs updated successfully");

      // Ensure we get the latest logs after updates - force refresh from server
      const updatedLogs = await getSymptomLogsForDate(date, true);
      console.log("Updated logs after submission:", updatedLogs);

      // Call the onComplete callback to close the dialog and refresh the parent component
      if (onComplete) {
        onComplete();
      }
    } catch (err) {
      console.error("Error updating symptoms:", err)
      setError("Failed to update symptoms. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  // If there's an error, show error message with retry button
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-40 space-y-4">
        <p className="text-red-500">{error}</p>
        <Button onClick={fetchData}>Retry</Button>
      </div>
    )
  }

  // If loading, show loading spinner
  if (loading) {
    return (
      <div className="flex items-center justify-center h-40">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <span className="ml-2">Loading symptoms...</span>
      </div>
    )
  }

  // If no symptoms are available, show a message
  if (symptomCategories.length === 0) {
    return (
      <div className="text-center py-8">
        <p>No symptoms available. Please add symptoms to your account.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6 max-h-[60vh] overflow-y-auto pr-2">
      {symptomCategories.map((category) => (
        <div key={category.id} className="space-y-3">
          <h3 className="text-lg font-semibold flex items-center">
            {category.icon && <span className="mr-2">{category.icon}</span>}
            {category.name}
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {category.symptoms.map((symptom) => (
              <button
                key={symptom.id}
                type="button"
                onClick={() => toggleSymptom(symptom.id)}
                className="flex flex-col items-center"
              >
                <div
                  className={cn(
                    "relative w-14 h-14 rounded-full flex items-center justify-center text-xl",
                    category.name.toLowerCase().includes("general")
                      ? "bg-purple-500"
                      : category.name.toLowerCase().includes("mood")
                        ? "bg-orange-300"
                        : category.name.toLowerCase().includes("sleep")
                          ? "bg-blue-400"
                          : category.name.toLowerCase().includes("physical") ||
                              category.name.toLowerCase().includes("activity")
                            ? "bg-green-400"
                            : "bg-yellow-300",
                    "hover:opacity-90 transition-opacity",
                  )}
                >
                  {symptom.icon}
                  {selectedSymptoms[symptom.id] && (
                    <div className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center">
                      <Check className="w-3 h-3" />
                    </div>
                  )}
                </div>
                <span className="text-xs mt-1 text-center">{symptom.name}</span>
              </button>
            ))}
          </div>
        </div>
      ))}

      <div className="space-y-2">
        <Label htmlFor="symptom-notes">Notes</Label>
        <Textarea
          id="symptom-notes"
          placeholder="How are you feeling today?"
          value={notes}
          onChange={handleNotesChange}
          className="min-h-[80px]"
        />
      </div>

      <Button className="w-full bg-pink-500 hover:bg-pink-600 text-white py-3" onClick={handleSubmit}>
        Apply
      </Button>
    </div>
  )
}
