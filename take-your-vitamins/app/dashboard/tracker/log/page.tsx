"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { format } from "date-fns"
import { useTracker } from "@/contexts/tracker-context"
import { Check, X } from "lucide-react"

export default function DailyLogPage() {
  const [selectedDate, setSelectedDate] = useState<Date>(new Date())
  const { trackedSupplements, intakeLogs, logIntake } = useTracker()

  // Format date for display
  const formattedDate = format(selectedDate, "EEEE, MMMM d, yyyy")

  // Get logs for the selected date
  const dateString = selectedDate.toISOString().split("T")[0]
  const logsForDate = intakeLogs.filter((log) => {
    const logDate = new Date(log.timestamp).toISOString().split("T")[0]
    return logDate === dateString
  })

  // Create a map of tracked supplement IDs to their intake status
  const supplementIntakeMap = new Map()
  logsForDate.forEach((log) => {
    supplementIntakeMap.set(log.trackedSupplementId, log.taken)
  })

  const handleLogIntake = (supplementId: string, taken: boolean) => {
    logIntake(supplementId, taken)
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
              onSelect={(date) => {
                // Only set the date if it's valid and different from current selection
                if (date && date.toString() !== selectedDate.toString()) {
                  // Force create a new Date object to ensure React recognizes the state change
                  const newDate = new Date(date.getTime());
                  setSelectedDate(newDate);
                }
              }}
              className="rounded-md border"
              classNames={{
                day_today: "!bg-transparent !text-orange-500 border border-orange-300 hover:bg-orange-100",
                day_selected: "!bg-primary !text-primary-foreground hover:!bg-primary hover:!text-primary-foreground"
              }}
              disabled={{ before: new Date(2000, 0, 1) }}
              defaultMonth={selectedDate}
              required
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Supplement Log for {formattedDate}</CardTitle>
            <CardDescription>Track which supplements you've taken today</CardDescription>
          </CardHeader>
          <CardContent>
            {trackedSupplements.length === 0 ? (
              <div className="text-center py-6">
                <p className="text-muted-foreground">No supplements being tracked.</p>
                <Button className="mt-2" asChild>
                  <a href="/dashboard/tracker/add">Add a supplement</a>
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {trackedSupplements.map((supplement) => {
                  const isTaken = supplementIntakeMap.get(supplement.id) === true
                  const isLogged = supplementIntakeMap.has(supplement.id)

                  return (
                    <div key={supplement.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <h3 className="font-medium">{supplement.supplement.name}</h3>
                        <p className="text-sm text-muted-foreground">{supplement.dosage}</p>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant={isTaken ? "default" : "outline"}
                          className={isTaken ? "bg-green-600 hover:bg-green-700" : ""}
                          onClick={() => handleLogIntake(supplement.id, true)}
                        >
                          <Check className="h-4 w-4 mr-1" />
                          Taken
                        </Button>
                        <Button
                          size="sm"
                          variant={isLogged && !isTaken ? "default" : "outline"}
                          className={isLogged && !isTaken ? "bg-red-600 hover:bg-red-700" : ""}
                          onClick={() => handleLogIntake(supplement.id, false)}
                        >
                          <X className="h-4 w-4 mr-1" />
                          Missed
                        </Button>
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

