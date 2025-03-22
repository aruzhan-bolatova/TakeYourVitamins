//Auth Context: Manages user authentication state
"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"

type User = {
  id: string
  name: string
  email: string
  image?: string
}

type AuthContextType = {
  user: User | null
  isLoading: boolean
  signIn: (email: string, password: string) => Promise<boolean>
  signUp: (name: string, email: string, password: string) => Promise<boolean>
  signOut: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Load user from localStorage on initial render
  useEffect(() => {
    const storedUser = localStorage.getItem("user")
    if (storedUser) {
      setUser(JSON.parse(storedUser))
    }
    setIsLoading(false)
  }, [])

  // Mock sign in function
  const signIn = async (email: string, password: string) => {
    setIsLoading(true)

    // Simulate API call delay
    await new Promise((resolve) => setTimeout(resolve, 1000))

    // For demo purposes, any email/password combination works
    // In a real app, you would validate against a backend
    const mockUser: User = {
      id: "user-1",
      name: email.split("@")[0],
      email: email,
    }

    setUser(mockUser)
    localStorage.setItem("user", JSON.stringify(mockUser))
    setIsLoading(false)
    return true
  }

  // Mock sign up function
  const signUp = async (name: string, email: string, password: string) => {
    setIsLoading(true)

    // Simulate API call delay
    await new Promise((resolve) => setTimeout(resolve, 1000))

    // For demo purposes, any registration works
    const mockUser: User = {
      id: "user-1",
      name: name,
      email: email,
    }

    setUser(mockUser)
    localStorage.setItem("user", JSON.stringify(mockUser))
    setIsLoading(false)
    return true
  }

  // Mock sign out function
  const signOut = () => {
    setUser(null)
    localStorage.removeItem("user")
    localStorage.removeItem("trackedSupplements")
    localStorage.removeItem("intakeLogs")
  }

  return <AuthContext.Provider value={{ user, isLoading, signIn, signUp, signOut }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}

