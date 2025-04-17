import { SearchResults } from "@/components/search-results"
import { SearchBar } from "@/components/search-bar"
import { Suspense } from "react"
import { SearchResultsSkeleton } from "@/components/search-results-skeleton"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { ChevronLeft } from "lucide-react"

export default function SearchResultsPage({
  searchParams,
}: {
  searchParams: { q: string }
}) {
  const query = searchParams.q || ""

  return (
    <main className="container mx-auto px-4 py-8">
      <div className="mb-4">
        <Button variant="ghost" size="sm" asChild className="mb-4">
          <Link href="/">
            <ChevronLeft className="mr-2 h-4 w-4" />
            Back to Home
          </Link>
        </Button>
      </div>
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

