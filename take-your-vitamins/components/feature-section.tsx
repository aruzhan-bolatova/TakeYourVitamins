"use client"

import { Search, Zap, Clock, Bell, LogIn, UserPlus } from "lucide-react"
import { useAuth } from "@/contexts/auth-context"
import { Button } from "@/components/ui/button"
import Link from "next/link"

interface FeatureCardProps {
  title: string
  description: string
  icon: React.ReactNode
  locked?: boolean
}

function FeatureCard({ title, description, icon, locked = false }: FeatureCardProps) {
  return (
    <div className={`bg-card/50 backdrop-blur-sm rounded-xl p-8 shadow-sm border border-border/30 hover:shadow-md transition-all duration-300 h-full ${locked ? 'relative' : ''}`}>
      <div className="bg-primary/10 text-primary rounded-full w-14 h-14 flex items-center justify-center mb-6">
        {icon}
      </div>
      <h3 className="text-xl font-semibold mb-4">{title}</h3>
      <p className="text-muted-foreground">{description}</p>
      
      {locked && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-card/80 backdrop-blur-sm rounded-xl">
          <p className="text-sm font-medium mb-2">Create an account to access</p>
          <LogIn className="h-6 w-6 text-primary" />
        </div>
      )}
    </div>
  )
}

export function FeatureSection() {
  const { user } = useAuth()
  
  const features = [
    {
      title: "Search Supplements",
      description: "Find detailed information on any supplement in our database.",
      icon: <Search className="h-6 w-6" />,
      locked: false
    },
    {
      title: "Check Interactions",
      description: "Learn about potential interactions between different supplements.",
      icon: <Zap className="h-6 w-6" />,
      locked: false
    },
    {
      title: "Track Daily Intake",
      description: "Keep track of which supplements you take and when.",
      icon: <Clock className="h-6 w-6" />,
      locked: !user
    },
    {
      title: "Set Reminders",
      description: "Never miss a dose with our reminder notifications.",
      icon: <Bell className="h-6 w-6" />,
      locked: !user
    }
  ]

  return (
    <section className="py-20 container">
      <div className="text-center mb-16">
        <h2 className="text-3xl md:text-4xl font-bold mb-4">What You Can Do</h2>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Our platform offers various features to help you manage your supplements effectively
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {features.map((feature, index) => (
          <FeatureCard
            key={index}
            title={feature.title}
            description={feature.description}
            icon={feature.icon}
            locked={feature.locked}
          />
        ))}
      </div>
      
      {!user && (
        <div className="mt-16 bg-primary/10 rounded-xl p-8 text-center">
          <h3 className="text-2xl font-bold mb-4">Ready to track your supplements?</h3>
          <p className="text-muted-foreground mb-6 max-w-xl mx-auto">
            Create an account to access all features, track your supplement intake, and get personalized recommendations.
          </p>
          <div className="flex justify-center gap-4">
            <Button asChild>
              <Link href="/signup">
                <UserPlus className="mr-2 h-5 w-5" />
                Sign Up
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href="/login">
                <LogIn className="mr-2 h-5 w-5" />
                Log In
              </Link>
            </Button>
          </div>
        </div>
      )}
    </section>
  )
} 