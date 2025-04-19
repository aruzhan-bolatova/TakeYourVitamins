"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import Link from "next/link"
import { getApiUrl } from "@/lib/api-config"
import { ErrorDisplay } from "@/components/ui/error-display"
import { useNotification } from "@/contexts/notification-context"
import { handleError } from "@/lib/error-handler"
import { useAuth } from "@/contexts/auth-context"
import { PublicRoute } from "@/components/public-route"

export default function SignupPage() {
  const { signUp } = useAuth()
  const router = useRouter()
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [age, setAge] = useState("")
  const [gender, setGender] = useState("")
  const [error, setError] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const notification = useNotification()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setIsLoading(true)

    if (!name.trim()) {
      setError("Name is required")
      setIsLoading(false)
      return
    }

    if (!email.trim()) {
      setError("Email is required")
      setIsLoading(false)
      return
    }

    if (!password || password.length < 6) {
      setError("Password must be at least 6 characters")
      setIsLoading(false)
      return
    }

    if (!age.trim()) {
      setError("Age is required")
      setIsLoading(false)
      return
    }

    if (!gender.trim()) {
      setError("Gender is required")
      setIsLoading(false)
      return
    }

    try {
      if (signUp) {
        const success = await signUp(name, email, password, age, gender)
        if (success) {
          // Don't show another success toast - auth context already does this
          setTimeout(() => {
            router.push("/login")
          }, 1500)
          return
        } else {
          setError("Failed to create account. Please try again.")
        }
      } else {
        // Fallback when signUp function isn't available - should be rare
        const response = await fetch(getApiUrl("/api/auth/register"), {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ name, email, password, age, gender }),
        })

        if (response.ok) {
          notification.notifySuccess("Account created successfully! Please log in.")
          setTimeout(() => {
            router.push("/login")
          }, 1500)
        } else {
          const data = await response.json()
          setError(data.message || "Failed to create account")
        }
      }
    } catch (err) {
      const errorMessage = handleError(err, {
        defaultMessage: "Something went wrong. Please try again.",
        context: "Signup",
        showToast: false // Don't show toast, we'll display in the form
      });
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <PublicRoute>
      <div className="flex min-h-screen items-center justify-center px-4">
        <Card className="w-full max-w-md">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl font-bold">Create an account</CardTitle>
            <CardDescription>Enter your information to create an account</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <ErrorDisplay 
                  message={error}
                  onRetry={() => {
                    setError("")
                    if (name && email && password && age && gender) {
                      handleSubmit(new Event('submit') as unknown as React.FormEvent)
                    }
                  }}
                />
              )}
              <div className="space-y-2">
                <label htmlFor="name" className="text-sm font-medium">
                  Name
                </label>
                <Input id="name" value={name} onChange={(e) => setName(e.target.value)} placeholder="John Doe" required />
              </div>
              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium">
                  Email
                </label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  required
                />
              </div>
              <div className="space-y-2">
                <label htmlFor="password" className="text-sm font-medium">
                  Password
                </label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                />
              </div>
              <div className="space-y-2">
                <label htmlFor="age" className="text-sm font-medium">
                  Age
                </label>
                <Input id="age" value={age} onChange={(e) => setAge(e.target.value)} placeholder="21" required />
              </div>
              <div className="space-y-2">
                <label htmlFor="gender" className="text-sm font-medium">
                  Gender
                </label>
                <Input id="gender" value={gender} onChange={(e) => setGender(e.target.value)} placeholder="Female" required />
              </div>
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? "Creating account..." : "Sign Up"}
              </Button>
            </form>
            <div className="mt-4 text-center text-sm">
              Already have an account?{" "}
              <Link href="/login" className="text-primary hover:underline">
                Login
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </PublicRoute>
  )
}
