"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"
import { Search } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"
import { getSuggestions } from "@/lib/supplements"

export function SearchBar() {
  const [query, setQuery] = useState("")
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [activeSuggestion, setActiveSuggestion] = useState(-1)
  const router = useRouter()
  const suggestionRef = useRef<HTMLDivElement>(null)    //Creates a reference to an HTML <div> element
                        // useRef is a React Hook that returns a mutable reference (ref) to a DOM element or a value that persists across renders without causing re-renders.
                        // Unlike useState, updating ref.current does not trigger a re-render
                        // Can be used for dropdowns, modals, or suggestion lists (e.g., auto-suggest inputs).
  useEffect(() => {
    const fetchSuggestions = async () => {
      if (query.trim().length > 0) {
        const results = await getSuggestions(query)
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
      // Use the new simplified route
      window.location.href = `/search-results?q=${encodeURIComponent(query.trim())}`
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion)
    // Use the new simplified route
    window.location.href = `/search-results?q=${encodeURIComponent(suggestion)}`
    setShowSuggestions(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Arrow down
    if (e.key === "ArrowDown") {
      e.preventDefault()
      setActiveSuggestion((prev) => (prev < suggestions.length - 1 ? prev + 1 : prev))
    }
    // Arrow up
    else if (e.key === "ArrowUp") {
      e.preventDefault()
      setActiveSuggestion((prev) => (prev > 0 ? prev - 1 : 0))
    }
    // Enter
    else if (e.key === "Enter" && activeSuggestion >= 0) {
      e.preventDefault()
      handleSuggestionClick(suggestions[activeSuggestion])
    }
    // Escape
    else if (e.key === "Escape") {
      setShowSuggestions(false)
    }
  }

  return (
    <form onSubmit={handleSearch} className="w-full max-w-2xl mx-auto">
      <div className="flex w-full items-center space-x-2 relative">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
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
            className="pl-10"
          />

          {showSuggestions && (
            <div
              ref={suggestionRef}
              className="absolute z-10 w-full mt-1 bg-background border rounded-md shadow-lg max-h-60 overflow-auto"
            >
              <ul className="py-1">
                {suggestions.map((suggestion, index) => (
                  <li
                    key={index}
                    className={`px-4 py-2 cursor-pointer hover:bg-muted ${
                      index === activeSuggestion ? "bg-muted" : ""
                    }`}
                    onClick={() => handleSuggestionClick(suggestion)}
                    onMouseEnter={() => setActiveSuggestion(index)}
                  >
                    {suggestion}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
        <Button type="submit">Search</Button>
      </div>
    </form>
  )
}

