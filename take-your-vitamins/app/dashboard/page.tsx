// "use client"

// import { useState, useEffect } from "react"
// import { useAuth } from "@/contexts/auth-context"
// import { useTracker, type TrackedSupplement } from "@/contexts/tracker-context"
// import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
// import { Button } from "@/components/ui/button"
// import Link from "next/link"
// import { Pill, Search, FileDown, TrendingUp, Activity } from "lucide-react"
// import { format, startOfWeek, addDays, subDays } from "date-fns"
// import { SymptomLogger } from "@/components/symptom-logger"

// export default function DashboardPage() {
//     const { user } = useAuth()
//     const { trackedSupplements, intakeLogs, logIntake, getIntakeLogsForDate } = useTracker()

//     const [selectedDate, setSelectedDate] = useState(new Date())
//     const [weekStartDate, setWeekStartDate] = useState(startOfWeek(new Date(), { weekStartsOn: 1 }))

//     // Calculate streak and progress
//     const [streak, setStreak] = useState(0)
//     const [improvement, setImprovement] = useState(0)
//     const [daysToNextAchievement, setDaysToNextAchievement] = useState(0)

//     useEffect(() => {
//         if (trackedSupplements.length === 0) return

//         // Calculate current streak
//         let currentStreak = 0
//         let currentDate = subDays(new Date(), 1) // Start from yesterday
//         let allTaken = true

//         while (allTaken) {
//             const dateStr = format(currentDate, "yyyy-MM-dd")
//             const logs = getIntakeLogsForDate(dateStr)

//             // Check if all supplements were taken on this day
//             const allSupplementsTaken = trackedSupplements.every((supplement) => {
//                 return logs.some((log) => log.trackedSupplementId === supplement.id && log.taken)
//             })

//             if (allSupplementsTaken) {
//                 currentStreak++
//                 currentDate = subDays(currentDate, 1)
//             } else {
//                 allTaken = false
//             }
//         }

//         setStreak(currentStreak)

//         // Calculate days to next achievement (10-day streak)
//         const nextAchievement = 10
//         setDaysToNextAchievement(Math.max(0, nextAchievement - currentStreak))

//         // Calculate improvement (mock data for now)
//         setImprovement(15)
//     }, [trackedSupplements, getIntakeLogsForDate])

//     // Generate weekdays for the header
//     const weekdays = ["M", "T", "W", "T", "F", "S", "S"]

//     // Handle supplement intake logging
//     const handleLogIntake = (supplement: TrackedSupplement, dayIndex: number) => {
//         const date = addDays(weekStartDate, dayIndex)
//         const dateStr = format(date, "yyyy-MM-dd")

//         // Check if already logged
//         const logs = getIntakeLogsForDate(dateStr)
//         const existingLog = logs.find((log) => log.trackedSupplementId === supplement.id)

//         // Toggle the taken status
//         logIntake(supplement.id, existingLog ? !existingLog.taken : true, dateStr)
//     }

//     // Check if a supplement was taken on a specific day
//     const wasSupplementTaken = (supplement: TrackedSupplement, dayIndex: number) => {
//         const date = addDays(weekStartDate, dayIndex)
//         const dateStr = format(date, "yyyy-MM-dd")

//         const logs = getIntakeLogsForDate(dateStr)
//         const log = logs.find((log) => log.trackedSupplementId === supplement.id)

//         return log?.taken || false
//     }

//     return (
//         <div className="space-y-6">
//             <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>

