"use client"

import React, { Component, ErrorInfo, ReactNode } from 'react'
import { ErrorDisplay } from './ui/error-display'
import { ErrorBoundaryProps } from '@/lib/error-handling'

interface Props {
  children: ReactNode
  fallback?: (props: ErrorBoundaryProps) => ReactNode
  onError?: (error: Error, info: ErrorInfo) => void
}

interface State {
  hasError: boolean
  error: Error | null
}

/**
 * Error boundary component to catch JavaScript errors in children components
 * and display a fallback UI instead of crashing the whole app
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log the error to an error reporting service
    console.error('Error caught by ErrorBoundary:', error, errorInfo)
    
    // Call onError if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo)
    }
  }

  resetErrorBoundary = () => {
    this.setState({ hasError: false, error: null })
  }

  render() {
    if (this.state.hasError && this.state.error) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback({
          error: this.state.error,
          resetErrorBoundary: this.resetErrorBoundary
        })
      }

      // Default fallback UI
      return (
        <div className="p-4">
          <ErrorDisplay
            severity="error"
            message="Something went wrong in this component."
            details={this.state.error.stack}
            onRetry={this.resetErrorBoundary}
          />
        </div>
      )
    }

    return this.props.children
  }
}

/**
 * Default error fallback component that can be used with ErrorBoundary
 */
export function DefaultErrorFallback({ error, resetErrorBoundary }: ErrorBoundaryProps) {
  return (
    <div className="p-4 max-w-xl mx-auto">
      <ErrorDisplay
        title="Something went wrong"
        message={error.message || "An unexpected error occurred"}
        details={error.stack}
        onRetry={resetErrorBoundary}
        severity="error"
      />
    </div>
  )
} 