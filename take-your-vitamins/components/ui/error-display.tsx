"use client"

import { AlertCircle, AlertTriangle, XCircle, RefreshCw } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"

type ErrorSeverity = "error" | "warning" | "fatal"

interface ErrorDisplayProps {
  title?: string
  message: string
  severity?: ErrorSeverity
  details?: string
  onRetry?: () => void
  className?: string
  id?: string
}

export function ErrorDisplay({
  title,
  message,
  severity = "error",
  details,
  onRetry,
  className = "",
  id,
}: ErrorDisplayProps) {
  const getIcon = () => {
    switch (severity) {
      case "fatal":
        return <XCircle className="h-5 w-5" />
      case "warning":
        return <AlertTriangle className="h-5 w-5 text-amber-500" />
      case "error":
      default:
        return <AlertCircle className="h-5 w-5" />
    }
  }

  const getVariant = () => {
    switch (severity) {
      case "fatal":
        return "destructive"
      case "warning":
        return "default"
      case "error":
      default:
        return "destructive"
    }
  }

  const getTitle = () => {
    if (title) return title
    
    switch (severity) {
      case "fatal":
        return "Critical Error"
      case "warning":
        return "Warning"
      case "error":
      default:
        return "Error"
    }
  }

  const getBgClass = () => {
    switch (severity) {
      case "fatal":
        return "bg-red-50 border-red-200 dark:bg-red-950 dark:border-red-800"
      case "warning":
        return "bg-amber-50 border-amber-200 dark:bg-amber-950 dark:border-amber-800"
      case "error":
      default:
        return "bg-red-50 border-red-200 dark:bg-red-950 dark:border-red-800"
    }
  }

  return (
    <Alert 
      variant={getVariant()} 
      className={`${getBgClass()} ${className}`}
      id={id}
    >
      <div className="flex items-start gap-2">
        {getIcon()}
        <div className="flex-1 space-y-1">
          <AlertTitle>{getTitle()}</AlertTitle>
          <AlertDescription className="text-sm">{message}</AlertDescription>
          
          {details && (
            <details className="mt-2 cursor-pointer">
              <summary className="text-xs font-medium hover:underline">
                Show technical details
              </summary>
              <div className="mt-2 rounded bg-gray-100 p-2 text-xs font-mono whitespace-pre-wrap text-gray-800 dark:bg-gray-800 dark:text-gray-200 overflow-auto max-h-[200px]">
                {details}
              </div>
            </details>
          )}
          
          {onRetry && (
            <div className="mt-3">
              <Button 
                size="sm" 
                variant="outline" 
                onClick={onRetry}
                className="flex items-center gap-1 text-xs"
              >
                <RefreshCw className="h-3 w-3" />
                Try Again
              </Button>
            </div>
          )}
        </div>
      </div>
    </Alert>
  )
} 