//             <div className="grid gap-5 md:grid-cols-3">
//                 {/* Daily Supplement Log */}
//                 <Card >
//                     <CardHeader>
//                         <CardTitle>Daily Supplement Log</CardTitle>
//                     </CardHeader>
//                     <CardContent>
//                         {trackedSupplements.length > 0 ? (
//                             <div className="space-y-6">
//                                 {trackedSupplements.map((supplement) => (
//                                     <div key={supplement.id} className="space-y-2">
//                                         <h3 className="font-medium">{supplement.supplement.name}</h3>
//                                         <div className="flex justify-between">
//                                             {weekdays.map((day, index) => (
//                                                 <div key={index} className="flex flex-col items-center">
//                                                     <button
//                                                         onClick={() => handleLogIntake(supplement, index)}
//                                                         className={`w-8 h-8 rounded-full border-2 flex items-center justify-center transition-colors ${wasSupplementTaken(supplement, index)
//                                                             ? "bg-green-500 border-green-600 text-white"
//                                                             : "bg-background border-gray-300 hover:border-gray-400"
//                                                             }`}
//                                                         aria-label={`${wasSupplementTaken(supplement, index) ? "Taken" : "Not taken"} on ${format(addDays(weekStartDate, index), "EEEE")}`}
//                                                     >
//                                                         {wasSupplementTaken(supplement, index) ? "✓" : ""}
//                                                     </button>
//                                                     <span className="text-xs mt-1">{day}</span>
//                                                 </div>
//                                             ))}
//                                         </div>
//                                     </div>
//                                 ))}
//                             </div>
//                         ) : (
//                             <div className="text-center py-6">
//                                 <p className="text-muted-foreground">No supplements being tracked.</p>
//                                 <Button className="mt-2" asChild>
//                                     <Link href="/dashboard/tracker/add">Add a supplement</Link>
//                                 </Button>
//                             </div>
//                         )}
//                     </CardContent>
//                 </Card>

//                 {/* Daily Symptom Log */}
//                 <Card>
//                     <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
//                         <CardTitle>Daily Symptom Log</CardTitle>
//                         <Button variant="ghost" size="sm" asChild>
//                             <Link href="/dashboard/symptoms" className="text-xs flex items-center">
//                                 <Activity className="mr-1 h-4 w-4" />
//                                 Full Tracker
//                             </Link>
//                         </Button>
//                     </CardHeader>
//                     <CardContent>
//                         <SymptomLogger date={format(selectedDate, "yyyy-MM-dd")} />
//                     </CardContent>
//                 </Card>

//                 {/* Quick Actions */}
//                 <Card >
//                     <CardHeader>
//                         <CardTitle>Quick Actions</CardTitle>
//                     </CardHeader>
//                     <CardContent className="space-y-4">
//                         <Button asChild className="w-full justify-start" variant="outline">
//                             <Link href="/dashboard/tracker">
//                                 <Pill className="mr-2 h-4 w-4" />
//                                 View Tracked Supplements
//                             </Link>
//                         </Button>
//                         <Button asChild className="w-full justify-start" variant="outline">
//                             <Link href="/dashboard/tracker/add">
//                                 <Pill className="mr-2 h-4 w-4" />
//                                 Add New Supplement
//                             </Link>
//                         </Button>
//                         <Button asChild className="w-full justify-start" variant="outline">
//                             <Link href="/dashboard/symptoms">
//                                 <Activity className="mr-2 h-4 w-4" />
//                                 Symptom Tracker
//                             </Link>
//                         </Button>
//                         <Button asChild className="w-full justify-start" variant="outline">
//                             <Link href="/">
//                                 <Search className="mr-2 h-4 w-4" />
//                                 Search Supplements
//                             </Link>
//                         </Button>
//                         <Button asChild className="w-full justify-start" variant="outline">
//                             <Link
//                                 href="#"
//                                 onClick={(e) => {
//                                     e.preventDefault()
//                                     alert("Export feature coming soon!")
//                                 }}
//                             >
//                                 <FileDown className="mr-2 h-4 w-4" />
//                                 Export Progress
//                             </Link>
//                         </Button>
//                     </CardContent>
//                 </Card>
//             </div>

//             {/* Progress Insights */}
//             <Card className="bg-amber-50 text-amber-800">
//                 <CardContent>
//                     <div className="flex items-center gap-2 mb-4">
//                         <TrendingUp className="h-6 w-6 text-yellow-400" />
//                         <h2 className="text-xl font-bold text-yellow-400">Progress Insights</h2>
//                     </div>

//                     <div className="space-y-2 text-black">
//                         <p>Your supplement consistency has improved by {improvement}% this week!</p>
//                         <p>Streak: {streak} days</p>
//                         {daysToNextAchievement > 0 && <p>Next achievement: 10-day streak ({daysToNextAchievement} days to go)</p>}
//                     </div>
//                 </CardContent>
//             </Card>
//         </div>
//     )
// }


