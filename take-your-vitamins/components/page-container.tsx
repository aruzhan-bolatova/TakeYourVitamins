"use client"

import React from "react"
import { cn } from "@/lib/utils"

interface PageContainerProps {
  children: React.ReactNode
  className?: string
  withGradient?: boolean
}

export function PageContainer({ 
  children, 
  className,
  withGradient = false
}: PageContainerProps) {
  return (
    <div className={cn(
      "relative w-full",
      withGradient && "before:absolute before:inset-0 before:bg-gradient-to-br before:from-primary/10 before:to-background before:rounded-xl before:opacity-50 before:-z-10",
      className
    )}>
      <div className="relative z-10 space-y-6 px-4 py-6 md:px-6 lg:px-8">
        {children}
      </div>
      
      {withGradient && (
        <div className="absolute top-0 right-0 -z-10 h-72 w-72 rounded-full bg-primary/20 blur-3xl" />
      )}
    </div>
  )
} 