"use client"

import { SearchBar } from "@/components/search-bar"
import { SupplementHero } from "@/components/supplement-hero"

export default function Home() {
  return (
    <main className="container mx-auto px-4 py-8">
      <SupplementHero />
      <div className="mt-8">
        <SearchBar />
      </div>
    </main>
  )
}