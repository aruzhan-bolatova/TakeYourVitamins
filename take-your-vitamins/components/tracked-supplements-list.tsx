"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Pill, Calendar, Clock, Trash2, Check } from "lucide-react"
import { type TrackedSupplement, useTracker } from "@/contexts/tracker-context"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { format } from "date-fns"

interface TrackedSupplementsListProps {
  supplements: TrackedSupplement[]
}

export function TrackedSupplementsList({ supplements }: TrackedSupplementsListProps) {
  const { removeTrackedSupplement, logIntake } = useTracker()
  const [isLogging, setIsLogging] = useState<Record<string, boolean>>({})
  const [isDeleting, setIsDeleting] = useState<Record<string, boolean>>({})

  const handleLogIntake = async (id: string) => {
    setIsLogging((prev) => ({ ...prev, [id]: true }))

    try {
      // Get the current date in YYYY-MM-DD format
      const today = new Date().toISOString().split('T')[0]
      
      // Find the supplement to get its dosage and unit
      const supplement = supplements.find(s => s.id === id)
      if (!supplement) return
      
      // Parse dosage as a number
      const dosageTaken = parseFloat(supplement.dosage)
      if (isNaN(dosageTaken)) return
      
      // Log the intake with current date, dosage, and unit
      await logIntake(id, today, dosageTaken, supplement.unit || "mg")
    } finally {
      setIsLogging((prev) => ({ ...prev, [id]: false }))
    }
  }

  const handleDelete = async (id: string) => {
    setIsDeleting((prev) => ({ ...prev, [id]: true }))

    try {
      await removeTrackedSupplement(id)
    } finally {
      setIsDeleting((prev) => ({ ...prev, [id]: false }))
    }
  }

  return (
    <div className="space-y-4">
      {supplements.map((item) => (
        <Card key={item.id}>
          <CardHeader>
            <div className="flex items-center justify-between flex-wrap gap-2">
              <div className="flex items-center">
                <Pill className="mr-2 h-5 w-5 text-primary" />
                <CardTitle>{item.supplementName}</CardTitle>
              </div>
            </div>
            <CardDescription>
              Started on {format(new Date(item.startDate), "PPP")}
              {item.endDate && ` • Ends on ${format(new Date(item.endDate), "PPP")}`}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex items-center text-sm">
              <Clock className="mr-2 h-4 w-4 text-muted-foreground" />
              <span>Dosage: {item.dosage} {item.unit}</span>
            </div>
            <div className="flex items-center text-sm">
              <Calendar className="mr-2 h-4 w-4 text-muted-foreground" />
              <span>Frequency: {item.frequency.replace("_", " ")}</span>
            </div>
            {item.notes && (
              <div className="mt-2 text-sm text-muted-foreground">
                <p>Notes: {item.notes}</p>
              </div>
            )}
          </CardContent>
          <CardFooter className="flex flex-wrap gap-3 sm:justify-between">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => handleLogIntake(item.id)}
              disabled={isLogging[item.id]}
              className="flex-1 sm:flex-initial"
            >
              <Check className="mr-2 h-4 w-4" />
              {isLogging[item.id] ? "Logging..." : "Log Intake"}
            </Button>
            
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button variant="destructive" size="sm" className="flex-1 sm:flex-initial">
                  <Trash2 className="mr-2 h-4 w-4" />
                  Remove
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                  <AlertDialogDescription>
                    This will remove {item.supplementName} from your tracked supplements. This action cannot be undone.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction onClick={() => handleDelete(item.id)} disabled={isDeleting[item.id]}>
                    {isDeleting[item.id] ? "Removing..." : "Remove"}
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </CardFooter>
        </Card>
      ))}
    </div>
  )
}