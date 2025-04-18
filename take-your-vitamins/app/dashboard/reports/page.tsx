"use client"

import { useState, useEffect } from "react"
import { getUserReport, ReportData } from "@/lib/reports"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import { format } from "date-fns"
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line
} from "recharts"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { AlertCircle, Award, TrendingUp } from "lucide-react"

export default function ReportsPage() {
  const [reportData, setReportData] = useState<ReportData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [reportRange, setReportRange] = useState<"daily" | "weekly" | "monthly" | "yearly">("weekly")

  useEffect(() => {
    async function fetchReport() {
      setLoading(true)
      setError(null)
      try {
        const data = await getUserReport(reportRange)
        setReportData(data)
      } catch (err) {
        setError("Failed to load report. Please try again later.")
        console.error("Error loading report:", err)
      } finally {
        setLoading(false)
      }
    }

    fetchReport()
  }, [reportRange])

  // Format date for display
  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), "PPP")
    } catch (error) {
      return dateString
    }
  }

  return (
    <div className="container py-6">
      <div className="flex flex-col gap-4">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Your Reports</h1>
          <Select 
            value={reportRange} 
            onValueChange={(value) => setReportRange(value as "daily" | "weekly" | "monthly" | "yearly")}
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select range" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="daily">Daily</SelectItem>
              <SelectItem value="weekly">Weekly</SelectItem>
              <SelectItem value="monthly">Monthly</SelectItem>
              <SelectItem value="yearly">Yearly</SelectItem>
            </SelectContent>
          </Select>
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

        {reportData && (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Report Overview</CardTitle>
                <CardDescription>
                  {reportRange.charAt(0).toUpperCase() + reportRange.slice(1)} report from {formatDate(reportData.startDate)} to {formatDate(reportData.endDate)}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="summary">
                  <TabsList className="grid w-full grid-cols-4">
                    <TabsTrigger value="summary">Summary</TabsTrigger>
                    <TabsTrigger value="streaks">Streaks</TabsTrigger>
                    <TabsTrigger value="correlations">Correlations</TabsTrigger>
                    <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
                  </TabsList>

                  {/* Summary Tab */}
                  <TabsContent value="summary">
                    <div className="grid md:grid-cols-2 gap-4 mt-4">
                      {/* Supplement Intake Summary */}
                      <Card>
                        <CardHeader>
                          <CardTitle>Supplement Intake</CardTitle>
                        </CardHeader>
                        <CardContent>
                          {reportData.intakeSummary.length > 0 ? (
                            <div className="space-y-4">
                              {reportData.intakeSummary.map((item) => (
                                <div key={item.supplementId} className="border rounded-lg p-3">
                                  <div className="flex justify-between items-center">
                                    <h3 className="font-medium">{item.name}</h3>
                                    <Badge variant="outline">{item.count} times</Badge>
                                  </div>
                                  <div className="mt-2 text-sm text-muted-foreground">
                                    <p>Taken on {item.uniqueDays} unique days</p>
                                    {item.mostCommonDosage && (
                                      <p>Common dosage: {item.mostCommonDosage}</p>
                                    )}
                                    {item.mostCommonTiming && (
                                      <p>Usually taken: {item.mostCommonTiming}</p>
                                    )}
                                  </div>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p className="text-center text-muted-foreground">No supplement intake data for this period</p>
                          )}
                        </CardContent>
                      </Card>

                      {/* Symptom Summary */}
                      <Card>
                        <CardHeader>
                          <CardTitle>Symptom Summary</CardTitle>
                        </CardHeader>
                        <CardContent>
                          {reportData.symptomSummary.length > 0 ? (
                            <div className="space-y-4">
                              {reportData.symptomSummary.map((item) => (
                                <div key={item.symptom} className="border rounded-lg p-3">
                                  <div className="flex justify-between items-center">
                                    <h3 className="font-medium">{item.symptom}</h3>
                                    <Badge variant="outline">{item.count} times</Badge>
                                  </div>
                                  <div className="mt-2 text-sm text-muted-foreground">
                                    <p>Average severity: {item.averageSeverity.toFixed(1)}/3</p>
                                  </div>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p className="text-center text-muted-foreground">No symptom data for this period</p>
                          )}
                        </CardContent>
                      </Card>
                    </div>

                    {/* Progress Trends */}
                    <Card className="mt-4">
                      <CardHeader>
                        <CardTitle>Progress Trends</CardTitle>
                      </CardHeader>
                      <CardContent>
                        {reportData.progress.supplementProgress.length > 0 ? (
                          <div className="h-64">
                            <ResponsiveContainer width="100%" height="100%">
                              <LineChart
                                data={reportData.progress.overallTrends.monthlyTotals}
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
                                  name="Total Intake"
                                  stroke="#8884d8" 
                                  activeDot={{ r: 8 }} 
                                />
                                <Line 
                                  type="monotone" 
                                  dataKey="totalUniqueDays" 
                                  name="Total Days"
                                  stroke="#82ca9d" 
                                />
                              </LineChart>
                            </ResponsiveContainer>
                          </div>
                        ) : (
                          <p className="text-center text-muted-foreground">No progress data available</p>
                        )}
                      </CardContent>
                    </Card>

                    {/* Milestones */}
                    {reportData.progress.milestones.length > 0 && (
                      <div className="mt-4 grid grid-cols-2 md:grid-cols-3 gap-4">
                        {reportData.progress.milestones.map((milestone, index) => (
                          <Card key={index}>
                            <CardContent className="pt-6">
                              <div className="flex flex-col items-center text-center">
                                <Award className="h-10 w-10 text-primary mb-2" />
                                <h3 className="font-medium">{milestone.description}</h3>
                                <p className="text-sm text-muted-foreground mt-1">
                                  {milestone.type === 'totalIntake' && `${milestone.value} times`}
                                  {milestone.type === 'consistency' && `${milestone.value}% consistent`}
                                </p>
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    )}
                  </TabsContent>

                  {/* Streaks Tab */}
                  <TabsContent value="streaks">
                    <div className="mt-4">
                      <Card>
                        <CardHeader>
                          <CardTitle>Your Supplement Streaks</CardTitle>
                          <CardDescription>Track your consistency in taking supplements</CardDescription>
                        </CardHeader>
                        <CardContent>
                          {reportData.streaks.length > 0 ? (
                            <div className="space-y-4">
                              {reportData.streaks.map((streak) => (
                                <div key={streak.supplementId} className="border rounded-lg p-4">
                                  <div className="flex justify-between items-center">
                                    <h3 className="font-medium">{streak.supplementName}</h3>
                                    <div className="flex space-x-2">
                                      <Badge variant="outline" className="bg-primary/10">
                                        Current: {streak.currentStreak} {streak.currentStreak === 1 ? 'day' : 'days'}
                                      </Badge>
                                      <Badge variant="outline" className="bg-secondary/10">
                                        Best: {streak.longestStreak} {streak.longestStreak === 1 ? 'day' : 'days'}
                                      </Badge>
                                    </div>
                                  </div>
                                  <p className="mt-2 text-sm text-muted-foreground">
                                    Last taken: {formatDate(streak.lastTaken)}
                                  </p>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p className="text-center text-muted-foreground">No streak data available</p>
                          )}
                        </CardContent>
                      </Card>
                    </div>
                  </TabsContent>

                  {/* Correlations Tab */}
                  <TabsContent value="correlations">
                    <div className="mt-4">
                      <Card>
                        <CardHeader>
                          <CardTitle>Supplement-Symptom Correlations</CardTitle>
                          <CardDescription>Possible relationships between supplements and symptoms</CardDescription>
                        </CardHeader>
                        <CardContent>
                          {reportData.correlations.length > 0 ? (
                            <div className="space-y-4">
                              {reportData.correlations.map((correlation, index) => (
                                <div key={index} className="border rounded-lg p-4">
                                  <div className="flex justify-between items-center">
                                    <div>
                                      <h3 className="font-medium">{correlation.supplementName} & {correlation.symptom}</h3>
                                      <p className="text-sm text-muted-foreground mt-1">
                                        {correlation.description}
                                      </p>
                                    </div>
                                    <Badge 
                                      variant={correlation.correlationStrength > 0.7 ? "destructive" : 
                                              correlation.correlationStrength > 0.4 ? "default" : "outline"}
                                    >
                                      {correlation.correlationStrength > 0.7 ? "Strong" : 
                                       correlation.correlationStrength > 0.4 ? "Moderate" : "Weak"}
                                    </Badge>
                                  </div>
                                  <p className="mt-2 text-xs text-muted-foreground">
                                    Confidence: {(correlation.confidence * 100).toFixed(0)}%
                                  </p>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p className="text-center text-muted-foreground">No correlations detected</p>
                          )}
                          <Alert className="mt-4">
                            <AlertCircle className="h-4 w-4" />
                            <AlertTitle>Important Note</AlertTitle>
                            <AlertDescription>
                              Correlations don't necessarily indicate causation. Please consult with a healthcare professional before making any changes to your supplement regimen.
                            </AlertDescription>
                          </Alert>
                        </CardContent>
                      </Card>
                    </div>
                  </TabsContent>

                  {/* Recommendations Tab */}
                  <TabsContent value="recommendations">
                    <div className="mt-4">
                      <Card>
                        <CardHeader>
                          <CardTitle>Personalized Recommendations</CardTitle>
                          <CardDescription>Based on your supplement intake and symptom patterns</CardDescription>
                        </CardHeader>
                        <CardContent>
                          {reportData.recommendations.length > 0 ? (
                            <div className="space-y-4">
                              {reportData.recommendations.map((recommendation, index) => (
                                <Alert key={index} className={recommendation.confidence > 0.7 ? "border-primary" : ""}>
                                  <TrendingUp className="h-4 w-4" />
                                  <AlertTitle>{recommendation.type}</AlertTitle>
                                  <AlertDescription>{recommendation.description}</AlertDescription>
                                </Alert>
                              ))}
                            </div>
                          ) : (
                            <p className="text-center text-muted-foreground">No recommendations available yet</p>
                          )}
                        </CardContent>
                      </Card>
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
} 