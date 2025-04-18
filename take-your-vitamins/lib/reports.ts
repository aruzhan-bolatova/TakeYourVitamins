import { getApiUrl } from "./api-config"

// Define report data types
export type IntakeSummary = {
  supplementId: string
  name: string
  count: number
  uniqueDays: number
  mostCommonDosage?: string
  mostCommonTiming?: string
}

export type SymptomSummary = {
  symptom: string
  count: number
  averageSeverity: number
  dates: string[]
}

export type Correlation = {
  supplementId: string
  supplementName: string
  symptom: string
  correlationStrength: number
  description: string
  confidence: number
}

export type Streak = {
  supplementId: string
  supplementName: string
  currentStreak: number
  longestStreak: number
  lastTaken: string
}

export type ProgressItem = {
  month: string
  count: number
  uniqueDays: number
  consistency: number
}

export type SupplementProgress = {
  supplementId: string
  supplementName: string
  monthlyData: ProgressItem[]
}

export type Milestone = {
  type: string
  value: number
  description: string
}

export type ReportData = {
  userId: string
  reportType: "daily" | "weekly" | "monthly" | "yearly"
  startDate: string
  endDate: string
  intakeSummary: IntakeSummary[]
  symptomSummary: SymptomSummary[]
  correlations: Correlation[]
  streaks: Streak[]
  progress: {
    supplementProgress: SupplementProgress[]
    overallTrends: {
      totalSupplements: number
      monthlyTotals: {
        month: string
        totalCount: number
        totalUniqueDays: number
      }[]
      consistencyTrend: "increasing" | "decreasing" | "stable"
    }
    milestones: Milestone[]
  }
  recommendations: {
    type: string
    description: string
    confidence: number
  }[]
}

export type StreaksData = {
  userId: string
  streaks: Streak[]
}

export type ProgressData = {
  userId: string
  progress: {
    supplementProgress: SupplementProgress[]
    overallTrends: {
      totalSupplements: number
      monthlyTotals: {
        month: string
        totalCount: number
        totalUniqueDays: number
      }[]
      consistencyTrend: "increasing" | "decreasing" | "stable"
    }
    milestones: Milestone[]
  }
}

/**
 * Get a complete report for the current user
 * @param range The time range for the report (daily, weekly, monthly, yearly)
 * @returns The report data or null if an error occurred
 */
export async function getUserReport(
  range: "daily" | "weekly" | "monthly" | "yearly" = "weekly"
): Promise<ReportData | null> {
  try {
    const token = localStorage.getItem("token")
    if (!token) {
      throw new Error("Authentication required")
    }

    // Get the user ID from token (since we need it for the endpoint)
    const userResponse = await fetch(getApiUrl("/api/auth/me"), {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!userResponse.ok) {
      throw new Error("Failed to get user information")
    }

    const userData = await userResponse.json()
    const userId = userData.userId

    // Now get the report
    const response = await fetch(
      getApiUrl(`/api/reports/${userId}?range=${range}`),
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    )

    if (!response.ok) {
      throw new Error("Failed to fetch report")
    }

    return await response.json()
  } catch (error) {
    console.error("Error fetching user report:", error)
    return null
  }
}

/**
 * Get streak information for the current user
 * @returns The streaks data or null if an error occurred
 */
export async function getUserStreaks(): Promise<StreaksData | null> {
  try {
    const token = localStorage.getItem("token")
    if (!token) {
      throw new Error("Authentication required")
    }

    // Get the user ID from token
    const userResponse = await fetch(getApiUrl("/api/auth/me"), {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!userResponse.ok) {
      throw new Error("Failed to get user information")
    }

    const userData = await userResponse.json()
    const userId = userData.userId

    // Now get the streaks
    const response = await fetch(
      getApiUrl(`/api/reports/streaks/${userId}`),
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    )

    if (!response.ok) {
      throw new Error("Failed to fetch streaks")
    }

    return await response.json()
  } catch (error) {
    console.error("Error fetching user streaks:", error)
    return null
  }
}

/**
 * Get progress information for the current user
 * @returns The progress data or null if an error occurred
 */
export async function getUserProgress(): Promise<ProgressData | null> {
  try {
    const token = localStorage.getItem("token")
    if (!token) {
      throw new Error("Authentication required")
    }

    // Get the user ID from token
    const userResponse = await fetch(getApiUrl("/api/auth/me"), {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!userResponse.ok) {
      throw new Error("Failed to get user information")
    }

    const userData = await userResponse.json()
    const userId = userData.userId

    // Now get the progress
    const response = await fetch(
      getApiUrl(`/api/reports/progress/${userId}`),
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    )

    if (!response.ok) {
      throw new Error("Failed to fetch progress")
    }

    return await response.json()
  } catch (error) {
    console.error("Error fetching user progress:", error)
    return null
  }
} 