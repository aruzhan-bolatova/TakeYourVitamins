"use client"

import { SearchBar } from "@/components/search-bar"
import { Pill, Zap, Clock, PlusCircle, Apple, ArrowRight, Search, LogIn } from "lucide-react"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import Image from "next/image"
import { useAuth } from "@/contexts/auth-context"

export default function Home() {
  const { user } = useAuth()

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden py-20">
        {/* Background elements */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-accent/5 -z-10" />
        
        {/* Decorative pill elements */}
        <div className="absolute top-1/4 right-1/4 animate-float opacity-10 delay-100">
          <Pill className="h-36 w-36 text-primary rotate-45" />
        </div>
        <div className="absolute bottom-1/3 right-20 animate-float opacity-10 delay-300">
          <Pill className="h-20 w-20 text-accent rotate-12" />
        </div>
        
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row items-center gap-10">
            <div className="flex-1 space-y-8">
              <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight">
                Find your <span className="text-primary">vitamins</span> and <span className="text-primary">supplements</span>
              </h1>
              
              <p className="text-xl text-muted-foreground max-w-2xl">
                Search our database of thousands of vitamins and track your daily supplement intake
              </p>
              
              <div className="pt-4">
        <SearchBar />
      </div>
              
              <div className="text-sm text-muted-foreground">
                Try searching for: Vitamin D, Omega-3, Zinc, Magnesium...
              </div>
              
              {!user && (
                <div className="flex flex-wrap gap-4 pt-4">
                  <Link href="/signup">
                    <Button size="lg" className="gap-2 bg-primary text-primary-foreground hover:bg-primary/90">
                      Sign Up <ArrowRight className="h-4 w-4" />
                    </Button>
                  </Link>
                  <Link href="/login">
                    <Button size="lg" variant="outline" className="gap-2 border-primary/50 text-primary hover:bg-primary/10">
                      Log In <LogIn className="h-4 w-4" />
                    </Button>
                  </Link>
                </div>
              )}
              
              {user && (
                <div className="flex flex-wrap gap-4 pt-4">
                  <Link href="/dashboard">
                    <Button size="lg" className="gap-2 bg-primary text-primary-foreground hover:bg-primary/90">
                      Dashboard <ArrowRight className="h-4 w-4" />
                    </Button>
                  </Link>
                </div>
              )}
            </div>
            
            <div className="flex-1 relative">
              {/* Vitamin pill illustrations */}
              <div className="relative h-72 w-full">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
                  <div className="bg-accent/10 w-72 h-36 rounded-full"></div>
                </div>
                
                {/* Orange pill */}
                <div className="absolute top-1/4 left-1/2 transform -translate-x-1/2 animate-float delay-100">
                  <div className="bg-primary h-24 w-10 rounded-full rotate-45 shadow-lg pulse-glow"></div>
                </div>
                
                {/* Orange pill 2 */}
                <div className="absolute top-1/3 right-1/4 animate-float delay-300">
                  <div className="bg-primary h-16 w-8 rounded-full rotate-12 shadow-md"></div>
                </div>
                
                {/* Amber pill */}
                <div className="absolute bottom-1/4 left-1/3 animate-float delay-500">
                  <div className="bg-accent h-20 w-8 rounded-full -rotate-12 shadow-md"></div>
                </div>
                
                {/* Orange rounded pill */}
                <div className="absolute bottom-1/3 right-1/3 animate-float delay-700">
                  <div className="bg-primary/80 h-10 w-16 rounded-full shadow-md"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
      
      {/* Features Section */}
      <section className="py-20 bg-card/50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-16">What You Can Do</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-background rounded-lg p-8 shadow-md hover:shadow-lg transition-shadow border border-border/50">
              <div className="bg-primary/10 p-4 rounded-full w-fit mb-6">
                <Search className="h-8 w-8 text-primary" />
              </div>
              <h3 className="text-xl font-bold mb-3">Search Supplements</h3>
              <p className="text-muted-foreground">Find detailed information on any supplement in our database.</p>
            </div>
            
            <div className="bg-background rounded-lg p-8 shadow-md hover:shadow-lg transition-shadow border border-border/50">
              <div className="bg-primary/10 p-4 rounded-full w-fit mb-6">
                <Zap className="h-8 w-8 text-primary" />
              </div>
              <h3 className="text-xl font-bold mb-3">Check Interactions</h3>
              <p className="text-muted-foreground">Learn about potential interactions between different supplements.</p>
            </div>
            
            <div className="bg-background rounded-lg p-8 shadow-md hover:shadow-lg transition-shadow border border-border/50">
              <div className="bg-primary/10 p-4 rounded-full w-fit mb-6">
                <Clock className="h-8 w-8 text-primary" />
              </div>
              <h3 className="text-xl font-bold mb-3">Track Daily Intake</h3>
              <p className="text-muted-foreground">Keep track of which supplements you take and when.</p>
            </div>
            
            <div className="bg-background rounded-lg p-8 shadow-md hover:shadow-lg transition-shadow border border-border/50">
              <div className="bg-primary/10 p-4 rounded-full w-fit mb-6">
                <Apple className="h-8 w-8 text-primary" />
              </div>
              <h3 className="text-xl font-bold mb-3">Set Reminders</h3>
              <p className="text-muted-foreground">Never miss a dose with our reminder notifications.</p>
            </div>
          </div>
        </div>
      </section>
      
      {/* CTA Section - Only show when not logged in */}
      {!user && (
        <section className="py-16">
          <div className="container mx-auto px-4 text-center">
            <div className="bg-card rounded-lg p-10 shadow-md border border-border/50 max-w-3xl mx-auto">
              <h2 className="text-3xl font-bold mb-6">Ready to optimize your supplement routine?</h2>
              <p className="text-xl text-muted-foreground mb-8">
                Log in to track your supplements and get personalized recommendations.
              </p>
              <div className="flex flex-wrap justify-center gap-6">
                <Link href="/login">
                  <Button size="lg" className="bg-primary text-primary-foreground hover:bg-primary/90">
                    Log In <LogIn className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
                <Link href="/signup">
                  <Button size="lg" variant="outline" className="border-primary/50 text-primary hover:bg-primary/10">
                    Sign Up <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </section>
      )}
    </div>
  )
}