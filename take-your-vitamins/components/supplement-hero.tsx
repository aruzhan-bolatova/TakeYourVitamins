import { Pill } from "lucide-react"

export function SupplementHero() {
  return (
    <div className="flex flex-col items-center text-center py-12 space-y-6">
      <div className="bg-primary/10 p-4 rounded-full">
        <Pill className="h-12 w-12 text-primary" />
      </div>
      <h1 className="text-4xl font-bold tracking-tight">Take Your Vitamins</h1>
      <p className="text-xl text-muted-foreground max-w-2xl">
        Search for supplements to learn about best intake practices, supplement-supplement interactions, and
        supplement-food interactions.
      </p>
    </div>
  )
}

