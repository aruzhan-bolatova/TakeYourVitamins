"use client"

import Link from "next/link"
import { Pill, Github } from "lucide-react"
import { useAuth } from "@/contexts/auth-context"

export function Footer() {
  const { user } = useAuth()
  
  return (
    <footer className="bg-card/30 border-t py-12 mt-10">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="md:col-span-1">
            <Link href="/" className="flex items-center gap-2 mb-4">
              <div className="bg-primary/10 p-2 rounded-full">
                <Pill className="h-5 w-5 text-primary" />
              </div>
              <span className="font-bold text-lg">Take Your Vitamins</span>
            </Link>
            <p className="text-sm text-muted-foreground mb-4">
              Find information about supplements, their interactions, and track your daily intake.
            </p>
            <div className="flex items-center gap-4">
              <a 
                href="https://github.com" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-muted-foreground hover:text-primary transition-colors"
              >
                <Github className="h-5 w-5" />
                <span className="sr-only">GitHub</span>
              </a>
            </div>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4">Features</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/supplements/search" className="text-muted-foreground hover:text-primary transition-colors">
                  Search Supplements
                </Link>
              </li>
              <li>
                <Link href="/dashboard/tracker" className="text-muted-foreground hover:text-primary transition-colors">
                  Track Intake
                </Link>
              </li>
              <li>
                <Link href="/settings" className="text-muted-foreground hover:text-primary transition-colors">
                  Set Reminders
                </Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4">Resources</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/dashboard/symptoms" className="text-muted-foreground hover:text-primary transition-colors">
                  Symptom Tracker
                </Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4">Account</h3>
            <ul className="space-y-2">
              {!user && (
                <>
                  <li>
                    <Link href="/login" className="text-muted-foreground hover:text-primary transition-colors">
                      Login
                    </Link>
                  </li>
                  <li>
                    <Link href="/signup" className="text-muted-foreground hover:text-primary transition-colors">
                      Sign Up
                    </Link>
                  </li>
                </>
              )}
              <li>
                <Link href="/profile" className="text-muted-foreground hover:text-primary transition-colors">
                  Profile
                </Link>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="border-t mt-8 pt-6 text-sm text-muted-foreground text-center">
          <p>&copy; {new Date().getFullYear()} Take Your Vitamins. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
} 