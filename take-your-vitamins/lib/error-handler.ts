import { toast } from "@/components/ui/use-toast"
import React from "react"
import { ToastAction } from "@/components/ui/toast"

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
  if (!isOnline()) {
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

  // Extract error message
  let errorMessage = defaultMessage;
  let errorDetails = "";
  
  if (typeof error === 'string') {
    errorMessage = error;
  } else if (error instanceof Error) {
    errorMessage = error.message;
    errorDetails = error.stack || "";
  } else if (error?.message) {
    errorMessage = error.message;
  } else if (error?.error) {
    errorMessage = error.error;
  } else if (error?.statusText) {
    errorMessage = error.statusText;
  }

  // Extract status code 
  const statusCode = error?.status || error?.statusCode;

  // Handle known authentication errors
  if (context === "Authentication" && statusCode === 401) {
    errorMessage = "Invalid email or password. Please try again.";
  } else if (context === "Authentication" && statusCode === 403) {
    errorMessage = "Your account doesn't have permission to access this resource.";
  } else if (context === "Authentication" || context === "Registration") {
    if (error?.statusText === "UNAUTHORIZED") {
      errorMessage = "Invalid email or password. Please try again.";
    } else if (statusCode === 400) {
      errorMessage = "Please check your information and try again.";
    } else if (statusCode === 409) {
      errorMessage = "An account with this email already exists.";
    }
  }

  // Add context if provided
  if (context && !errorMessage.startsWith(context)) {
    errorMessage = `${context}: ${errorMessage}`;
  }

  // Format error details for better readability
  if (!errorDetails) {
    try {
      if (typeof error === 'object' && error !== null) {
        errorDetails = JSON.stringify(error, null, 2);
      } else {
        errorDetails = String(error);
      }
    } catch {
      errorDetails = "Error details could not be displayed";
    }
  }

  // Reporting for analytics (placeholder for future implementation)
  if (reportToAnalytics) {
    // In the future, could implement analytics reporting here
    console.info("Error would be reported to analytics:", {
      message: errorMessage,
      statusCode,
      details: errorDetails
    });
  }

  // Show toast notification
  if (showToast) {
    // Choose the appropriate error message based on status code
    if (statusCode === 401) {
      toast.error("Authentication required. Please log in again.");
    } else if (statusCode === 403) {
      toast.error("You don't have permission to perform this action.");
    } else if (statusCode === 404) {
      toast.error("The requested resource was not found.");
    } else if (statusCode === 422 || statusCode === 400) {
      toast.error(errorMessage || "Validation error. Please check your input.");
    } else if (statusCode === 429) {
      toast.error("Too many requests. Please try again later.");
    } else if (statusCode >= 500) {
      toast.error("Server error. Please try again later.");
    } else {
      toast.error(errorMessage);
    }
  }

  // Log to console
  if (logToConsole) {
    const errorGroup = context || "Application Error";
    console.groupCollapsed(`${errorGroup}: ${errorMessage}`);
    console.error("Error details:", error);
    if (statusCode) console.info("Status code:", statusCode);
    if (errorDetails) console.info("Stack trace:", errorDetails);
    console.groupEnd();
  }

  // Return the error message for use in UI or further processing
  return errorMessage;
}

/**
 * This function enhances a fetch request with error handling and AJAX-like features
 * @param url - The URL to fetch
 * @param options - Fetch options
 * @returns The response data
 */
export async function fetchWithErrorHandling<T>(
  url: string, 
  options?: RequestInit & { 
    context?: string, 
    showLoadingToast?: boolean,
    retryCount?: number
  }
): Promise<T> {
  const { context, showLoadingToast = false, retryCount = 0, ...fetchOptions } = options || {};
  let loadingToast: any = null;
  
  try {
    // Check if online first
    if (!isOnline()) {
      throw new Error("You are currently offline. Please check your connection and try again.");
    }
    
    // Show loading toast if requested
    if (showLoadingToast) {
      loadingToast = toast.info("Loading...");
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
    
    // We just let the loading toast auto-disappear
    // No need to dismiss it manually
    
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
    // We just let the loading toast auto-disappear
    // No need to dismiss it manually
    
    // Special handling for timeout errors
    if (error instanceof Error && error.name === 'AbortError') {
      const timeoutError = new Error("The request took too long to complete. Please try again.");
      handleError(timeoutError, {
        context,
        retry: () => fetchWithErrorHandling(url, {
          ...options,
          retryCount: retryCount + 1
        }),
        retryCount
      });
      throw timeoutError;
    }
    
    // Handle using our standardized error handler
    handleError(error, {
      context,
      retry: () => fetchWithErrorHandling(url, {
        ...options,
        retryCount: retryCount + 1
      }),
      retryCount
    });
    
    // Re-throw the error for the calling code to handle
    throw error;
  }
} 