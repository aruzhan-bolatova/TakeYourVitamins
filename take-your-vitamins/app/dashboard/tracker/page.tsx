"use client"

import { useTracker } from "@/contexts/tracker-context"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Calendar } from "@/components/ui/calendar"
import { Pill, Plus, Search, Calendar as CalendarIcon, AlertTriangle, Clock, Activity, ArrowUpRight } from "lucide-react"
import { TrackedSupplementsList } from "@/components/tracked-supplements-list"
import { format } from "date-fns"

export default function TrackerPage() {
  const { trackedSupplements, intakeLogs } = useTracker()
  const today = new Date()

  // Count supplements taken today
  const takenToday = intakeLogs.filter(log => {
    const logDate = new Date(log.timestamp).toISOString().split('T')[0]
    const todayDate = today.toISOString().split('T')[0]
    return logDate === todayDate && log.taken
  }).length

  // Get upcoming supplement times
  const getTimeString = (hour: number, minute: number) => {
    return `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 p-6 rounded-lg shadow-lg text-white">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight flex items-center">
              <Pill className="mr-2 h-6 w-6" /> Supplement Tracker
            </h1>
            <p className="mt-2 opacity-90">
              Track, manage, and optimize your supplement regimen
            </p>
          </div>
          <Button asChild variant="secondary" className="bg-white text-purple-700 hover:bg-gray-100">
            <Link href="/dashboard/tracker/add">
              <Plus className="mr-2 h-4 w-4" /> Add Supplement
            </Link>
          </Button>
        </div>
      </div>
      
      {/* Main content */}
      <div className="grid gap-6 md:grid-cols-3">
        {/* Tracking summary card */}
        <Card className="md:col-span-1">
          <CardHeader className="bg-slate-50 dark:bg-slate-900 rounded-t-lg pb-2">
            <CardTitle className="flex items-center text-lg">
              <Activity className="mr-2 h-5 w-5 text-purple-600" />
              Tracking Summary
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Supplements tracked:</span>
                <Badge variant="outline" className="font-medium text-purple-600">
                  {trackedSupplements.length}
                </Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Taken today:</span>
                <Badge variant="outline" className="font-medium text-green-600">
                  {takenToday} / {trackedSupplements.length}
                </Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Next scheduled:</span>
                <Badge variant="outline" className="font-medium text-blue-600">
                  {trackedSupplements.length > 0 ? getTimeString(12, 0) : "None"}
                </Badge>
              </div>
            </div>
          </CardContent>
          <CardFooter className="pt-0">
            <Button variant="outline" asChild className="w-full">
              <Link href="/dashboard/tracker/log" className="flex items-center justify-center">
                <CalendarIcon className="mr-2 h-4 w-4" /> 
                View Daily Log
                <ArrowUpRight className="ml-2 h-3 w-3" />
              </Link>
            </Button>
          </CardFooter>
        </Card>

        {/* Weekly schedule card */}
        <Card className="md:col-span-2">
          <CardHeader className="bg-slate-50 dark:bg-slate-900 rounded-t-lg pb-2">
            <CardTitle className="flex items-center text-lg">
              <Clock className="mr-2 h-5 w-5 text-blue-600" />
              Weekly Schedule
            </CardTitle>
            <CardDescription>
              Your supplement schedule for the week
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="grid grid-cols-7 gap-2 text-center mb-2">
              {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((day) => (
                <div key={day} className="font-medium text-sm">{day}</div>
              ))}
            </div>
            <div className="grid grid-cols-7 gap-2">
              {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((day) => (
                <div key={day} className="border rounded-md p-2 h-28 text-xs">
                  <div className="mb-1 bg-orange-100 text-orange-800 rounded px-1 py-0.5 text-xs font-medium">
                    Morning
                  </div>
                  {day === "Mon" || day === "Wed" || day === "Fri" ? (
                    <div className="text-xs">Vitamin D, B Complex</div>
                  ) : day === "Tue" || day === "Thu" ? (
                    <div className="text-xs">Omega-3, Zinc</div>
                  ) : (
                    <div className="text-xs text-gray-400 italic">None</div>
                  )}
                  
                  <div className="mt-2 bg-blue-100 text-blue-800 rounded px-1 py-0.5 text-xs font-medium">
                    Evening
                  </div>
                  {day === "Mon" || day === "Wed" || day === "Fri" || day === "Sun" ? (
                    <div className="text-xs">Magnesium, Calcium</div>
                  ) : (
                    <div className="text-xs text-gray-400 italic">None</div>
                  )}
                </div>
              ))}
            </div>
            <div className="mt-4 text-center text-sm text-muted-foreground">
              <Link href="/dashboard/tracker/log" className="text-blue-600 hover:underline flex items-center justify-center">
                <Search className="h-3 w-3 mr-1" /> View detailed schedule
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Potential interactions alerts */}
        <Card>
          <CardHeader className="bg-slate-50 dark:bg-slate-900 rounded-t-lg pb-2">
            <CardTitle className="flex items-center text-lg">
              <AlertTriangle className="mr-2 h-5 w-5 text-amber-500" />
              Potential Interactions
            </CardTitle>
            <CardDescription>
              Supplements that may interact with each other
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-6">
            {trackedSupplements.length > 0 ? (
              <div className="space-y-4">
                <div className="flex items-start space-x-4 p-3 bg-amber-50 border border-amber-100 rounded-md">
                  <div className="mt-0.5">
                    <AlertTriangle className="h-5 w-5 text-amber-500" />
                  </div>
                  <div>
                    <h4 className="font-medium text-sm">Calcium & Magnesium</h4>
                    <p className="text-xs text-slate-600 mt-1">
                      These supplements may compete for absorption. Consider taking them at different times.
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4 p-3 bg-amber-50 border border-amber-100 rounded-md">
                  <div className="mt-0.5">
                    <AlertTriangle className="h-5 w-5 text-amber-500" />
                  </div>
                  <div>
                    <h4 className="font-medium text-sm">Iron & Zinc</h4>
                    <p className="text-xs text-slate-600 mt-1">
                      High doses of these minerals can interfere with each other's absorption. Space them 2 hours apart.
                    </p>
                  </div>
                </div>
                
                <Button variant="outline" size="sm" className="w-full mt-2">
                  <Activity className="h-4 w-4 mr-2" />
                  View All Interactions
                </Button>
              </div>
            ) : (
              <div className="text-center py-6">
                <div className="rounded-full bg-amber-100 p-3 w-12 h-12 mx-auto mb-3 flex items-center justify-center">
                  <AlertTriangle className="h-6 w-6 text-amber-500" />
                </div>
                <p className="text-sm text-muted-foreground">
                  No supplements tracked yet to check for interactions
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Supplements list */}
        <div className="md:col-span-3">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Pill className="mr-2 h-5 w-5 text-purple-600" /> Your Tracked Supplements
          </h2>
          {trackedSupplements.length > 0 ? (
            <TrackedSupplementsList supplements={trackedSupplements} />
          ) : (
            <div className="rounded-lg border border-dashed p-8 text-center bg-slate-50 dark:bg-slate-900">
              <h3 className="text-lg font-medium">No supplements tracked yet</h3>
              <p className="mt-2 text-muted-foreground">
                Start tracking your supplements to get personalized recommendations and interaction warnings.
              </p>
              <Button asChild className="mt-4 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700">
                <Link href="/dashboard/tracker/add">
                  <Plus className="mr-2 h-4 w-4" /> Add Your First Supplement
                </Link>
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

