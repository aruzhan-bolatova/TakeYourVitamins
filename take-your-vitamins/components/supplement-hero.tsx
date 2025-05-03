"use client"

import { ArrowRight, LogIn } from "lucide-react"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { useAuth } from "@/contexts/auth-context"

export function SupplementHero() {
  const { user } = useAuth()

  return (
    <div className="relative overflow-hidden bg-gradient-to-b from-background to-primary/5 py-20">
      <div className="absolute top-0 left-0 w-full h-full">
        <svg width="100%" height="100%" viewBox="0 0 800 800" fill="none" xmlns="http://www.w3.org/2000/svg" className="opacity-10">
          <circle cx="400" cy="400" r="200" stroke="currentColor" strokeWidth="2" />
          <circle cx="400" cy="400" r="300" stroke="currentColor" strokeWidth="2" />
          <circle cx="400" cy="400" r="400" stroke="currentColor" strokeWidth="2" />
          <circle cx="200" cy="600" r="100" fill="currentColor" fillOpacity="0.1" />
          <circle cx="600" cy="200" r="70" fill="currentColor" fillOpacity="0.1" />
          <circle cx="700" cy="500" r="50" fill="currentColor" fillOpacity="0.1" />
          <circle cx="200" cy="200" r="60" fill="currentColor" fillOpacity="0.1" />
        </svg>
      </div>

      <div className="relative z-10 mx-auto max-w-6xl px-6 lg:px-8">
        <div className="flex flex-col lg:flex-row items-center gap-12">
          <div className="flex-1 text-center lg:text-left">
            <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight mb-8">
              <span className="block">Find your</span>
              <span className="block text-primary">vitamins</span>
              <span className="block">and</span>
              <span className="block text-primary">supplements</span>
            </h1>
            <p className="text-xl font-medium text-muted-foreground mb-8 max-w-2xl mx-auto lg:mx-0">
              Search our database of thousands of vitamins and track your daily
              supplement intake
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <Button size="lg" asChild>
                <Link href="/supplements/search">
                  Find Supplements <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              
              {user ? (
                <Button size="lg" variant="outline" asChild>
                  <Link href="/dashboard/tracker">
                    Track Intake
                  </Link>
                </Button>
              ) : (
                <Button size="lg" variant="outline" asChild>
                  <Link href="/login">
                    <LogIn className="mr-2 h-4 w-4" />
                    Log in to Track
                  </Link>
                </Button>
              )}
            </div>
            
            {!user && (
              <div className="mt-6 p-4 bg-primary/10 rounded-lg text-sm">
                <p className="font-medium">Create an account to track your supplements, get intake reminders, and monitor your health journey.</p>
              </div>
            )}
          </div>
          <div className="flex-1 relative">
            <div className="w-full h-full flex items-center justify-center">
              <div className="relative w-[300px] h-[300px] md:w-[400px] md:h-[400px]">
                <div className="absolute inset-0 animate-float">
                  <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
                    <path fill="var(--primary)" d="M42.8,-65.3C54.9,-56.7,63.8,-42.8,70.4,-27.6C77,-12.4,81.3,4.1,77.7,19.3C74.1,34.5,62.7,48.3,48.9,58.9C35.1,69.5,19,76.8,2.2,74.9C-14.7,73,-32.3,61.8,-46.5,49.1C-60.7,36.3,-71.5,22,-74.7,6.4C-77.9,-9.2,-73.5,-26.1,-63.7,-38.6C-53.9,-51.1,-38.7,-59.2,-24,-65.6C-9.3,-72,5,-76.7,19.6,-74.7C34.2,-72.7,30.6,-74,42.8,-65.3Z" transform="translate(100 100)" />
                  </svg>
                </div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="grid grid-cols-3 grid-rows-3 gap-4">
                    {['A', 'B', 'C', 'D', 'E', 'Zinc', 'Iron', 'Mg', 'Ca'].map((vitamin, i) => (
                      <div key={i} 
                        className="w-16 h-16 md:w-20 md:h-20 rounded-full bg-white shadow-lg flex items-center justify-center font-bold text-xs md:text-sm"
                        style={{ 
                          animation: `float ${3 + (i * 0.2)}s ease-in-out infinite`,
                          animationDelay: `${i * 0.1}s`
                        }}
                      >
                        {vitamin}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

