"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { toast } from "@/components/ui/use-toast"

export default function ToastTestPage() {
  const showSuccessToast = () => {
    toast.success("This is a success toast!")
  }

  const showErrorToast = () => {
    toast.error("This is an error toast!")
  }

  const showInfoToast = () => {
    toast.info("This is an info toast!")
  }

  const showWarningToast = () => {
    toast.warning("This is a warning toast!")
  }

  const showApiErrorToast = () => {
    toast.apiError({
      message: "API Error Message",
      details: "Detailed error information would appear here.\nSecond line of error details.",
      status: 500
    })
  }

  return (
    <div className="container py-6">
      <Card>
        <CardHeader>
          <CardTitle>Toast Notification Test</CardTitle>
          <CardDescription>Click the buttons below to test different toast notifications</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
            <Button onClick={showSuccessToast} className="bg-green-600 hover:bg-green-700">
              Success Toast
            </Button>
            <Button onClick={showErrorToast} className="bg-red-600 hover:bg-red-700">
              Error Toast
            </Button>
            <Button onClick={showInfoToast} className="bg-blue-600 hover:bg-blue-700">
              Info Toast
            </Button>
            <Button onClick={showWarningToast} className="bg-amber-600 hover:bg-amber-700">
              Warning Toast
            </Button>
            <Button onClick={showApiErrorToast} className="bg-purple-600 hover:bg-purple-700">
              API Error Toast
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 