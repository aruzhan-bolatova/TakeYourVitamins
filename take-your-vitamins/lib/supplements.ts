// supplements.ts : Contains the mock data and search functions
import type { Supplement, CategorizedInteractions } from "@/lib/types"
// Function to search supplements by name or aliases
export async function searchSupplements(query: string): Promise<Supplement[]> {
  if (!query.trim()) return []

  try {
    // Fetch supplements from the backend API using the search query
    const response = await fetch(`http://10.228.244.25:5001/api/supplements/?search=${encodeURIComponent(query)}`)
    if (!response.ok) {
      console.error("Failed to fetch search results")
      return []
    }

    // Parse and return the JSON response
    return await response.json()
  } catch (error) {
    console.error("Error while fetching search results:", error)
    return []
  }
}

// Function to fetch a specific supplement by its ID
export async function getSupplementById(supplementId: string): Promise<Supplement | null> {
  if (!supplementId.trim()) return null

  try {
    const response = await fetch(`http://10.228.244.25:5001/api/supplements/${encodeURIComponent(supplementId)}`)

    if (!response.ok) {
      console.error("Failed to fetch supplement by ID")
      return null
    }

    const data = await response.json()
    return data as Supplement
  } catch (error) {
    console.error("Error while fetching supplement by ID:", error)
    return null
  }
}

export async function getSupplementInteractions(supplementId: string): Promise<CategorizedInteractions | null> { 
  if (!supplementId.trim()) return null
  try
  {
    const response = await fetch(`http://10.228.244.25:5001/api/supplements/by-supplement/${supplementId}`)
    if (!response.ok) {
      console.error("Failed to fetch interactions by supplement ID")
      return null
    }

    const data = await response.json()
    console.log("Fetched interactions:", data)
    return data as CategorizedInteractions
  } catch (error) {
    console.error("Error while fetching interactions for supplement ID:", error)
    return null
  }
  }

// Check interactions for a given supplement
export async function checkInteractions(supplementId: string): Promise<string[]> {
  if (!supplementId.trim()) return []

  try {
    // Fetch interactions for the supplement from the backend
    const response = await fetch(
      `http://10.228.244.25:5001/api/supplements/by-supplement/${supplementId}`
    )

    if (!response.ok) {
      console.error("Failed to fetch interactions by supplement ID")
      return []
    }

    const data = await response.json()

    // Extract and format interaction warnings
    const warnings: string[] = []

    // Process supplement-supplement interactions
    if (data.supplementSupplementInteractions) {
      data.supplementSupplementInteractions.forEach((interaction: any) => {
        const description = interaction.description || "No description provided."
        const recommendation = interaction.recommendation || "No recommendation provided."
        warnings.push(
          `Interaction: ${description} Recommendation: ${recommendation}`
        )
      })
    }

    // Process supplement-food interactions (if applicable)
    if (data.supplementFoodInteractions) {
      data.supplementFoodInteractions.forEach((interaction: any) => {
        const description = interaction.description || "No description provided."
        const recommendation = interaction.recommendation || "No recommendation provided."
        warnings.push(
          `Food Interaction: ${description} Recommendation: ${recommendation}`
        )
      })
    }

    return warnings
  } catch (error) {
    console.error("Error while fetching interactions for supplement ID:", error)
    return []
  }
}

// Function to fetch autocomplete suggestions for supplements
export type AutocompleteSuggestion = {
  id: string
  name: string
}

export async function getAutocompleteSuggestions(query: string): Promise<AutocompleteSuggestion[]> {
  if (!query.trim()) return []

  try {
    const response = await fetch(`http://10.228.244.25:5001/api/supplements/autocomplete?search=${encodeURIComponent(query)}`)
    if (!response.ok) {
      console.error("Failed to fetch autocomplete suggestions")
      return []
    }

    const data = await response.json()
    console.log("Autocomplete suggestions:", data)
    return data as AutocompleteSuggestion[]
  } catch (error) {
    console.error("Error while fetching autocomplete suggestions:", error)
    return []
  }
}

// Function to fetch all supplements (without any search query)
export async function getAllSupplements(): Promise<Supplement[]> {
  try {
    // Fetch all supplements from the backend API
    const response = await fetch(`http://10.228.244.25:5001/api/supplements/`)
    console.log("Fetched all supplements:", response)
    if (!response.ok) {
      console.error("Failed to fetch all supplements")
      return []
    }

    // Parse and return the JSON response
    return await response.json()
  } catch (error) {
    console.error("Error while fetching all supplements:", error)
    return []
  }
}