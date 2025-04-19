"use client"

import React, { createContext, useContext, ReactNode, useMemo } from 'react'
import { useToast } from '@/components/ui/use-toast'
import { formatError, getUserFriendlyErrorMessage, isNetworkError, isAuthError, isValidationError } from '@/lib/error-handling'

export type NotificationType = 'success' | 'error' | 'warning' | 'info'

interface NotificationContextType {
  notify: (type: NotificationType, message: string, options?: any) => void
  notifySuccess: (message: string, options?: any) => void
  notifyError: (message: string, options?: any) => void
  notifyWarning: (message: string, options?: any) => void
  notifyInfo: (message: string, options?: any) => void
  handleApiError: (error: any, fallbackMessage?: string) => void
  dismissAll: () => void
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined)

// Keep track of recently shown messages to prevent duplicates
const recentMessages = new Set<string>()
const MAX_RECENT_MESSAGES = 10
// Increased the timeout from 2000ms to 5000ms to make duplicate detection less aggressive
const MESSAGE_EXPIRY_TIME = 5000 // 5 seconds

// Check if a message is a duplicate
const isDuplicate = (message: string | undefined): boolean => {
  if (!message) return false;
  
  // Log for debugging
  if (recentMessages.has(message)) {
    console.log(`Duplicate message detected: "${message}"`);
    return true;
  }
  
  return false;
}

// Clear a message from the recent messages set after expiry time
const trackRecentMessage = (message: string | undefined) => {
  if (!message) return; // Skip if message is undefined
  
  // Log for debugging
  console.log(`Tracking message: "${message}"`);
  
  const messageStr: string = message; // Explicitly type as string after null check
  recentMessages.add(messageStr);
  
  // Remove from recent messages after expiry
  setTimeout(() => {
    console.log(`Removing expired message: "${messageStr}"`);
    recentMessages.delete(messageStr);
  }, MESSAGE_EXPIRY_TIME);
  
  // If we've reached the limit, remove the oldest messages
  if (recentMessages.size > MAX_RECENT_MESSAGES) {
    const iterator = recentMessages.values();
    const oldest = iterator.next().value;
    // Check if oldest is defined before attempting to delete
    if (oldest !== undefined) {
      console.log(`Removing oldest message: "${oldest}"`);
      recentMessages.delete(oldest);
    }
  }
}

export function NotificationProvider({ children }: { children: ReactNode }) {
  const { toast, dismiss } = useToast()

  const notify = (type: NotificationType, message: string, options = {}) => {
    // Prevent duplicates
    if (isDuplicate(message)) {
      return
    }
    
    // Track this message to prevent duplicates
    trackRecentMessage(message)
    
    switch (type) {
      case 'success':
        toast.success(message, options)
        break
      case 'error':
        toast.error(message, options)
        break
      case 'warning':
        toast.warning(message, options)
        break
      case 'info':
        toast.info(message, options)
        break
      default:
        toast({
          description: message,
          ...options,
        })
    }
  }

  const notifySuccess = (message: string, options = {}) => {
    if (isDuplicate(message)) return
    trackRecentMessage(message)
    toast.success(message, options)
  }

  const notifyError = (message: string, options = {}) => {
    console.log(`notifyError called with message: "${message}"`)
    
    // Check for duplicates
    if (isDuplicate(message)) {
      console.log(`Skipping duplicate error message: "${message}"`)
      return
    }
    
    // Track this message to prevent duplicates
    trackRecentMessage(message)
    
    // Debug that we're about to show the toast
    console.log(`Showing error toast with message: "${message}"`)
    
    // Call the toast function
    try {
      toast.error(message, options)
      console.log(`Toast.error called successfully for: "${message}"`)
    } catch (error) {
      console.error(`Error calling toast.error:`, error)
    }
  }

  const notifyWarning = (message: string, options = {}) => {
    if (isDuplicate(message)) return
    trackRecentMessage(message)
    toast.warning(message, options)
  }

  const notifyInfo = (message: string, options = {}) => {
    if (isDuplicate(message)) return
    trackRecentMessage(message)
    toast.info(message, options)
  }

  const handleApiError = (error: any, fallbackMessage = 'An unexpected error occurred') => {
    // Format the error to ensure we have a consistent structure
    const formattedError = formatError(error);
    
    // Get a user friendly message
    let errorMessage = getUserFriendlyErrorMessage(formattedError);
    
    // If we have a fallback message and the error is generic, use the fallback
    if (fallbackMessage && errorMessage === "An unexpected error occurred. Please try again later.") {
      errorMessage = fallbackMessage;
    }
    
    // Prevent duplicates
    if (isDuplicate(errorMessage)) {
      return;
    }
    
    // Track this message
    trackRecentMessage(errorMessage);
    
    // Handle based on error type
    if (isNetworkError(formattedError)) {
      toast.error("Network error. Please check your internet connection and try again.");
    } else if (isAuthError(formattedError)) {
      toast.error("Authentication required. Please log in again.");
    } else if (isValidationError(formattedError)) {
      toast.error(errorMessage || "Validation error. Please check your input.");
    } else if (formattedError.response?.status === 429) {
      toast.error("Too many requests. Please try again later.");
    } else if (formattedError.response?.status && formattedError.response.status >= 500) {
      toast.error("Server error. Please try again later.");
    } else if (formattedError.response?.data?.message) {
      // API errors with specific messages
      toast.apiError({
        message: errorMessage,
        details: formattedError.response.data.details || JSON.stringify(formattedError.response.data, null, 2),
      });
    } else {
      // Generic errors
      toast.error(errorMessage);
    }
    
    // Log error to console for debugging
    console.error('API Error:', formattedError);
  }
  
  // Function to dismiss all active notifications
  const dismissAll = () => {
    console.log("Dismissing all notifications")
    // Call the dismiss function from useToast which will dismiss all toasts
    dismiss()
    // Also clear the tracking set to reset duplicate tracking
    recentMessages.clear()
    console.log("All notifications dismissed and tracking reset")
  }

  const value = useMemo(() => ({
    notify,
    notifySuccess,
    notifyError,
    notifyWarning,
    notifyInfo,
    handleApiError,
    dismissAll
  }), [dismiss])

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  )
}

export const useNotification = () => {
  const context = useContext(NotificationContext)
  if (context === undefined) {
    throw new Error('useNotification must be used within a NotificationProvider')
  }
  return context
} 