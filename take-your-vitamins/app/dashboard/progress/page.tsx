"use client"

import { useState, useEffect } from "react"
import { getUserProgress, ProgressData, SupplementProgress } from "@/lib/reports"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { AlertCircle, Award, TrendingUp, TrendingDown, Minus } from "lucide-react"
import { 
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell
} from "recharts"

// Colors for charts
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

export default function ProgressPage() {
  const [progressData, setProgressData] = useState<ProgressData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedSupplement, setSelectedSupplement] = useState<string | null>(null)

  useEffect(() => {
    async function fetchProgress() {
      setLoading(true)
      setError(null)
      try {
        const data = await getUserProgress()
        if (data) {
          setProgressData(data)
          // Set the first supplement as selected by default if available
          if (data.progress?.supplementProgress?.length > 0) {
            setSelectedSupplement(data.progress.supplementProgress[0].supplementId)
          }
        } else {
          throw new Error("No data returned")
        }
      } catch (err) {
        setError("Failed to load progress data. Please try again later.")
        console.error("Error loading progress:", err)
      } finally {
        setLoading(false)
      }
    }

    fetchProgress()
  }, [])

  // Helper to generate chart data for a specific supplement
  const getSupplementChartData = (supplementId: string) => {
    if (!progressData) return []
    
    const supplement = progressData.progress.supplementProgress.find(
      s => s.supplementId === supplementId
    )
    
    if (!supplement) return []
    return supplement.monthlyData
  }

  // Helper to get trend icon based on trend direction
  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'increasing':
        return <TrendingUp className="h-4 w-4 text-green-500" />
      case 'decreasing':
        return <TrendingDown className="h-4 w-4 text-red-500" />
      default:
        return <Minus className="h-4 w-4 text-yellow-500" />
    }
  }

  return (
    <div className="container py-6">
      <div className="flex flex-col gap-4">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Your Progress</h1>
        </div>

        {loading && (
          <div className="space-y-4">
            <Skeleton className="h-48 w-full" />
            <Skeleton className="h-48 w-full" />
            <Skeleton className="h-48 w-full" />
          </div>
        )}

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {progressData && (
          <div className="space-y-6">
            {/* Overall Trends */}
            <Card>
              <CardHeader>
                <CardTitle>Overall Progress</CardTitle>
                <CardDescription>
                  Your supplement intake trends over time
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2 mb-4">
                  <div className="flex items-center gap-1">
                    <span>Consistency Trend:</span>
                    {getTrendIcon(progressData.progress.overallTrends.consistencyTrend)}
                    <span className="ml-1 font-medium">
                      {progressData.progress.overallTrends.consistencyTrend.charAt(0).toUpperCase() + 
                      progressData.progress.overallTrends.consistencyTrend.slice(1)}
                    </span>
                  </div>
                </div>

                {/* Overall Chart */}
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={progressData.progress.overallTrends.monthlyTotals}
                      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line 
                        type="monotone" 
                        dataKey="totalCount" 
                        name="Total Intake Count" 
                        stroke="#8884d8" 
                        activeDot={{ r: 8 }} 
                      />
                      <Line 
                        type="monotone" 
                        dataKey="totalUniqueDays" 
                        name="Unique Days" 
                        stroke="#82ca9d" 
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* Supplement-Specific Progress */}
            <Card>
              <CardHeader>
                <CardTitle>Supplement-Specific Progress</CardTitle>
                <CardDescription>
                  Track how consistently you've been taking each supplement
                </CardDescription>
              </CardHeader>
              <CardContent>
                {progressData.progress.supplementProgress.length > 0 ? (
                  <>
                    <Tabs 
                      defaultValue={selectedSupplement || undefined}
                      onValueChange={(value) => setSelectedSupplement(value)}
                    >
                      <TabsList className="mb-4">
                        {progressData.progress.supplementProgress.map((supplement) => (
                          <TabsTrigger key={supplement.supplementId} value={supplement.supplementId}>
                            {supplement.supplementName}
                          </TabsTrigger>
                        ))}
                      </TabsList>

                      {progressData.progress.supplementProgress.map((supplement) => (
                        <TabsContent key={supplement.supplementId} value={supplement.supplementId}>
                          <div className="h-64">
                            <ResponsiveContainer width="100%" height="100%">
                              <BarChart
                                data={supplement.monthlyData}
                                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                              >
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="month" />
                                <YAxis yAxisId="left" orientation="left" stroke="#8884d8" />
                                <YAxis yAxisId="right" orientation="right" stroke="#82ca9d" />
                                <Tooltip />
                                <Legend />
                                <Bar 
                                  yAxisId="left" 
                                  dataKey="count" 
                                  name="Total Intake" 
                                  fill="#8884d8" 
                                />
                                <Bar 
                                  yAxisId="right" 
                                  dataKey="consistency" 
                                  name="Consistency %" 
                                  fill="#82ca9d" 
                                />
                              </BarChart>
                            </ResponsiveContainer>
                          </div>
                        </TabsContent>
                      ))}
                    </Tabs>
                  </>
                ) : (
                  <p className="text-center text-muted-foreground py-8">
                    No supplement-specific progress data available yet
                  </p>
                )}
              </CardContent>
            </Card>

            {/* Milestones */}
            {progressData.progress.milestones.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Your Milestones</CardTitle>
                  <CardDescription>
                    Achievements in your supplement journey
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {progressData.progress.milestones.map((milestone, index) => (
                      <Card key={index} className="border-primary/20">
                        <CardContent className="pt-6">
                          <div className="flex flex-col items-center text-center">
                            <Award className="h-12 w-12 text-primary mb-3" />
                            <h3 className="font-medium text-lg">{milestone.description}</h3>
                            <p className="text-sm text-muted-foreground mt-2">
                              {milestone.value} {milestone.type === 'totalIntake' ? 'total intakes' : 
                                milestone.type === 'consistency' ? '% consistency' : 'milestone value'}
                            </p>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  )
} 