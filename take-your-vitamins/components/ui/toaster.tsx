"use client"

import {
  AlertCircle,
  AlertTriangle,
  CheckCircle,
  Info,
  XCircle,
} from "lucide-react"
import React from "react"

import { useToast } from "@/components/ui/use-toast"
import {
  Toast,
  ToastClose,
  ToastDescription,
  ToastProvider,
  ToastTitle,
  ToastViewport,
} from "@/components/ui/toast"

export function Toaster() {
  const { toasts } = useToast()

  return (
    <ToastProvider>
      {toasts.map(function ({ id, title, description, variant, errorDetails, ...props }) {
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