"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { useTracker } from "@/contexts/tracker-context"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { AlertCircle, AlertTriangle } from "lucide-react"
import type { Supplement } from "@/lib/types"
import { DatePicker } from "@/components/date-picker"
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select"
import { getAllSupplements, getAutocompleteSuggestions, AutocompleteSuggestion, getSupplementById } from "@/lib/supplements"

export default function AddSupplementPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const supplementIdFromUrl = searchParams.get('supplement')
  
  const { addTrackedSupplement, checkInteractions, trackedSupplements } = useTracker()
  const [supplements, setSupplements] = useState<Supplement[]>([])
  const [selectedSupplement, setSelectedSupplement] = useState<string>("")
  const [selectedSupplementName, setSelectedSupplementName] = useState<string>("")
  const [dosage, setDosage] = useState<string>("")
  const [unit, setUnit] = useState<string>("mg")
  const [frequency, setFrequency] = useState<string>("daily")
  const [startDate, setStartDate] = useState<Date | null>(new Date())
  const [endDate, setEndDate] = useState<Date | null>(null)
  const [notes, setNotes] = useState<string>("")
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [error, setError] = useState<string>("")
  const [isAlreadyTracked, setIsAlreadyTracked] = useState<boolean>(false)
  const [interactionWarnings, setInteractionWarnings] = useState<string[]>([])
  const [autocompleteOptions, setAutocompleteOptions] = useState<AutocompleteSuggestion[]>([])

  // Check if supplement from URL is already tracked and auto-fill form
  useEffect(() => {
    if (!supplementIdFromUrl) return;
    
    const loadSupplementData = async () => {
      try {
        // Check if already tracked
        const alreadyTracked = trackedSupplements.find(
          supplement => supplement.supplementId === supplementIdFromUrl
        );
        
        if (alreadyTracked) {
          setIsAlreadyTracked(true);
          return;
        }
        
        // If not tracked, get supplement details and auto-fill form
        const supplementDetails = await getSupplementById(supplementIdFromUrl);
        if (supplementDetails) {
          setSelectedSupplement(supplementDetails._id);
          setSelectedSupplementName(supplementDetails.name);
          
          // Try to extract dosage from recommended dosage if available
          const dosageMatch = supplementDetails.intakePractices?.dosage?.match(/(\d+)/);
          if (dosageMatch && dosageMatch[1]) {
            setDosage(dosageMatch[1]);
          }
          
          // Set default unit based on common pattern in the dosage text
          if (supplementDetails.intakePractices?.dosage?.toLowerCase().includes('mg')) {
            setUnit('mg');
          } else if (supplementDetails.intakePractices?.dosage?.toLowerCase().includes('g')) {
            setUnit('g');
          } else if (supplementDetails.intakePractices?.dosage?.toLowerCase().includes('mcg')) {
            setUnit('mcg');
          } else if (supplementDetails.intakePractices?.dosage?.toLowerCase().includes('iu')) {
            setUnit('IU');
          }
          
          // Add recommended intake instructions to notes
          let autoNotes = '';
          if (supplementDetails.intakePractices?.timing) {
            autoNotes += `Recommended timing: ${supplementDetails.intakePractices.timing}\n`;
          }
          if (supplementDetails.intakePractices?.specialInstructions) {
            autoNotes += `Special instructions: ${supplementDetails.intakePractices.specialInstructions}`;
          }
          setNotes(autoNotes.trim());
        }
      } catch (error) {
        console.error("Failed to load supplement details:", error);
      }
    };
    
    loadSupplementData();
  }, [supplementIdFromUrl, trackedSupplements]);

  useEffect(() => {
    const fetchSupplements = async () => {
      try {
        const results = await getAllSupplements()
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
      if (!selectedSupplement) {
        setError("Please select a supplement.")
        setIsLoading(false)
        return
      }

      if (!startDate) {
        setError("Start date is required!")
        setIsLoading(false)
        return
      }      

      if (!dosage) {
        setError("Dosage is required!")
        setIsLoading(false)
        return
      }

      if (endDate && startDate && endDate < startDate) {
        setError("End date cannot be earlier than start date.")
        setIsLoading(false)
        return
      }
      
      const { success, warnings } = await addTrackedSupplement({
        supplementId: selectedSupplement,
        supplementName: selectedSupplementName,
        dosage,
        unit,
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

  // If the supplement is already tracked, show an alert instead of the form
  if (isAlreadyTracked) {
    return (
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle>Add Supplement to Tracker</CardTitle>
          </CardHeader>
          <CardContent>
            <Alert className="bg-blue-50 text-blue-800 border-blue-200 mb-6">
              <AlertTriangle className="h-4 w-4 text-blue-800" />
              <AlertTitle>Supplement Already Tracked</AlertTitle>
              <AlertDescription>
                You are already tracking this supplement. You can view and edit your tracked supplements on the tracker page.
              </AlertDescription>
            </Alert>
            <div className="flex justify-between">
              <Button variant="outline" onClick={() => router.back()}>
                Go Back
              </Button>
              <Button onClick={() => router.push('/dashboard/tracker')}>
                View Tracked Supplements
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
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

            <div className="space-y-2 relative">
              <Label htmlFor="supplement-search">Supplement</Label>
              <Input
                id="supplement-search"
                value={selectedSupplementName}
                onChange={async (e) => {
                  const value = e.target.value
                  setSelectedSupplement("") // clear current selection
                  setSelectedSupplementName(value)
                  if (value.length > 0) {
                    const suggestions = await getAutocompleteSuggestions(value)
                    setAutocompleteOptions(suggestions)
                  } else {
                    setAutocompleteOptions([])
                  }
                }}
                placeholder="Start typing to search supplements"
                required
              />
              {autocompleteOptions.length > 0 && (
                <div className="absolute z-10 bg-popover text-popover-foreground border rounded w-full max-h-48 overflow-y-auto mt-1">
                  {autocompleteOptions.map((option) => (
                    <div
                      key={option.id}
                      className="px-3 py-2 hover:bg-accent hover:text-accent-foreground cursor-pointer"
                      onClick={() => {
                        setSelectedSupplement(option.id)
                        setSelectedSupplementName(option.name)
                        setAutocompleteOptions([])
                      }}
                    >
                      {option.name}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="dosage">Dosage</Label>
                <Input
                  id="dosage"
                  value={dosage}
                  onChange={(e) => setDosage(e.target.value)}
                  placeholder="e.g., 1000"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="unit">Unit</Label>
                <Select value={unit} onValueChange={setUnit} required>
                  <SelectTrigger className="text-foreground">
                    <SelectValue placeholder="Select unit" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="mg">mg (milligram)</SelectItem>
                    <SelectItem value="g">g (gram)</SelectItem>
                    <SelectItem value="mcg">mcg (microgram)</SelectItem>
                    <SelectItem value="ml">ml (milliliter)</SelectItem>
                    <SelectItem value="IU">IU (International Unit)</SelectItem>
                    <SelectItem value="tablet">tablet</SelectItem>
                    <SelectItem value="capsule">capsule</SelectItem>
                    <SelectItem value="drop">drop</SelectItem>
                    <SelectItem value="tsp">tsp (teaspoon)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="frequency">Frequency</Label>
              <Select value={frequency} onValueChange={setFrequency} required>
                <SelectTrigger className="text-foreground">
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
          <Button variant="outline" type="button" onClick={() => router.back()}>
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