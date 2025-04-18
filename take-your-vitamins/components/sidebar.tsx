"use client"

import type React from "react"

import { useState, useEffect } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Home, Search, BarChart2, Settings, User, ChevronLeft, ChevronRight, Pill } from "lucide-react"

type SidebarItem = {
  title: string
  icon: React.ReactNode
  href: string
  badge?: number
}

export function Sidebar() {
  const [expanded, setExpanded] = useState(true)
  const pathname = usePathname()

  // Check if we're on mobile and collapse sidebar by default
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 1024) {
        setExpanded(false)
      }
    }

    // Set initial state
    handleResize()

    window.addEventListener("resize", handleResize)
    return () => window.removeEventListener("resize", handleResize)
  }, [])

  // Save sidebar state in localStorage
  useEffect(() => {
    if (typeof window !== "undefined") {
      localStorage.setItem("sidebarExpanded", expanded.toString())
    }
  }, [expanded])

  // Load sidebar state from localStorage
  useEffect(() => {
    if (typeof window !== "undefined") {
      const savedState = localStorage.getItem("sidebarExpanded")
      if (savedState) {
        setExpanded(savedState === "true")
      }
    }
  }, [])

  const sidebarItems: SidebarItem[] = [
    {
      title: "Dashboard",
      icon: <Home size={20} />,
      href: "/dashboard",
    },
    {
      title: "Search",
      icon: <Search size={20} />,
      href: "/search",
    },
    {
      title: "Insights",
      icon: <BarChart2 size={20} />,
      href: "/insights",
    },
    // {
    //   title: "Supplements",
    //   icon: <Pill size={20} />,
    //   href: "/dashboard/tracker",
    // },
    {
      title: "Settings",
      icon: <Settings size={20} />,
      href: "/settings",
    },
    {
      title: "Profile",
      icon: <User size={20} />,
      href: "/profile",
    },
  ]

  return (
    <div className="relative">
      {/* Sidebar */}
      <aside
        className={cn(
          "fixed left-0 top-0 z-40 h-screen text-white transition-all duration-300",
          expanded ? "w-64" : "w-16",
        )}
      >
        {/* App Logo */}
        <div
          className={cn(
            "flex h-16 items-center border-b border-slate-800 px-4",
            expanded ? "justify-start" : "justify-center",
          )}
        >
          <div className="flex items-center gap-3">
            <Pill className="h-6 w-6 text-primary" />
            {expanded && <span className="text-lg font-semibold">Take Your Vitamins</span>}
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="flex flex-col gap-1 p-2">
          {sidebarItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`)

            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 transition-colors",
                  isActive ? "bg-slate-800 text-white" : "text-slate-300 hover:bg-slate-800 hover:text-white",
                )}
              >
                <div className="flex h-6 w-6 items-center justify-center">{item.icon}</div>

                {expanded && <span className="text-sm font-medium">{item.title}</span>}

                {expanded && item.badge && (
                  <span className="ml-auto flex h-5 w-5 items-center justify-center rounded-full bg-primary text-xs font-medium">
                    {item.badge}
                  </span>
                )}
              </Link>
            )
          })}
        </nav>

        {/* Toggle Button */}
        <Button
          variant="ghost"
          size="icon"
          className="absolute -right-3 top-20 h-6 w-6 rounded-full border border-slate-800 bg-slate-900 text-white hover:bg-slate-800"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? <ChevronLeft size={12} /> : <ChevronRight size={12} />}
        </Button>
      </aside>

      {/* Content Margin */}
      <div className={cn("transition-all duration-300", expanded ? "ml-64" : "ml-16")} />
    </div>
  )
}

