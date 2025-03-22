import { searchSupplements } from "@/lib/supplements"
import { SupplementCard } from "@/components/supplement-card"

export async function SearchResults({ query }: { query: string }) {
  // Add a check for empty query
  if (!query.trim()) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-medium mb-2">Please enter a search term</h2>
        <p className="text-muted-foreground">Try searching for a supplement like "Vitamin D" or "Magnesium"</p>
      </div>
    )
  }

  const results = await searchSupplements(query)

  if (results.length === 0) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-medium mb-2">No supplements found</h2>
        <p className="text-muted-foreground">Try searching for a different supplement or check your spelling.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {results.map((supplement) => (
        <SupplementCard key={supplement.id} supplement={supplement} />
      ))}
    </div>
  )
}

