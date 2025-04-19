"use client"

import type React from "react"
import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import Link from "next/link"
import { useAuth } from "@/contexts/auth-context"
import { handleError } from "@/lib/error-handler"
import { ErrorDisplay } from "@/components/ui/error-display"
import { useNotification } from "@/contexts/notification-context"

export default function LoginPage() {
  const { signIn, isLoading } = useAuth()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [localLoading, setLocalLoading] = useState(false)
  const notification = useNotification()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLocalLoading(true)
    
    // Validate form fields
    if (!email.trim()) {
      setError("Email is required");
      setLocalLoading(false);
      return;
    }
    
    if (!password) {
      setError("Password is required");
      setLocalLoading(false);
      return;
    }
    
    try {
      // Don't show separate loading toast - the button state is enough
      const success = await signIn(email, password)
      
      if (!success) {
        setError("Invalid email or password. Please try again.");
      }
    } catch (err) {
      const errorMessage = handleError(err, {
        defaultMessage: "Login failed. Please check your credentials.",
        context: "Authentication",
        showToast: false // Don't show toast, we'll show the error in the form
      });
      setError(errorMessage);
    } finally {
      setLocalLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold">Login</CardTitle>
          <CardDescription>Enter your email and password to access your account</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <ErrorDisplay 
                message={error}
                onRetry={() => {
                  setError(null);
                  if (email && password) {
                    handleSubmit(new Event('submit') as unknown as React.FormEvent);
                  }
                }}
              />
            )}
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
                autoComplete="email"
              />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label htmlFor="password" className="text-sm font-medium">
                  Password
                </label>
                <Link href="#" className="text-sm text-primary hover:underline">
                  Forgot password?
                </Link>
              </div>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                autoComplete="current-password"
              />
            </div>
            <Button type="submit" className="w-full" disabled={isLoading || localLoading}>
              {isLoading || localLoading ? "Logging in..." : "Login"}
            </Button>
          </form>
          <div className="mt-4 text-center text-sm">
            Don't have an account?{" "}
            <Link href="/signup" className="text-primary hover:underline">
              Sign up
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
