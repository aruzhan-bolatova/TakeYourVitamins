import { SearchResults } from "@/components/search-results"
import { SearchBar } from "@/components/search-bar"
import { Suspense } from "react"
import { SearchResultsSkeleton } from "@/components/search-results-skeleton"

export default function SearchPage({
  searchParams,
}: {
  searchParams: { q: string }
}) {
  const query = searchParams.q || ""

  return (
    <main className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <SearchBar />
      </div>
      <h1 className="text-2xl font-bold mb-6">
        Search results for: <span className="text-primary">{query}</span>
      </h1>
      <Suspense fallback={<SearchResultsSkeleton />}>
        <SearchResults query={query} />
      </Suspense>
    </main>
  )
}

