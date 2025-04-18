"use client"

import { useState } from "react"
import { useAlerts } from "@/contexts/alerts-context"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertTriangle, Bell, Check, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

export default function AlertsPage() {
  const { alerts, loading, error, generateTestAlert, fetchAlerts, markAsRead } = useAlerts()
  const [refreshing, setRefreshing] = useState(false)
  const [generating, setGenerating] = useState(false)

  // Get severity color
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "high":
        return "text-red-500"
      case "medium":
        return "text-amber-500"
      default:
        return "text-blue-500"
    }
  }

  // Handle refresh
  const handleRefresh = async () => {
    setRefreshing(true)
    await fetchAlerts()
    setRefreshing(false)
  }

  // Handle test alert generation
  const handleGenerateTestAlert = async () => {
    setGenerating(true)
    try {
      await generateTestAlert()
    } finally {
      setGenerating(false)
    }
  }

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      weekday: 'short',
      year: 'numeric',
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  return (
    <div className="container py-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Your Alerts</h1>
        <div className="space-x-2">
          <Button 
            variant="outline" 
            onClick={handleRefresh}
            disabled={refreshing || loading || generating}
          >
            {refreshing ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Refreshing...
              </>
            ) : "Refresh"}
          </Button>
          <Button 
            onClick={handleGenerateTestAlert} 
            disabled={generating || loading || refreshing}
          >
            {generating ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Generating...
              </>
            ) : "Generate Test Alert"}
          </Button>
        </div>
      </div>

      {error && (
        <Card className="mb-6 border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500 mt-0.5" />
              <div>
                <h3 className="font-semibold text-red-800">Error</h3>
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {loading ? (
        <div className="text-center py-12">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-muted-foreground" />
          <p className="text-muted-foreground">Loading alerts...</p>
        </div>
      ) : alerts.length === 0 ? (
        <Card>
          <CardContent className="pt-6 pb-6 text-center">
            <Bell className="h-12 w-12 mx-auto text-muted-foreground mb-3" />
            <h3 className="text-lg font-medium mb-2 text-gray-900">No alerts</h3>
            <p className="text-sm text-gray-700">
              You don't have any alerts at the moment. Generate a test alert to see how they appear.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {alerts.map((alert) => (
            <Card 
              key={alert._id} 
              className="bg-blue-50 border border-blue-200 shadow-sm"
            >
              <CardHeader className="pb-2">
                <div className="flex justify-between items-start">
                  <CardTitle className="text-lg flex items-center gap-2 text-gray-900">
                    <span className={getSeverityColor(alert.severity)}>●</span> 
                    {alert.title}
                  </CardTitle>
                  <CardDescription className="text-gray-600">
                    {formatDate(alert.createdAt)}
                  </CardDescription>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-800">{alert.message}</p>
              </CardContent>
              <CardFooter className="pt-0 flex justify-between">
                <CardDescription className="text-gray-700">
                  Severity: <span className={getSeverityColor(alert.severity)}>{alert.severity}</span>
                </CardDescription>
                {!alert.read && (
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="text-xs bg-white"
                    onClick={() => markAsRead(alert._id)}
                  >
                    <Check className="h-3 w-3 mr-1" /> Mark as read
                  </Button>
                )}
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
} 