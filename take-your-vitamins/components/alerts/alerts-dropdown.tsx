"use client"

import { useState } from "react"
import { Bell, AlertTriangle } from "lucide-react"
import { useAlerts } from "@/contexts/alerts-context"
import { Button } from "@/components/ui/button"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

export function AlertsDropdown() {
  const { alerts, unreadCount, loading, error, markAsRead } = useAlerts()
  const [open, setOpen] = useState(false)

  // Handle marking an alert as read
  const handleMarkAsRead = async (alertId: string) => {
    await markAsRead(alertId)
  }

  // Get severity color
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "high":
        return "bg-red-500"
      case "medium":
        return "bg-amber-500"
      default:
        return "bg-blue-500"
    }
  }

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <Badge 
              variant="destructive" 
              className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs"
            >
              {unreadCount}
            </Badge>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80 max-h-96 overflow-y-auto p-0" align="end">
        <div className="p-4 border-b">
          <h3 className="font-semibold text-gray-900">Notifications</h3>
          {loading && <p className="text-sm text-gray-500">Loading...</p>}
        </div>
        
        {error ? (
          <div className="p-4 text-center">
            <AlertTriangle className="h-5 w-5 text-red-500 mx-auto mb-2" />
            <p className="text-sm text-red-500">{error}</p>
          </div>
        ) : alerts.length === 0 && !loading ? (
          <div className="p-4 text-center text-sm text-gray-500">
            No notifications
          </div>
        ) : (
          <div className="divide-y">
            {alerts.map((alert) => (
              <div 
                key={alert._id} 
                className="p-4 bg-blue-50 hover:bg-blue-100 transition-colors cursor-pointer"
                onClick={() => handleMarkAsRead(alert._id)}
              >
                <div className="flex items-start gap-2 mb-1">
                  <div className={cn("h-2 w-2 mt-1.5 rounded-full", getSeverityColor(alert.severity))} />
                  <div className="flex-1">
                    <h4 className="font-medium text-sm text-gray-900">{alert.title}</h4>
                    <p className="text-sm text-gray-700">{alert.message}</p>
                  </div>
                </div>
                <div className="text-xs text-gray-500 pl-4">
                  {formatDate(alert.createdAt)}
                </div>
              </div>
            ))}
          </div>
        )}
      </PopoverContent>
    </Popover>
  )
} 