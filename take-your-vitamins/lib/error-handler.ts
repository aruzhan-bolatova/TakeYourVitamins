import { toast } from "@/components/ui/use-toast"
import React from "react"
import { ToastAction } from "@/components/ui/toast"
import { 
  formatError, 
  getUserFriendlyErrorMessage, 
  isNetworkError, 
  isAuthError, 
  isValidationError
} from "@/lib/error-handling"
import { useNotification } from "@/contexts/notification-context"

type ErrorOptions = {
  showToast?: boolean
  logToConsole?: boolean
  defaultMessage?: string
  retry?: () => Promise<any>
  context?: string // Add context for better error messages
  reportToAnalytics?: boolean // For future analytics integration
  retryCount?: number // Track retry count to prevent infinite recursion
}

// Maximum number of retry attempts to prevent infinite recursion
const MAX_RETRY_LIMIT = 3;

// Helper to check if the browser is online
const isOnline = (): boolean => {
  return typeof navigator !== 'undefined' && typeof navigator.onLine === 'boolean'
    ? navigator.onLine
    : true;
};

// For use in components that don't have access to the notification context
// We keep the toast-based implementation as a fallback
/**
 * This function handles errors in a standardized way across the application
 * @param error - The error to handle
 * @param options - Options for handling the error
 * @returns The error message
 */
export function handleError(error: any, options: ErrorOptions = {}): string {
  const {
    showToast = true,
    logToConsole = true,
    defaultMessage = "An unexpected error occurred",
    retry,
    context = "",
    reportToAnalytics = false,
    retryCount = 0
  } = options

  // Handle offline status specially
  if (!isOnline() || isNetworkError(error)) {
    const offlineMessage = "You appear to be offline. Please check your internet connection.";
    
    if (showToast) {
      // Check if we've reached the retry limit
      if (retryCount >= MAX_RETRY_LIMIT) {
        toast.error("Maximum retry attempts reached. Please try again when you're back online.");
        
        if (logToConsole) {
          console.warn("Maximum retry attempts reached while offline");
        }
        
        return offlineMessage;
      }
      
      // Show simple toast without action to avoid complexity
      toast.error(offlineMessage);
    }
    
    if (logToConsole) {
      console.error(`Network Error: User is offline (retry attempt: ${retryCount}/${MAX_RETRY_LIMIT})`);
    }
    
    return offlineMessage;
  }

  // Create a properly formatted error
  const formattedError = formatError(error);
  let errorMessage = getUserFriendlyErrorMessage(formattedError);
  
  // Override with default message if provided
  if (defaultMessage && errorMessage === "An unexpected error occurred. Please try again later.") {
    errorMessage = defaultMessage;
  }

  // Add context if provided
  if (context && !errorMessage.startsWith(context)) {
    errorMessage = `${context}: ${errorMessage}`;
  }

  // Reporting for analytics (placeholder for future implementation)
  if (reportToAnalytics) {
    // In the future, could implement analytics reporting here
    console.info("Error would be reported to analytics:", {
      message: errorMessage,
      statusCode: formattedError.response?.status,
      // Only include stack if it exists on the original error object
      details: error instanceof Error && error.stack ? error.stack : undefined
    });
  }

  // Show toast notification
  if (showToast) {
    if (isAuthError(formattedError)) {
      toast.error("Authentication required. Please log in again.");
    } else if (isValidationError(formattedError)) {
      toast.error(errorMessage || "Validation error. Please check your input.");
    } else if (formattedError.response?.status === 429) {
      toast.error("Too many requests. Please try again later.");
    } else if (formattedError.response?.status && formattedError.response.status >= 500) {
      toast.error("Server error. Please try again later.");
    } else {
      toast.error(errorMessage);
    }
  }

  // Log to console
  if (logToConsole) {
    const errorGroup = context || "Application Error";
    console.groupCollapsed(`${errorGroup}: ${errorMessage}`);
    console.error("Error details:", formattedError);
    if (formattedError.response?.status) console.info("Status code:", formattedError.response.status);
    // Only log stack trace if it exists on the original error
    if (error instanceof Error && error.stack) console.info("Stack trace:", error.stack);
    console.groupEnd();
  }

  // Return the error message for use in UI or further processing
  return errorMessage;
}

/**
 * This function enhances a fetch request with error handling and AJAX-like features
 * Using the notification context when available
 * @param url - The URL to fetch
 * @param options - Fetch options
 * @returns The response data
 */
export async function fetchWithErrorHandling<T>(
  url: string, 
  options?: RequestInit & { 
    context?: string, 
    showLoadingToast?: boolean,
    retryCount?: number,
    notification?: ReturnType<typeof useNotification>
  }
): Promise<T> {
  const { context, showLoadingToast = false, retryCount = 0, notification, ...fetchOptions } = options || {};
  
  try {
    // Check if online first
    if (!isOnline()) {
      throw new Error("You are currently offline. Please check your connection and try again.");
    }
    
    // Show loading toast if requested - use notification context if available
    if (showLoadingToast) {
      if (notification) {
        notification.notifyInfo("Loading...");
      } else {
        toast.info("Loading...");
      }
    }
    
    // Add timeout to the fetch request
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
    
    const response = await fetch(url, {
      ...fetchOptions,
      signal: controller.signal
    });
    
    // Clear the timeout
    clearTimeout(timeoutId);
    
    // No need to dismiss loading notifications - they auto-dismiss
    
    if (!response.ok) {
      // Attempt to parse error response
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        // If parsing fails, create an error object with status info
        errorData = {
          status: response.status,
          statusText: response.statusText,
        };
      }
      
      // Add response status to error data
      errorData.status = response.status;
      errorData.statusText = response.statusText;
      
      throw errorData;
    }
    
    const data = await response.json();
    return data as T;
  } catch (error: unknown) {
    // No need to dismiss loading notifications
    
    // Special handling for timeout errors
    if (error instanceof Error && error.name === 'AbortError') {
      const timeoutError = new Error("The request took too long to complete. Please try again.");
      
      if (notification) {
        notification.notifyError("The request took too long to complete. Please try again.");
      } else {
        handleError(timeoutError, {
          context,
          retry: () => fetchWithErrorHandling(url, {
            ...options,
            retryCount: retryCount + 1
          }),
          retryCount
        });
      }
      
      throw timeoutError;
    }
    
    // Use notification context if available
    if (notification) {
      notification.handleApiError(error, context ? `${context}: An error occurred` : undefined);
    } else {
      // Fall back to handleError for components without notification context
      handleError(error, {
        context,
        retry: retryCount < MAX_RETRY_LIMIT
          ? () => fetchWithErrorHandling(url, {
              ...options,
              retryCount: retryCount + 1
            })
          : undefined,
        retryCount
      });
    }
    
    throw error;
  }
} 