"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import { useRouter } from "next/navigation"

type User = {
  _id: string
  name: string
  email: string
  gender: string
  age: string
}

type AuthContextType = {
  user: User | null
  isLoading: boolean
  signIn: (email: string, password: string) => Promise<boolean>
  signUp: (name: string, email: string, password: string, age: string, gender: string) => Promise<boolean>
  signOut: () => void
  deleteAccount: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  // Load user and token from localStorage on initial render
  // Helper function to check if a token is expired
  const isTokenExpired = (token: string): boolean => {
    try {
      const payload = JSON.parse(atob(token.split(".")[1]))
      const currentTime = Math.floor(Date.now() / 1000)
      return payload.exp < currentTime
    } catch (error) {
      console.error("Error decoding token:", error)
      return true
    }
  }

  useEffect(() => {
    const storedToken = localStorage.getItem("token")
    const storedUser = localStorage.getItem("user")
  
    if (storedToken && isTokenExpired(storedToken)) {
      console.log("Token expired. Logging out.")
      signOut()
      return
    }
  
    if (storedToken && storedUser) {
      setUser(JSON.parse(storedUser))
      console.log("User loaded from localStorage:", JSON.parse(storedUser))
    }
  
    setIsLoading(false)
  }, [])

  // Sign in function using the backend auth/login endpoint
  const signIn = async (email: string, password: string) => {
    setIsLoading(true)

    try {
      // Make a POST request to the auth/login endpoint
      const response = await fetch("http://localhost:5001/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      })

      if (!response.ok) {
        throw new Error("Failed to authenticate. Please check your credentials.")
      }

      // Parse the response to get the access token and userId
      const { access_token, message, userId } = await response.json()
      console.log("Login successful:", message)
      console.log("Access token received:", access_token)
      console.log("User ID:", userId)

      // Save the token in localStorage
      localStorage.setItem("token", access_token)

      // Fetch the user details from the database using the access_token
      const userResponse = await fetch("http://localhost:5001/api/auth/me", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${access_token}`,
        },
      })

      if (!userResponse.ok) {
        throw new Error("Failed to fetch user details.")
      }

      const userData = await userResponse.json()
      console.log("User data received:", userData)

      // Set the user state and save it in localStorage
      setUser(userData)
      console.log("User set in state:", userData)
      localStorage.setItem("user", JSON.stringify(userData))

      // Navigate to the dashboard
      router.push("/dashboard")
      return true
    } catch (error) {
      console.error("Error during sign-in:", error)
      setUser(null)
      localStorage.removeItem("access_token")
      localStorage.removeItem("user")
      return false
    } finally {
      setIsLoading(false)
    }
  }

  // Sign up function using the backend auth/register endpoint
  const signUp = async (name: string, email: string, password: string, age: string, gender: string) => {
    setIsLoading(true)

    try {
      // Make a POST request to the auth/register endpoint
      const response = await fetch("http://localhost:5001/api/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name, email, password, age, gender }),
      })

      if (!response.ok) {
        throw new Error("Failed to register. Please check your details.")
      }

      // Parse the response and set the user
      const userData = await response.json()
      setUser(userData)

      // Store the user in localStorage for persistence
      localStorage.setItem("user", JSON.stringify(userData))
      return true
    } catch (error) {
      console.error("Error during sign-up:", error)
      setUser(null)
      return false
    } finally {
      setIsLoading(false)
    }
  }

  // Sign out function
  const signOut = () => {
    setUser(null)
    localStorage.removeItem("user")
    localStorage.removeItem("token")
    router.push("/")
  }

  const deleteAccount = async () => {
    setIsLoading(true)

    try{
      const response = await fetch("http://localhost:5001/api/users", {
        method: "DELETE",
      })
    
      if (!response.ok) {
        throw new Error("Failed to delete account.")
      }
    }
    catch (error) {
      console.error("Error during account deletion:", error)
    }
    finally{
      setIsLoading(false)
    }
  }

  return (
    // Provide the auth context to children components
    <AuthContext.Provider value={{ user, isLoading, signIn, signUp, signOut, deleteAccount }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}