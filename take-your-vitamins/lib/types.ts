export type Supplement = {
  _id: string
  supplementId: string
  name: string
  aliases: string[]
  description: string
  intakePractices: {
    dosage?: string
    timing?: string
    specialInstructions?: string
  }
  scientificDetails: {
    benefits?: string[]
    sideEffects?: string[]
    studies?: {
      title: string
      journal: string
      year: number
      summary: string
    }[]
  }
  category: string
  updatedAt: string | null
}

export type Interaction = {
  _id: string
  interactionId: string
  interactionType: "Supplement-Supplement" | "Supplement-Food"
  effect: string
  description: string
  recommendation: string
  severity?: string
  foodItem?: string
  supplements: {
    supplementId: string
    name: string
  }[]
  sources: string[]
  updatedAt: string | null
}

export type CategorizedInteractions = {
  supplementSupplementInteractions: Interaction[]
  supplementFoodInteractions: Interaction[]
}