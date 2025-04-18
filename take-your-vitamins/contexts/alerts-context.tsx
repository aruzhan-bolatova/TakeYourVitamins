"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import { useAuth } from "./auth-context"
import { getAlerts, markAlertAsRead, generateTestAlert as generateAlert } from "@/lib/alerts"

export type Alert = {
  _id: string
  alertId: string
  userId: string
  type: string
  title: string
  message: string
  severity: "low" | "medium" | "high"
  read: boolean
  createdAt: string
  updatedAt: string | null
}

interface AlertsContextType {
  alerts: Alert[]
  unreadCount: number
  loading: boolean
  error: string | null
  fetchAlerts: () => Promise<void>
  markAsRead: (alertId: string) => Promise<void>
  generateTestAlert: () => Promise<void>
}

const AlertsContext = createContext<AlertsContextType | undefined>(undefined)

export function AlertsProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth()
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Computed value for unread alerts count
  const unreadCount = alerts.filter(alert => !alert.read).length

  // Fetch alerts from the API
  const fetchAlerts = async () => {
    if (!user) return

    setLoading(true)
    setError(null)

    try {
      const fetchedAlerts = await getAlerts()
      setAlerts(fetchedAlerts)
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unknown error occurred")
      console.error("Error fetching alerts:", err)
    } finally {
      setLoading(false)
    }
  }

  // Mark an alert as read
  const markAsRead = async (alertId: string) => {
    if (!user) return

    try {
      const success = await markAlertAsRead(alertId)
      
      if (success) {
        // Update local state
        setAlerts(prevAlerts =>
          prevAlerts.map(alert =>
            alert._id === alertId || alert.alertId === alertId
              ? { ...alert, read: true }
              : alert
          )
        )
      } else {
        throw new Error("Failed to mark alert as read")
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unknown error occurred")
      console.error("Error marking alert as read:", err)
    }
  }

  // Generate a test alert
  const generateTestAlert = async () => {
    if (!user) {
      setError("You must be logged in to generate alerts")
      return
    }

    setLoading(true)
    setError(null)

    try {
      console.log("Generating test alert...")
      const newAlert = await generateAlert()
      
      if (newAlert) {
        console.log("Alert generated successfully:", newAlert)
        setAlerts(prevAlerts => [newAlert, ...prevAlerts])
      } else {
        throw new Error("No alert was returned from the server")
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to generate test alert"
      console.error("Error in generateTestAlert:", errorMessage)
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  // Fetch alerts when user changes
  useEffect(() => {
    if (user) {
      fetchAlerts()
    } else {
      setAlerts([])
    }
  }, [user])

  return (
    <AlertsContext.Provider
      value={{
        alerts,
        unreadCount,
        loading,
        error,
        fetchAlerts,
        markAsRead,
        generateTestAlert,
      }}
    >
      {children}
    </AlertsContext.Provider>
  )
}

export function useAlerts() {
  const context = useContext(AlertsContext)
  if (context === undefined) {
    throw new Error("useAlerts must be used within an AlertsProvider")
  }
  return context
} 