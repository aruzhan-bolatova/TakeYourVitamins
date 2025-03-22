export interface Supplement {
    id: string
    name: string
    aliases: string[]
    category: string
    description: string
    intakePractices: {
      dosage: string
      timing: string
      specialInstructions: string
    }
    supplementInteractions: {
      supplementName: string
      severity: "low" | "medium" | "high"
      effect: string
      recommendation?: string
    }[]
    foodInteractions: {
      foodName: string
      effect: string
      description: string
      recommendation?: string
    }[]
  }
  
  