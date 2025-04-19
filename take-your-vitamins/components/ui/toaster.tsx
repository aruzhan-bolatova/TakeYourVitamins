"use client"

import {
  AlertCircle,
  AlertTriangle,
  CheckCircle,
  Info,
  XCircle,
  X
} from "lucide-react"
import React, { useState, useEffect } from "react"

import { useToast } from "@/components/ui/use-toast"
import {
  Toast,
  ToastClose,
  ToastDescription,
  ToastProvider,
  ToastTitle,
  ToastViewport,
} from "@/components/ui/toast"
import { Button } from "./button"

// Maximum number of toasts to display at once
const MAX_VISIBLE_TOASTS = 3

export function Toaster() {
  const { toasts, dismiss } = useToast()
  
  // Track if there are hidden toasts
  const [hiddenToastCount, setHiddenToastCount] = useState(0)
  
  // Update hidden toast count when toasts change
  useEffect(() => {
    const visibleCount = Math.min(toasts.length, MAX_VISIBLE_TOASTS)
    const hidden = Math.max(0, toasts.length - visibleCount)
    setHiddenToastCount(hidden)
  }, [toasts])
  
  // Clear all toasts
  const clearAllToasts = () => {
    toasts.forEach(toast => {
      if (toast.id) dismiss(toast.id)
    })
  }
  
  // Get visible toasts
  const visibleToasts = toasts.slice(0, MAX_VISIBLE_TOASTS)

  return (
    <ToastProvider>
      {/* Show a summary toast if there are hidden toasts */}
      {hiddenToastCount > 0 && (
        <Toast 
          variant="default" 
          className="bg-blue-50 border-blue-200 dark:bg-blue-950 dark:border-blue-800"
        >
          <div className="flex justify-between items-center w-full">
            <div className="flex items-center gap-2">
              <Info className="h-5 w-5 text-blue-600 dark:text-blue-400" />
              <ToastTitle>{hiddenToastCount} more notification{hiddenToastCount > 1 ? 's' : ''}</ToastTitle>
            </div>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={clearAllToasts}
              className="h-6 px-2 text-xs flex items-center gap-1"
            >
              <X className="h-3 w-3" />
              Clear all
            </Button>
          </div>
        </Toast>
      )}
    
      {visibleToasts.map(function ({ id, title, description, variant, errorDetails, ...props }) {
        // Icon selection based on variant
        let Icon = Info
        if (variant === "destructive") Icon = XCircle
        if (variant === "success") Icon = CheckCircle
        if (variant === "warning") Icon = AlertTriangle
        if (variant === "info") Icon = Info

        return (
          <Toast key={id} variant={variant} {...props}>
            <div className="flex gap-3 items-start">
              <Icon className="h-5 w-5" />
              <div className="grid gap-1">
                {title && <ToastTitle>{title}</ToastTitle>}
                {description && (
                  <ToastDescription>{description}</ToastDescription>
                )}
                {errorDetails && (
                  <details className="mt-2 text-xs">
                    <summary className="cursor-pointer hover:underline">
                      View details
                    </summary>
                    <div className="mt-2 max-h-32 overflow-auto p-2 bg-gray-100 dark:bg-gray-800 rounded text-xs whitespace-pre-wrap font-mono">
                      {errorDetails}
                    </div>
                  </details>
                )}
              </div>
            </div>
            <ToastClose />
          </Toast>
        )
      })}
      <ToastViewport />
    </ToastProvider>
  )
} 