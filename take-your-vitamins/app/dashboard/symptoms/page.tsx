"use client"

import { useState, useEffect } from "react"
import { format } from "date-fns"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Moon, Activity } from "lucide-react"
import { useTracker } from "@/contexts/tracker-context"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { CategorySymptomLogger } from "@/components/category-symptom-logger"

export default function SymptomsPage() {
    const [selectedDate, setSelectedDate] = useState<Date>(new Date())
    const { symptomLogs, getSymptomLogsForDate } = useTracker()
    const [datesWithSymptoms, setDatesWithSymptoms] = useState<Date[]>([])

    // Dialog open states
    const [symptomsDialogOpen, setSymptomsDialogOpen] = useState(false)

    // Format date for display
    const formattedDate = format(selectedDate, "EEEE, MMMM d, yyyy")

    // Get date string for the selected date
    const dateString = format(selectedDate, "yyyy-MM-dd")

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
                                    <Button className="flex items-center gap-2">
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
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Symptoms Summary</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <SymptomSummary date={dateString} />
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}

// Enhanced component for symptom summary
function SymptomSummary({ date }: { date: string }) {
    const { getSymptomLogsForDate, symptoms } = useTracker()
    const logsForDate = getSymptomLogsForDate(date)

    // Get active symptoms (severity not "none")
    const activeSymptomLogs = logsForDate.filter((log) => log.severity !== "none")

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
    const symptomsByCategory: Record<string, Array<(typeof symptoms)[0]>> = {}

    // Initialize categories
    categories.forEach((category) => {
        symptomsByCategory[category.id] = []
    })

    // Group active symptoms by their categories
    activeSymptomLogs.forEach((log) => {
        const symptom = symptoms.find((s) => s.id === log.symptomId)
        if (symptom && symptom.category) {
            if (!symptomsByCategory[symptom.category]) {
                symptomsByCategory[symptom.category] = []
            }
            symptomsByCategory[symptom.category].push(symptom)
        }
    })

    // Get notes
    const notes = activeSymptomLogs.find((log) => log.notes)?.notes || ""

    return (
        <div className="space-y-2">
            {categories.map((category) => {
                const categorySymptoms = symptomsByCategory[category.id]

                // Skip empty categories
                if (categorySymptoms.length === 0) return null

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

            {notes && (
                <div className="mt-6 bg-gray-50 rounded-lg border border-gray-200 p-4">
                    <div className="flex items-center gap-2 mb-2">
                        <span className="text-xl">📝</span>
                        <h3 className="font-medium">Notes</h3>
                    </div>
                    <p className="text-gray-700 italic">{notes}</p>
                </div>
            )}
        </div>
    )
}

