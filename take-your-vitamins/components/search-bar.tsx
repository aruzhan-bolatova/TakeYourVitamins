"use client"

import type React from "react"
import { useState, useEffect, useRef } from "react"
import { Search } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"
import { getAutocompleteSuggestions, AutocompleteSuggestion } from "@/lib/supplements"

export function SearchBar() {
  const [query, setQuery] = useState("")
  const [suggestions, setSuggestions] = useState<AutocompleteSuggestion[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [activeSuggestion, setActiveSuggestion] = useState(-1)
  const router = useRouter()
  const suggestionRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const fetchSuggestions = async () => {
      if (query.trim().length > 0) {
        const results = await getAutocompleteSuggestions(query)
        setSuggestions(results)
        setShowSuggestions(results.length > 0)
      } else {
        setSuggestions([])
        setShowSuggestions(false)
      }
    }

    fetchSuggestions()
  }, [query])

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (suggestionRef.current && !suggestionRef.current.contains(event.target as Node)) {
        setShowSuggestions(false)
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    return () => {
      document.removeEventListener("mousedown", handleClickOutside)
    }
  }, [])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      window.location.href = `/search-results?q=${encodeURIComponent(query.trim())}`
    }
  }

  const handleSuggestionClick = (suggestion: AutocompleteSuggestion) => {
    setQuery(suggestion.name)
    router.push(`/supplements/${suggestion.id}`)
    setShowSuggestions(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      e.preventDefault()
      setActiveSuggestion((prev) => (prev < suggestions.length - 1 ? prev + 1 : prev))
    } else if (e.key === "ArrowUp") {
      e.preventDefault()
      setActiveSuggestion((prev) => (prev > 0 ? prev - 1 : 0))
    } else if (e.key === "Enter" && activeSuggestion >= 0) {
      e.preventDefault()
      handleSuggestionClick(suggestions[activeSuggestion])
    } else if (e.key === "Escape") {
      setShowSuggestions(false)
    }
  }

  return (
    <div className="w-full max-w-3xl mx-auto relative z-10">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold mb-2">Search Our Database</h2>
        <p className="text-muted-foreground">Try searching for: Vitamin D, Omega-3, Zinc, Magnesium...</p>
      </div>
      
      <form onSubmit={handleSearch} className="w-full">
      <div className="flex w-full items-center space-x-2 relative">
        <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-primary" />
          <Input
            type="text"
            placeholder="Search for a supplement (e.g., Vitamin D, Magnesium, Omega-3)"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => {
              if (query.trim() && suggestions.length > 0) {
                setShowSuggestions(true)
              }
            }}
              className="pl-10 py-6 text-base border-primary/20 focus:border-primary"
          />

          {showSuggestions && (
            <div
              ref={suggestionRef}
              className="absolute z-10 w-full mt-1 bg-background border rounded-md shadow-lg max-h-60 overflow-auto"
            >
              <ul className="py-1">
                {suggestions.map((suggestion, index) => (
                  <li
                    key={suggestion.id}
                      className={`px-4 py-3 cursor-pointer hover:bg-primary/5 font-medium ${
                        index === activeSuggestion ? "bg-primary/5 text-primary" : ""
                    }`}
                    onClick={() => handleSuggestionClick(suggestion)}
                    onMouseEnter={() => setActiveSuggestion(index)}
                  >
                    {suggestion.name}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
          <Button type="submit" size="lg" className="py-6 px-8">
            <Search className="h-5 w-5 mr-2" />
            Search
          </Button>
      </div>
    </form>
    </div>
  )
}