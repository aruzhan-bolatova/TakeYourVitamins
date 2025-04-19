import { Pill } from "lucide-react"

export function SupplementHero() {
  return (
    <div className="relative flex flex-col items-center text-center py-16 space-y-8 overflow-hidden">
      {/* Background gradient for hero */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-accent/5 -z-10 rounded-2xl" />
      
      {/* Decorative pills */}
      <div className="flex space-x-4 relative">
        {/* Pill background element */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full">
          <div className="bg-accent/5 w-full h-full rounded-full blur-xl"></div>
        </div>
        
        {/* Animated pill elements */}
        <div className="relative animate-float delay-200">
          <div className="bg-primary h-16 w-6 rounded-full rotate-12 shadow-lg"></div>
        </div>
        
        <div className="relative animate-float delay-500">
          <div className="bg-primary/80 h-18 w-7 rounded-full -rotate-12 shadow-lg pulse-glow"></div>
        </div>
        
        <div className="relative animate-float delay-800">
          <div className="bg-accent h-14 w-6 rounded-full rotate-6 shadow-lg"></div>
        </div>
      </div>
      
      <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
        Take <span className="text-primary">Your</span> Vitamins
      </h1>
      
      <p className="text-xl text-muted-foreground max-w-2xl leading-relaxed">
        Search for supplements to learn about best intake practices, supplement-supplement interactions, and
        supplement-food interactions.
      </p>
    </div>
  )
}

