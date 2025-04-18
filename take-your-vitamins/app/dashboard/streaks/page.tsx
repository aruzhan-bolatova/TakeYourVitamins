"use client"

import { useState, useEffect } from "react"
import { getUserStreaks, Streak } from "@/lib/reports"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { format } from "date-fns"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { AlertCircle, CheckCircle2, Trophy } from "lucide-react"

export default function StreaksPage() {
  const [streaksData, setStreaksData] = useState<Streak[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchStreaks() {
      setLoading(true)
      setError(null)
      try {
        const data = await getUserStreaks()
        if (data) {
          setStreaksData(data.streaks)
        } else {
          throw new Error("No data returned")
        }
      } catch (err) {
        setError("Failed to load streaks. Please try again later.")
        console.error("Error loading streaks:", err)
      } finally {
        setLoading(false)
      }
    }

    fetchStreaks()
  }, [])

  // Format date for display
  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), "PPP")
    } catch (error) {
      return dateString
    }
  }

  // Helper to determine the streak card color based on streak length
  const getStreakColorClass = (streakDays: number) => {
    if (streakDays >= 30) return "bg-green-50 border-green-200 dark:bg-green-950 dark:border-green-800"
    if (streakDays >= 14) return "bg-emerald-50 border-emerald-200 dark:bg-emerald-950 dark:border-emerald-800"
    if (streakDays >= 7) return "bg-blue-50 border-blue-200 dark:bg-blue-950 dark:border-blue-800"
    if (streakDays >= 3) return "bg-purple-50 border-purple-200 dark:bg-purple-950 dark:border-purple-800"
    return ""
  }

  return (
    <div className="container py-6">
      <div className="flex flex-col gap-4">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Your Supplement Streaks</h1>
        </div>

        {loading && (
          <div className="space-y-4">
            <Skeleton className="h-32 w-full" />
            <Skeleton className="h-32 w-full" />
            <Skeleton className="h-32 w-full" />
          </div>
        )}

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {streaksData && streaksData.length === 0 && (
          <Card>
            <CardContent className="pt-6">
              <div className="text-center py-8">
                <p className="text-muted-foreground">No streak data available yet</p>
                <p className="text-sm mt-2">Start tracking your supplements to build streaks!</p>
              </div>
            </CardContent>
          </Card>
        )}

        {streaksData && streaksData.length > 0 && (
          <>
            {/* Streaks Overview Card */}
            <Card>
              <CardHeader>
                <CardTitle>Streaks Overview</CardTitle>
                <CardDescription>Your consistency in taking supplements</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {streaksData.map((streak) => (
                    <Card 
                      key={streak.supplementId} 
                      className={`border ${getStreakColorClass(streak.currentStreak)}`}
                    >
                      <CardContent className="pt-6">
                        <div className="flex flex-col items-center text-center">
                          <div className="flex items-center justify-center w-12 h-12 rounded-full bg-primary/10 mb-4">
                            {streak.currentStreak >= streak.longestStreak && streak.currentStreak > 3 ? (
                              <Trophy className="h-6 w-6 text-primary" />
                            ) : (
                              <CheckCircle2 className="h-6 w-6 text-primary" />
                            )}
                          </div>
                          <h3 className="font-medium text-lg">{streak.supplementName}</h3>
                          <div className="grid grid-cols-2 gap-4 mt-4 w-full">
                            <div className="text-center">
                              <p className="text-xs text-muted-foreground">Current</p>
                              <p className="text-xl font-bold">{streak.currentStreak}</p>
                              <p className="text-xs">{streak.currentStreak === 1 ? 'day' : 'days'}</p>
                            </div>
                            <div className="text-center">
                              <p className="text-xs text-muted-foreground">Best</p>
                              <p className="text-xl font-bold">{streak.longestStreak}</p>
                              <p className="text-xs">{streak.longestStreak === 1 ? 'day' : 'days'}</p>
                            </div>
                          </div>
                          <p className="mt-4 text-sm text-muted-foreground">
                            Last taken: {formatDate(streak.lastTaken)}
                          </p>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Streaks Tips */}
            <Card>
              <CardHeader>
                <CardTitle>Tips to Maintain Your Streaks</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="list-disc pl-5 space-y-2">
                  <li>Set a daily reminder at the same time each day</li>
                  <li>Keep your supplements in a visible location</li>
                  <li>Pair taking supplements with another daily habit like breakfast</li>
                  <li>Use the calendar in the dashboard to track your consistency</li>
                  <li>Celebrate milestones to stay motivated</li>
                </ul>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </div>
  )
} 