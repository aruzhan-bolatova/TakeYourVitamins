import type { Alert } from "@/contexts/alerts-context"
import { getApiUrl } from "./api-config"

// Get all alerts for the current user
export async function getAlerts(): Promise<Alert[]> {
  try {
    const token = localStorage.getItem("token")
    if (!token) {
      throw new Error("Authentication required")
    }

    const response = await fetch(getApiUrl("/api/alerts/"), {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      throw new Error("Failed to fetch alerts")
    }

    return await response.json()
  } catch (error) {
    console.error("Error fetching alerts:", error)
    return []
  }
}

// Mark an alert as read
export async function markAlertAsRead(alertId: string): Promise<boolean> {
  try {
    const token = localStorage.getItem("token")
    if (!token) {
      throw new Error("Authentication required")
    }

    const response = await fetch(getApiUrl(`/api/alerts/${alertId}`), {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ read: true }),
    })

    return response.ok
  } catch (error) {
    console.error("Error marking alert as read:", error)
    return false
  }
}

// Generate a test alert
export async function generateTestAlert(): Promise<Alert | null> {
  try {
    // Get the auth token from local storage
    const token = localStorage.getItem("token")
    if (!token) {
      console.error("No authentication token found")
      return null
    }

    console.log("Sending request to generate test alert")
    try {
      // Try first with a connectivity check
      const apiUrl = getApiUrl("/api/alerts/generate")
      console.log("Using API URL:", apiUrl)
      
      // Make the API request to generate a test alert
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        }
      })

      // Check if the response is successful
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        console.error("Failed to generate test alert:", response.status, errorData)
        throw new Error(errorData.error || "Failed to generate test alert")
      }

      // Parse the response
      const data = await response.json()
      console.log("Generated test alert:", data)
      return data
    } catch (networkError) {
      console.error("Network error when connecting to API:", networkError)
      throw new Error("Network error: Cannot connect to the server. Please check your connection and server status.")
    }
  } catch (error) {
    console.error("Error generating test alert:", error)
    throw error // Rethrow to let the context handle it
  }
} 