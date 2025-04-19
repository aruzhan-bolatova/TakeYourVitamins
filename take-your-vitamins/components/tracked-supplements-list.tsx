"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Pill, Calendar, Clock, Trash2, Check, Info, Edit, MoreHorizontal, AlertTriangle, Droplets } from "lucide-react"
import { type TrackedSupplement, useTracker, type IntakeLog } from "@/contexts/tracker-context"
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
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { format, isToday } from "date-fns"
import Link from "next/link"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { cn } from "@/lib/utils"

interface TrackedSupplementsListProps {
  supplements: TrackedSupplement[]
}

export function TrackedSupplementsList({ supplements }: TrackedSupplementsListProps) {
  const { removeTrackedSupplement, logIntake, intakeLogs } = useTracker()
  const [isLogging, setIsLogging] = useState<Record<string, boolean>>({})
  const [isDeleting, setIsDeleting] = useState<Record<string, boolean>>({})

  const handleLogIntake = async (id: string) => {
    setIsLogging((prev) => ({ ...prev, [id]: true }))

    try {
      logIntake(id, true)
    } finally {
      setIsLogging((prev) => ({ ...prev, [id]: false }))
    }
  }

  const handleDelete = async (id: string) => {
    setIsDeleting((prev) => ({ ...prev, [id]: true }))

    try {
      removeTrackedSupplement(id)
    } finally {
      setIsDeleting((prev) => ({ ...prev, [id]: false }))
    }
  }

  // Get intake logs for a specific supplement
  const getSupplementIntakeLogs = (supplementId: string): IntakeLog[] => {
    return intakeLogs.filter(log => log.trackedSupplementId === supplementId);
  };

  // Check if supplement was taken today
  const wasTakenToday = (supplementId: string): boolean => {
    const logs = getSupplementIntakeLogs(supplementId);
    return logs.some(log => {
      const logDate = new Date(log.timestamp).toISOString().split("T")[0];
      const today = new Date().toISOString().split("T")[0];
      return logDate === today && log.taken;
    });
  };

  // Group supplements by frequency for better organization
  const getSupplementsByFrequency = () => {
    const result: Record<string, TrackedSupplement[]> = {
      daily: [],
      weekly: [],
      monthly: [],
      other: []
    }
    
    supplements.forEach(supp => {
      if (supp.frequency.includes('daily')) {
        result.daily.push(supp)
      } else if (supp.frequency.includes('weekly')) {
        result.weekly.push(supp)
      } else if (supp.frequency.includes('monthly')) {
        result.monthly.push(supp)
      } else {
        result.other.push(supp)
      }
    })
    
    return result
  }

  const supplementsByFrequency = getSupplementsByFrequency()
  const frequencyLabels = {
    daily: 'Daily',
    weekly: 'Weekly',
    monthly: 'Monthly',
    other: 'Other'
  }

  // Function to render the status badge
  const renderStatusBadge = (item: TrackedSupplement) => {
    const takenToday = wasTakenToday(item.id);
    
    if (takenToday) {
      return (
        <Badge className="bg-green-100 text-green-700 hover:bg-green-200 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800/30">
          <Check className="mr-1 h-3 w-3" /> Taken Today
        </Badge>
      )
    }
    
    return (
      <Badge variant="outline" className="text-orange-600 bg-orange-50 hover:bg-orange-100 border-orange-200 dark:bg-orange-900/20 dark:text-orange-400 dark:border-orange-800/30">
        Pending
      </Badge>
    )
  }

  // Get category icon
  const getCategoryIcon = (category: string) => {
    switch(category.toLowerCase()) {
      case 'vitamin':
        return <Pill className="h-4 w-4 text-blue-500" />;
      case 'mineral':
        return <Droplets className="h-4 w-4 text-blue-500" />;
      default:
        return <Pill className="h-4 w-4 text-blue-500" />;
    }
  };

  return (
    <div className="space-y-8">
      {Object.entries(supplementsByFrequency).map(([freqKey, freqSupplements]) => 
        freqSupplements.length > 0 && (
          <div key={freqKey} className="space-y-4">
            <h3 className="text-lg font-medium flex items-center">
              <Clock className="mr-2 h-4 w-4 text-blue-600" />
              {frequencyLabels[freqKey as keyof typeof frequencyLabels]} Supplements
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {freqSupplements.map((item) => (
                <Card key={item.id} className="border overflow-hidden transition-all hover:shadow-md relative">
                  <div className={cn(
                    "h-1.5 w-full absolute top-0 left-0",
                    wasTakenToday(item.id) 
                      ? "bg-gradient-to-r from-green-400 to-green-600" 
                      : "bg-gradient-to-r from-orange-400 to-orange-600"
                  )} />
                  <CardHeader className="pb-2 pt-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="mr-2 p-1.5 rounded-full bg-slate-100 dark:bg-slate-800">
                          {getCategoryIcon(item.supplement.category)}
                        </div>
                        <CardTitle className="text-lg">{item.supplement.name}</CardTitle>
                      </div>
                      <div className="flex items-center gap-1">
                        {renderStatusBadge(item)}
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon" className="h-8 w-8">
                              <MoreHorizontal className="h-4 w-4" />
                              <span className="sr-only">Open menu</span>
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuLabel>Options</DropdownMenuLabel>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem 
                              onClick={() => handleLogIntake(item.id)}
                              disabled={isLogging[item.id] || wasTakenToday(item.id)}
                              className={!wasTakenToday(item.id) ? "text-green-600 font-medium" : ""}
                            >
                              <Check className="mr-2 h-4 w-4" />
                              {wasTakenToday(item.id) ? "Already Taken" : "Log Intake"}
                            </DropdownMenuItem>
                            <DropdownMenuItem asChild>
                              <Link href={`/dashboard/tracker/edit/${item.id}`}>
                                <Edit className="mr-2 h-4 w-4" />
                                Edit Details
                              </Link>
                            </DropdownMenuItem>
                            <DropdownMenuItem asChild>
                              <Link href={`/dashboard/supplement/${item.supplement.supplementId}`}>
                                <Info className="mr-2 h-4 w-4" />
                                View Info
                              </Link>
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <AlertDialog>
                              <AlertDialogTrigger asChild>
                                <DropdownMenuItem onSelect={(e) => e.preventDefault()} className="text-destructive">
                                  <Trash2 className="mr-2 h-4 w-4" />
                                  Remove
                                </DropdownMenuItem>
                              </AlertDialogTrigger>
                              <AlertDialogContent>
                                <AlertDialogHeader>
                                  <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                                  <AlertDialogDescription>
                                    This will remove {item.supplement.name} from your tracked supplements. This action cannot be undone.
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
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </div>
                    <CardDescription className="mt-1">
                      <Badge variant="outline" className="mr-2 bg-slate-50 dark:bg-slate-900 border-slate-200 dark:border-slate-700">
                        {item.supplement.category}
                      </Badge>
                      {format(new Date(item.startDate), "MMM d, yyyy")}
                      {item.endDate && ` - ${format(new Date(item.endDate), "MMM d, yyyy")}`}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3 pt-2">
                    <div className="grid grid-cols-2 gap-2">
                      <div className="flex items-center text-sm p-2 bg-slate-50 dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800">
                        <TooltipProvider>
                          <Tooltip>
                            <TooltipTrigger>
                              <Clock className="mr-2 h-4 w-4 text-blue-600" />
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>Dosage</p>
                            </TooltipContent>
                          </Tooltip>
                        </TooltipProvider>
                        <span>{item.dosage}</span>
                      </div>
                      <div className="flex items-center text-sm p-2 bg-slate-50 dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800">
                        <TooltipProvider>
                          <Tooltip>
                            <TooltipTrigger>
                              <Calendar className="mr-2 h-4 w-4 text-blue-600" />
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>Frequency</p>
                            </TooltipContent>
                          </Tooltip>
                        </TooltipProvider>
                        <span>{item.frequency.replace("_", " ")}</span>
                      </div>
                    </div>
                    {item.notes && (
                      <div className="text-sm text-muted-foreground p-2 border border-slate-200 dark:border-slate-800 rounded bg-slate-50 dark:bg-slate-900 italic">
                        <p>{item.notes}</p>
                      </div>
                    )}
                  </CardContent>
                  <CardFooter className="pt-0 pb-4">
                    <Button 
                      variant={wasTakenToday(item.id) ? "outline" : "default"}
                      className={cn(
                        "w-full text-sm flex items-center justify-center",
                        wasTakenToday(item.id) 
                          ? "border-green-200 text-green-700 dark:border-green-800 dark:text-green-400" 
                          : "bg-gradient-to-r from-blue-600 to-blue-800 hover:from-blue-700 hover:to-blue-900"
                      )}
                      disabled={isLogging[item.id] || wasTakenToday(item.id)}
                      onClick={() => handleLogIntake(item.id)}
                    >
                      {wasTakenToday(item.id) 
                        ? <><Check className="mr-2 h-4 w-4" /> Taken Today</> 
                        : <><Check className="mr-2 h-4 w-4" /> Log Intake</>
                      }
                    </Button>
                  </CardFooter>
                </Card>
              ))}
            </div>
          </div>
        )
      )}
    </div>
  )
}

