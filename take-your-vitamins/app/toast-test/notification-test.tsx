"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { toast } from "@/components/ui/use-toast"
import { useNotification } from "@/contexts/notification-context"
import { useEffect, useState } from "react"

export default function NotificationTestPage() {
  const notification = useNotification()
  const [toastCounts, setToastCounts] = useState({
    direct: 0,
    context: 0,
    duplicate: 0,
    multiple: 0
  })

  const showDirectToastError = () => {
    console.log("Calling direct toast.error")
    toast.error("This is a direct toast.error call")
    setToastCounts(prev => ({ ...prev, direct: prev.direct + 1 }))
  }

  const showNotificationContextError = () => {
    console.log("Calling notification.notifyError")
    notification.notifyError("This is a notification.notifyError call")
    setToastCounts(prev => ({ ...prev, context: prev.context + 1 }))
  }

  const showDuplicateError = () => {
    console.log("Testing duplicate detection")
    // This should only show once due to duplicate detection in notification context
    notification.notifyError("This is a duplicate notification that should show only once")
    // Wait a short time and try again with the same message
    setTimeout(() => {
      console.log("Calling duplicate notification again")
      notification.notifyError("This is a duplicate notification that should show only once")
    }, 500)
    setToastCounts(prev => ({ ...prev, duplicate: prev.duplicate + 1 }))
  }

  const showMultipleMessages = () => {
    console.log("Sending multiple notifications")
    // Clear any existing notifications first
    notification.dismissAll()
    
    // Send multiple notifications in sequence
    notification.notifySuccess("Success notification 1")
    notification.notifyInfo("Info notification 2")
    notification.notifyWarning("Warning notification 3")
    notification.notifyError("Error notification 4")
    notification.notifySuccess("Success notification 5")
    setToastCounts(prev => ({ ...prev, multiple: prev.multiple + 1 }))
  }

  useEffect(() => {
    // Log out that the component mounted to verify hooks are working
    console.log("NotificationTestPage mounted")
    return () => {
      console.log("NotificationTestPage unmounted")
    }
  }, [])

  return (
    <div className="container py-6">
      <Card>
        <CardHeader>
          <CardTitle>Notification Context Test</CardTitle>
          <CardDescription>Testing notification context vs direct toast calls</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Button onClick={showDirectToastError} className="bg-red-600 hover:bg-red-700">
              Direct toast.error ({toastCounts.direct})
            </Button>
            <Button onClick={showNotificationContextError} className="bg-blue-600 hover:bg-blue-700">
              notification.notifyError ({toastCounts.context})
            </Button>
            <Button onClick={showDuplicateError} className="bg-purple-600 hover:bg-purple-700">
              Test Duplicate Prevention ({toastCounts.duplicate})
            </Button>
            <Button onClick={showMultipleMessages} className="bg-green-600 hover:bg-green-700">
              Show Multiple Messages ({toastCounts.multiple})
            </Button>
          </div>
          
          <div className="mt-4 flex justify-center">
            <Button 
              onClick={() => {
                console.log("Manually clearing all notifications")
                notification.dismissAll()
              }} 
              className="bg-gray-800 hover:bg-gray-900 text-white px-8"
              size="lg"
            >
              Clear All Notifications
            </Button>
          </div>
          
          <div className="mt-8 p-4 bg-gray-100 dark:bg-gray-800 rounded-md">
            <h3 className="text-lg font-medium mb-2">Debugging Tips</h3>
            <ul className="list-disc pl-5 space-y-1">
              <li>Check browser console for any errors</li>
              <li>Make sure the Toaster component is correctly mounted in layout.tsx</li>
              <li>The MESSAGE_EXPIRY_TIME in notification-context is {2000}ms - duplicate messages within this time will be ignored</li>
              <li>If notifications aren't showing but no errors appear, try increasing the timeout</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 