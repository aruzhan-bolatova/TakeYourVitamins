"use client"

import React from "react"
import { SiteHeader } from "@/components/site-header"
import { SiteFooter } from "@/components/site-footer"
import { useAuth } from "@/contexts/auth-context"

export function RootLayoutClient({ children }: { children: React.ReactNode }) {
  const { user } = useAuth()

  return (
    <div className="relative flex min-h-screen flex-col">
      {!user && (
        <div className="bg-primary/20 p-2 text-center text-sm">
          <p>
            Create an account to track supplements and monitor your health!{" "}
            <a href="/login" className="font-bold underline">
              Login or Sign up
            </a>
          </p>
        </div>
      )}
      
      <SiteHeader />
      <main className="flex-1">{children}</main>
      <SiteFooter />
    </div>
  )
} 