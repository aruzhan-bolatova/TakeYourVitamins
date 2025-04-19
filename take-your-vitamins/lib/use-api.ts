"use client";

import { useState, useCallback } from 'react';
import { useNotification } from '@/contexts/notification-context';
import { tryCatch, formatError } from '@/lib/error-handling';

interface UseApiOptions {
  onSuccess?: (data: any) => void;
  onError?: (error: any) => void;
  successMessage?: string;
  errorMessage?: string;
  showSuccessToast?: boolean;
  showErrorToast?: boolean;
}

/**
 * Custom hook for making API calls with built-in error handling and loading state
 */
export function useApi<T = any>(
  options: UseApiOptions = {}
) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [data, setData] = useState<T | null>(null);
  
  const notification = useNotification();
  
  const {
    onSuccess,
    onError,
    successMessage,
    errorMessage = 'An error occurred while processing your request',
    showSuccessToast = true,
    showErrorToast = true,
  } = options;
  
  const execute = useCallback(
    async <R = T>(
      apiCall: () => Promise<R>,
      callOptions: {
        onSuccess?: (data: R) => void;
        onError?: (error: any) => void;
        successMessage?: string;
        errorMessage?: string;
        showSuccessToast?: boolean;
        showErrorToast?: boolean;
      } = {}
    ): Promise<[R | null, Error | null]> => {
      // Reset state
      setIsLoading(true);
      setError(null);
      
      // Merge options
      const mergedOptions = {
        onSuccess: callOptions.onSuccess || onSuccess,
        onError: callOptions.onError || onError,
        successMessage: callOptions.successMessage || successMessage,
        errorMessage: callOptions.errorMessage || errorMessage,
        showSuccessToast:
          callOptions.showSuccessToast !== undefined
            ? callOptions.showSuccessToast
            : showSuccessToast,
        showErrorToast:
          callOptions.showErrorToast !== undefined
            ? callOptions.showErrorToast
            : showErrorToast,
      };
      
      try {
        // Execute API call
        const [result, apiError] = await tryCatch<R>(apiCall);
        
        if (apiError) {
          throw apiError;
        }
        
        if (result !== null) {
          // Set data and call success callback
          setData(result as unknown as T);
          
          if (mergedOptions.onSuccess) {
            mergedOptions.onSuccess(result);
          }
          
          // Show success toast if enabled and message is provided
          if (mergedOptions.showSuccessToast && mergedOptions.successMessage) {
            notification.notifySuccess(mergedOptions.successMessage);
          }
          
          return [result, null];
        }
        
        return [null, null];
      } catch (error) {
        // Format and handle error
        const formattedError = formatError(error);
        setError(formattedError);
        
        // Call error callback
        if (mergedOptions.onError) {
          mergedOptions.onError(formattedError);
        }
        
        // Show error toast if enabled
        if (mergedOptions.showErrorToast) {
          notification.handleApiError(
            formattedError,
            mergedOptions.errorMessage
          );
        }
        
        return [null, formattedError];
      } finally {
        setIsLoading(false);
      }
    },
    [
      notification,
      onSuccess,
      onError,
      successMessage,
      errorMessage,
      showSuccessToast,
      showErrorToast,
    ]
  );
  
  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setIsLoading(false);
  }, []);
  
  return {
    isLoading,
    error,
    data,
    execute,
    reset,
  };
}

/**
 * Hook for single API call - useful for data fetching
 */
export function useFetch<T = any>(
  fetchFn: () => Promise<T>,
  options: UseApiOptions & { 
    skip?: boolean;
    deps?: any[];
  } = {}
) {
  const { skip = false, deps = [], ...apiOptions } = options;
  const { isLoading, error, data, execute } = useApi<T>(apiOptions);
  
  const fetchData = useCallback(async () => {
    if (skip) return;
    await execute(fetchFn);
  }, [execute, fetchFn, skip, ...(deps || [])]);
  
  // This would normally use useEffect to trigger the fetch
  // but since this is for React server components/server actions
  // we just return the fetchData function for manual triggering
  
  return {
    isLoading,
    error,
    data,
    fetchData,
  };
} 