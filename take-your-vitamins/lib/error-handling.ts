/**
 * Error handling utilities for the application
 */

interface FormattedError {
  message?: string;
  code?: string;
  status?: number;
  response?: {
    data?: any;
    status?: number;
    statusText?: string;
  };
  isNetworkError?: boolean;
  isAuthError?: boolean;
  isValidationError?: boolean;
}

/**
 * Formats an error into a consistent structure
 */
export function formatError(error: any): FormattedError {
  if (!error) {
    return { message: 'Unknown error' };
  }

  // If it's already a formatted error, return it
  if (error.isNetworkError || error.isAuthError || error.isValidationError) {
    return error;
  }

  let formattedError: FormattedError = {
    message: error.message,
    code: error.code,
    status: error.status,
    response: error.response,
  };

  // Check for network errors
  if (error.message === 'Network Error' || error.code === 'ECONNABORTED' || !navigator.onLine) {
    formattedError.isNetworkError = true;
  }

  // Check for authentication errors
  if (error.response?.status === 401 || error.response?.status === 403) {
    formattedError.isAuthError = true;
  }

  // Check for validation errors
  if (error.response?.status === 400 || 
      error.response?.status === 422 ||
      error.response?.data?.errors) {
    formattedError.isValidationError = true;
  }

  return formattedError;
}

/**
 * Checks if an error is a network error
 */
export function isNetworkError(error: FormattedError): boolean {
  return !!error.isNetworkError;
}

/**
 * Checks if an error is an authentication error
 */
export function isAuthError(error: FormattedError): boolean {
  return !!error.isAuthError;
}

/**
 * Checks if an error is a validation error
 */
export function isValidationError(error: FormattedError): boolean {
  return !!error.isValidationError;
}

/**
 * Gets a user-friendly error message from an error
 */
export function getUserFriendlyErrorMessage(error: FormattedError): string {
  if (!error) {
    return "An unexpected error occurred. Please try again later.";
  }

  if (error.isNetworkError) {
    return "Network error. Please check your internet connection and try again.";
  }

  if (error.isAuthError) {
    return error.response?.status === 401 
      ? "Authentication required. Please log in again."
      : "You don't have permission to perform this action.";
  }

  if (error.isValidationError) {
    // Extract validation error messages if available
    if (error.response?.data?.errors) {
      const errors = error.response.data.errors;
      if (typeof errors === 'string') {
        return errors;
      } else if (Array.isArray(errors)) {
        return errors.join('. ');
      } else if (typeof errors === 'object') {
        const messages: string[] = [];
        for (const field in errors) {
          if (Array.isArray(errors[field])) {
            messages.push(`${field}: ${errors[field].join(', ')}`);
          } else if (typeof errors[field] === 'string') {
            messages.push(`${field}: ${errors[field]}`);
          }
        }
        return messages.join('. ');
      }
    }
    
    return error.response?.data?.message || "Please check your input and try again.";
  }

  // Prioritize these sources for error messages
  return (
    error.message ||
    error.response?.data?.message ||
    error.response?.statusText ||
    "An unexpected error occurred. Please try again later."
  );
}

/**
 * Error boundary fallback component props interface
 */
export interface ErrorBoundaryProps {
  error: Error;
  resetErrorBoundary: () => void;
}

/**
 * Safely execute a function and return result or error
 */
export async function tryCatch<T>(fn: () => Promise<T>): Promise<[T | null, FormattedError | null]> {
  try {
    const data = await fn();
    return [data, null];
  } catch (error) {
    return [null, formatError(error)];
  }
} 