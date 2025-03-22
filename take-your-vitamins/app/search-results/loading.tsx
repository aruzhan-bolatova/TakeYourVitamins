import { SearchResultsSkeleton } from "@/components/search-results-skeleton"

export default function Loading() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        {/* Placeholder for search bar */}
        <div className="w-full max-w-2xl mx-auto h-10 bg-muted/30 rounded-md animate-pulse" />
      </div>
      <div className="h-8 w-64 bg-muted/30 rounded-md animate-pulse mb-6" />
      <SearchResultsSkeleton />
    </div>
  )
}

