"use client"

import { SearchBar } from "@/components/search-bar"
import { SupplementHero } from "@/components/supplement-hero"
import { FeatureSection } from "@/components/feature-section"

export default function Home() {
  return (
    <main className="w-full">
      <SupplementHero />
      <div className="container mx-auto px-4 py-8">
        <SearchBar />
      </div>
      <FeatureSection />
    </main>
  )
}