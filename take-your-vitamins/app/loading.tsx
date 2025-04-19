import { Pill } from "lucide-react"

export default function Loading() {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-background/90 backdrop-blur-sm z-50">
      <div className="flex flex-col items-center">
        <div className="relative">
          {/* Animated Pill Icons */}
          <div className="animate-spin-slow absolute -left-10 opacity-40">
            <Pill className="h-8 w-8 rotate-45 text-primary" />
          </div>
          <div className="animate-spin-slow absolute -right-10 opacity-40">
            <Pill className="h-8 w-8 rotate-12 text-accent" />
          </div>
          <div className="animate-spin-slow absolute -top-10 opacity-40">
            <Pill className="h-8 w-8 -rotate-45 text-primary" />
          </div>
          <div className="animate-spin-slow absolute -bottom-10 opacity-40">
            <Pill className="h-8 w-8 -rotate-12 text-accent" />
          </div>
          
          {/* Center Pill */}
          <div className="pulse-glow">
            <div className="bg-primary h-20 w-8 rounded-full animate-bounce shadow-lg"></div>
          </div>
        </div>
        <p className="mt-6 text-lg font-medium text-primary">Loading...</p>
      </div>
    </div>
  )
}