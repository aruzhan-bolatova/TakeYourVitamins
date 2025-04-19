"use client"
import Link from "next/link"
import { useTracker } from "@/contexts/tracker-context"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"
import { TrackedSupplementsList } from "@/components/tracked-supplements-list"

export default function TrackerPage() {
  const { trackedSupplements } = useTracker()

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Supplement Tracker</h1>
        <Button asChild>
          <Link href="/dashboard/tracker/add">
            <Plus className="mr-2 h-4 w-4" /> Add Supplement
          </Link>
        </Button>
      </div>

      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Your Tracked Supplements</h2>
        {trackedSupplements.length > 0 ? (
          <TrackedSupplementsList supplements={trackedSupplements} />
        ) : (
          <div className="rounded-lg border border-dashed p-8 text-center">
            <h3 className="text-lg font-medium">No supplements tracked yet</h3>
            <p className="mt-2 text-muted-foreground">
              Start tracking your supplements to get personalized recommendations and interaction warnings.
            </p>
            <Button asChild className="mt-4">
              <Link href="/dashboard/tracker/add">
                <Plus className="mr-2 h-4 w-4" /> Add Your First Supplement
              </Link>
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}

