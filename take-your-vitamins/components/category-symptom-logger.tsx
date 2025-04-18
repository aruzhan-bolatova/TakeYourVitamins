"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useTracker } from "@/contexts/tracker-context"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Check } from "lucide-react"
import { cn } from "@/lib/utils"

interface CategorySymptomLoggerProps {
    date: string
    onComplete?: () => void
}


// Define symptom categories with their symptoms
const symptomCategories = [
    {
        name: "General",
        symptoms: [
            { id: "fine", name: "Everything is fine", icon: "👍" },
            { id: "acne", name: "Skin issues", icon: "🤡" },
            { id: "fatigue", name: "Fatigue", icon: "🫠" },
            { id: "headache", name: "Headache", icon: "🤕" },
            { id: "abdominal-pain", name: "Abdominal Pain", icon: "😣" },
            { id: "dizziness", name: "Dizziness", icon: "😵‍💫" },
        ],
    },
    {
        name: "Mood",
        symptoms: [
            { id: "calm", name: "Calm", icon: "😌" },
            { id: "mood-swings", name: "Mood swings", icon: "🔄" },
            { id: "happy", name: "Happy", icon: "😊" },
            { id: "energetic", name: "Energetic", icon: "⚡" },
            { id: "irritated", name: "Irritated", icon: "🥴" },
            { id: "depressed", name: "Depressed", icon: "😓" },
            { id: "low-energy", name: "Low energy", icon: "🥱" },
            { id: "anxious", name: "Anxious", icon: "😰" },
        ],
    },
    {
        name: "Sleep",
        symptoms: [
            { id: "insomnia", name: "Insomnia", icon: "😳" },
            { id: "good-sleep", name: "Good sleep", icon: "😴" },
            { id: "restless", name: "Restless", icon: "🔄" },
            { id: "tired", name: "Tired", icon: "🥱" },
        ],
    },
    {
        name: "Digestive",
        symptoms: [
            { id: "bloating", name: "Bloating", icon: "🎈" },
            { id: "nausea", name: "Nausea", icon: "🤢" },
            { id: "constipation", name: "Constipation", icon: "⏸️" },
            { id: "diarrhea", name: "Diarrhea", icon: "⏩" },
        ],
    },
    {
        name: "Appetite",
        symptoms: [
            { id: "low", name: "Low", icon: "🫢" },
            { id: "normal", name: "Normal", icon: "🍽️" },
            { id: "high", name: "High", icon: "🍔" },

        ]
    },
    {
        name: "Physical Activity",
        symptoms: [
            { id: "no-activity", name: "Didn't exercise", icon: "⭕️" },
            { id: "yoga", name: "Yoga", icon: "🧘‍♀️" },
            { id: "gym", name: "Gym", icon: "🏋️" },
            { id: "swimming", name: "Swimming", icon: "🏊‍♀️" },
            { id: "running", name: "Running", icon: "🏃" },
            { id: "cycling", name: "Cycling", icon: "🚴‍♀️" },
            { id: "team-sports", name: "Team Sports", icon: "⛹️‍♀️" },
            { id: "dancing", name: "Aerobics/Dancing", icon: "💃" },
        ]
    }
]

export function CategorySymptomLogger({ date, onComplete }: CategorySymptomLoggerProps) {
    const { symptomLogs, logSymptom, getSymptomLogsForDate } = useTracker()
    const [notes, setNotes] = useState("")
    const [selectedSymptoms, setSelectedSymptoms] = useState<Record<string, boolean>>({})

    // Get existing logs for this date
    const logsForDate = getSymptomLogsForDate(date)

    // Find notes for this date
    const existingNotes = logsForDate.find((log) => log.notes)?.notes || ""

    // Set initial state from existing logs
    useEffect(() => {
        const initialSelected: Record<string, boolean> = {}

        // Initialize all symptoms as unselected
        symptomCategories.forEach((category) => {
            category.symptoms.forEach((symptom) => {
                initialSelected[symptom.id] = false
            })
        })

        // Mark symptoms as selected if they exist in logs with severity not "none"
        logsForDate.forEach((log) => {
            if (log.severity !== "none") {
                initialSelected[log.symptomId] = true
            }
        })

        setSelectedSymptoms(initialSelected)
        setNotes(existingNotes)

        // Only run this effect when the date or logsForDate changes
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [date, logsForDate.length, existingNotes])

    // Update the toggleSymptom function to avoid calling logSymptom during render
    const toggleSymptom = (symptomId: string) => {
        const newState = !selectedSymptoms[symptomId]

        // Update local state
        setSelectedSymptoms((prev) => ({
            ...prev,
            [symptomId]: newState,
        }))

        // Log the symptom with appropriate severity
        logSymptom(
            symptomId,
            date,
            newState ? "average" : "none", // Use "average" as default severity when selected
            notes,
        )
    }

    // Handle notes change
    const handleNotesChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const newNotes = e.target.value
        setNotes(newNotes)

        // Update all selected symptom logs with the new notes
        Object.entries(selectedSymptoms).forEach(([symptomId, isSelected]) => {
            if (isSelected) {
                logSymptom(symptomId, date, "average", newNotes)
            }
        })
    }

    // Handle form submission
    const handleSubmit = () => {
        // Call the onComplete callback to close the dialog
        if (onComplete) {
            onComplete()
        }
    }

    return (
        <div className="space-y-6 max-h-[60vh] overflow-y-auto pr-2">
            {symptomCategories.map((category) => (
                <div key={category.name} className="space-y-3">
                    <h3 className="text-lg font-semibold">{category.name}</h3>
                    <div className="grid grid-cols-4 gap-3">
                        {category.symptoms.map((symptom) => (
                            <button
                                key={symptom.id}
                                type="button"
                                onClick={() => toggleSymptom(symptom.id)}
                                className="flex flex-col items-center"
                            >
                                <div
                                    className={cn(
                                        "relative w-16 h-16 rounded-full flex items-center justify-center text-2xl",
                                        category.name === "General"
                                            ? "bg-purple-500"
                                            : category.name === "Mood"
                                                ? "bg-orange-300"
                                                : category.name === "Sleep"
                                                    ? "bg-blue-400"
                                                    : category.name === "Physical Activity"
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

