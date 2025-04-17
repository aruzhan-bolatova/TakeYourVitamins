"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { AlertCircle } from "lucide-react"
import type { Supplement } from "@/lib/types"
import { DatePicker } from "@/components/date-picker"
import { searchSupplements } from "@/lib/supplements"
import { useTracker } from "@/contexts/tracker-context"

export default function AddSupplementPage() {
  const router = useRouter()
  const { addTrackedSupplement, checkInteractions } = useTracker()
  const [supplements, setSupplements] = useState<Supplement[]>([])
  const [selectedSupplement, setSelectedSupplement] = useState<string>("")
  const [dosage, setDosage] = useState<string>("")
  const [frequency, setFrequency] = useState<string>("daily")
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);
  const [notes, setNotes] = useState<string>("")
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [error, setError] = useState<string>("")
  const [interactionWarnings, setInteractionWarnings] = useState<string[]>([])

  useEffect(() => {
    // Fetch all supplements for the dropdown
    const fetchSupplements = async () => {
      try {
        const results = await searchSupplements("")
        setSupplements(results)
      } catch (error) {
        console.error("Failed to fetch supplements:", error)
      }
    }

    fetchSupplements()
  }, [])

  // Check for interactions when a supplement is selected
  useEffect(() => {
    if (!selectedSupplement) {
      setInteractionWarnings([])
      return
    }

    const checkForInteractions = async () => {
      try {
        const warnings = await checkInteractions(selectedSupplement)
        setInteractionWarnings(warnings)
      } catch (error) {
        console.error("Failed to check interactions:", error)
      }
    }

    checkForInteractions()
  }, [selectedSupplement, checkInteractions])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError("")

    try {
      if (!startDate) {
        console.error("Start date is required!");
        return;
      }      
      const { success, warnings } = await addTrackedSupplement({
        supplementId: selectedSupplement,
        dosage,
        frequency,
        startDate: startDate.toISOString(),
        endDate: endDate ? endDate.toISOString() : undefined,
        notes,
      })

      if (success) {
        router.push("/dashboard/tracker")
      } else {
        setError("Failed to add supplement")
      }
    } catch (error: any) {
      setError(error.message || "Something went wrong. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Add Supplement to Tracker</CardTitle>
          <CardDescription>
            Track a new supplement you're taking to monitor interactions and maintain your regimen
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {interactionWarnings.length > 0 && (
              <Alert className="bg-amber-50 text-amber-800 border-amber-200">
                <AlertCircle className="h-4 w-4 text-amber-800" />
                <AlertTitle>Potential Interactions Detected</AlertTitle>
                <AlertDescription>
                  <ul className="list-disc pl-5 mt-2 space-y-1">
                    {interactionWarnings.map((warning, index) => (
                      <li key={index}>{warning}</li>
                    ))}
                  </ul>
                </AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="supplement">Supplement</Label>
              <Select value={selectedSupplement} onValueChange={setSelectedSupplement} required>
                <SelectTrigger>
                  <SelectValue placeholder="Select a supplement" />
                </SelectTrigger>
                <SelectContent>
                  {supplements.map((supplement) => (
                    <SelectItem key={supplement.id} value={supplement.id}>
                      {supplement.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="dosage">Dosage</Label>
              <Input
                id="dosage"
                value={dosage}
                onChange={(e) => setDosage(e.target.value)}
                placeholder="e.g., 1000mg, 2 tablets"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="frequency">Frequency</Label>
              <Select value={frequency} onValueChange={setFrequency} required>
                <SelectTrigger>
                  <SelectValue placeholder="Select frequency" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="daily">Once daily</SelectItem>
                  <SelectItem value="twice_daily">Twice daily</SelectItem>
                  <SelectItem value="three_times_daily">Three times daily</SelectItem>
                  <SelectItem value="weekly">Weekly</SelectItem>
                  <SelectItem value="as_needed">As needed</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Start Date</Label>
                <DatePicker date={startDate} setDate={setStartDate} />
              </div>
              <div className="space-y-2">
                <Label>End Date (Optional)</Label>
                <DatePicker date={endDate} setDate={setEndDate} />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="notes">Notes (Optional)</Label>
              <Textarea
                id="notes"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Any additional information about your supplement regimen"
                rows={3}
              />
            </div>
          </form>
        </CardContent>
        <CardFooter className="flex justify-between">
          <Button variant="outline" onClick={() => router.back()}>
            Cancel
          </Button>
          <Button type="submit" disabled={isLoading} onClick={handleSubmit}>
            {isLoading ? "Adding..." : "Add Supplement"}
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}