"use client"

import { useState, useEffect } from "react"
import { useAuth } from "@/contexts/auth-context"
import { useTracker, type TrackedSupplement } from "@/contexts/tracker-context"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { Pill, Search, TrendingUp, Activity, Moon, FileDown } from "lucide-react"
import { format, startOfWeek, addDays, subDays } from "date-fns"
import { Calendar } from "@/components/ui/calendar"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { CategorySymptomLogger } from "@/components/category-symptom-logger"

export default function DashboardPage() {
    const { user } = useAuth()
    const { trackedSupplements, intakeLogs, logIntake, getIntakeLogsForDate, symptomLogs } = useTracker()

    const [selectedDate, setSelectedDate] = useState(new Date())
    const [weekStartDate, setWeekStartDate] = useState(startOfWeek(new Date(), { weekStartsOn: 1 }))
    const [datesWithSymptoms, setDatesWithSymptoms] = useState<Date[]>([])

    // Dialog open states
    const [symptomsDialogOpen, setSymptomsDialogOpen] = useState(false)

    // Format date for display
    const formattedDate = format(selectedDate, "EEEE, MMMM d, yyyy")

    // Get date string for the selected date
    const dateString = format(selectedDate, "yyyy-MM-dd")

    // Calculate streak and progress
    const [streak, setStreak] = useState(0)
    const [improvement, setImprovement] = useState(0)
    const [daysToNextAchievement, setDaysToNextAchievement] = useState(0)

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

    useEffect(() => {
        if (trackedSupplements.length === 0) return

        // Calculate current streak
        let currentStreak = 0
        let currentDate = subDays(new Date(), 1) // Start from yesterday
        let allTaken = true

        while (allTaken) {
            const dateStr = format(currentDate, "yyyy-MM-dd")
            const logs = getIntakeLogsForDate(dateStr)

            // Check if all supplements were taken on this day
            const allSupplementsTaken = trackedSupplements.every((supplement) => {
                return logs.some((log) => log.trackedSupplementId === supplement.id && log.taken)
            })

            if (allSupplementsTaken) {
                currentStreak++
                currentDate = subDays(currentDate, 1)
            } else {
                allTaken = false
            }
        }

        setStreak(currentStreak)

        // Calculate days to next achievement (10-day streak)
        const nextAchievement = 10
        setDaysToNextAchievement(Math.max(0, nextAchievement - currentStreak))

        // Calculate improvement (mock data for now)
        setImprovement(15)
    }, [trackedSupplements, getIntakeLogsForDate])

    // Generate weekdays for the header
    const weekdays = ["M", "T", "W", "T", "F", "S", "S"]

    // Handle supplement intake logging
    const handleLogIntake = (supplement: TrackedSupplement, dayIndex: number) => {
        const date = addDays(weekStartDate, dayIndex)
        const dateStr = format(date, "yyyy-MM-dd")

        // Check if already logged
        const logs = getIntakeLogsForDate(dateStr)
        const existingLog = logs.find((log) => log.trackedSupplementId === supplement.id)

        // Toggle the taken status
        logIntake(supplement.id, existingLog ? !existingLog.taken : true, dateStr)
    }

    // Check if a supplement was taken on a specific day
    const wasSupplementTaken = (supplement: TrackedSupplement, dayIndex: number) => {
        const date = addDays(weekStartDate, dayIndex)
        const dateStr = format(date, "yyyy-MM-dd")

        const logs = getIntakeLogsForDate(dateStr)
        const log = logs.find((log) => log.trackedSupplementId === supplement.id)

        return log?.taken || false
    }

    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>

            <div className="grid gap-6 md:grid-cols-3">
                {/* Daily Supplement Log */}
                <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle>Daily Supplement Log</CardTitle>
                        <Button variant="ghost" size="sm" asChild>
                            <Link href="/dashboard/tracker/log" className="text-xs flex items-center">
                                <Activity className="mr-1 h-4 w-4" />
                                Full Tracker
                            </Link>
                        </Button>
                    </CardHeader>
                    <CardContent>
                        {trackedSupplements.length > 0 ? (
                            <div className="space-y-6">
                                {trackedSupplements.map((supplement) => (
                                    <div key={supplement.id} className="space-y-2">
                                        <h3 className="font-medium">{supplement.supplement.name}</h3>
                                        <div className="flex justify-between">
                                            {weekdays.map((day, index) => (
                                                <div key={index} className="flex flex-col items-center">
                                                    <button
                                                        onClick={() => handleLogIntake(supplement, index)}
                                                        className={`w-8 h-8 rounded-full border-2 flex items-center justify-center transition-colors ${wasSupplementTaken(supplement, index)
                                                            ? "bg-green-500 border-green-600 text-white"
                                                            : "bg-background border-gray-300 hover:border-gray-400"
                                                            }`}
                                                        aria-label={`${wasSupplementTaken(supplement, index) ? "Taken" : "Not taken"} on ${format(addDays(weekStartDate, index), "EEEE")}`}
                                                    >
                                                        {wasSupplementTaken(supplement, index) ? "✓" : ""}
                                                    </button>
                                                    <span className="text-xs mt-1">{day}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-6">
                                <p className="text-muted-foreground">No supplements being tracked.</p>
                                <Button className="mt-2" asChild>
                                    <Link href="/dashboard/tracker/add">Add a supplement</Link>
                                </Button>
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Daily Symptom Log Card */}
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle>Daily Symptom Log</CardTitle>
                        <Button variant="ghost" size="sm" asChild>
                            <Link href="/dashboard/symptoms" className="text-xs flex items-center">
                                <Activity className="mr-1 h-4 w-4" />
                                Full Tracker
                            </Link>
                        </Button>
                    </CardHeader>
                    <CardContent>
                        <div className="flex flex-col items-center">
                            <Calendar
                                mode="single"
                                selected={selectedDate}
                                onSelect={(date) => date && setSelectedDate(date)}
                                className="rounded-md border mx-auto mb-4"
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

                            <p className="text-center mb-4">
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
                        </div>
                    </CardContent>
                </Card>

                {/* Quick Actions */}
                <Card >
                    <CardHeader>
                        <CardTitle>Quick Actions</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <Button asChild className="w-full justify-start" variant="outline">
                            <Link href="/dashboard/tracker">
                                <Pill className="mr-2 h-4 w-4" />
                                View Tracked Supplements
                            </Link>
                        </Button>
                        <Button asChild className="w-full justify-start" variant="outline">
                            <Link href="/dashboard/tracker/add">
                                <Pill className="mr-2 h-4 w-4" />
                                Add New Supplement
                            </Link>
                        </Button>
                        <Button asChild className="w-full justify-start" variant="outline">
                            <Link href="/dashboard/symptoms">
                                <Activity className="mr-2 h-4 w-4" />
                                Symptom Tracker
                            </Link>
                        </Button>
                        <Button asChild className="w-full justify-start" variant="outline">
                            <Link href="/">
                                <Search className="mr-2 h-4 w-4" />
                                Search Supplements
                            </Link>
                        </Button>
                        <Button asChild className="w-full justify-start" variant="outline">
                            <Link
                                href="#"
                                onClick={(e) => {
                                    e.preventDefault()
                                    alert("Export feature coming soon!")
                                }}
                            >
                                <FileDown className="mr-2 h-4 w-4" />
                                Export Progress
                            </Link>
                        </Button>
                    </CardContent>
                </Card>
            </div>

            {/* Progress Insights */}
            <Card className="bg-amber-50 text-amber-800">
                <CardContent>
                    <div className="flex items-center gap-2 mb-4">
                        <TrendingUp className="h-6 w-6 text-yellow-400" />
                        <h2 className="text-xl font-bold text-yellow-400">Progress Insights</h2>
                    </div>

                    <div className="space-y-2 text-black">
                        <p>Your supplement consistency has improved by {improvement}% this week!</p>
                        <p>Streak: {streak} days</p>
                        {daysToNextAchievement > 0 && <p>Next achievement: 10-day streak ({daysToNextAchievement} days to go)</p>}
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}

