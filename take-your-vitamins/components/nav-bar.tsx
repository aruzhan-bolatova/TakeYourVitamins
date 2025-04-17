"use client"

import { useState, useRef, useEffect } from "react"
import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { Pill, ChevronDown, Settings, LogOut } from "lucide-react"
import { useAuth } from "@/contexts/auth-context"
import { cn } from "@/lib/utils"

export function NavBar() {
  const { user, signOut } = useAuth()
  const router = useRouter()
  const pathname = usePathname()
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false)
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  const handleSignOut = () => {
    signOut()
    router.push("/")
    setDropdownOpen(false)
  }

  const navItems = [
    { name: "Search", href: "/" },
    { name: "Tracker", href: "/dashboard" },
  ]

  return (
    <header className="top-0 z-50 w-full border-b relative">
      <div className="flex h-16 items-center justify-between ml-2">
        {/* Left section: Logo and nav links */}
        <div className="flex items-center gap-8">
          <Link href={user ? "/dashboard" : "/"} className="flex items-center gap-2 ">
            <div className="flex h-10 w-20 items-center justify-center rounded-full">
              <Pill className="h-5 w-5 text-white" />
              <span className="font-medium">T.Y.V</span>
            </div>
          </Link>

          {(
            <nav className="hidden md:flex items-center gap-6">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "text-base font-medium transition-colors hover:text-primary",
                    pathname === item.href || pathname.startsWith(`${item.href}/`) ? "text-primary" : "text-gray-700",
                  )}
                >
                  {item.name}
                </Link>
              ))}
            </nav>
          )}
        </div>

        {/* Center: App title */}
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
          <h1 className="text-xl font-bold">Take Your Vitamins</h1>
        </div>

        {/* Right section: Profile dropdown */}
        {user ? (
          <div className="relative mr-8" ref={dropdownRef}>
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="flex items-center gap-1 text-base font-medium text-gray-700 hover:text-primary"
            >
              Profile
              <ChevronDown className="h-4 w-4" />
            </button>

            {dropdownOpen && (
              <div className="absolute right-0 mt-2 w-64 rounded-md border bg-white p-4 shadow-lg">
                <div className="mb-4 border-b pb-2">
                  <p className="text-lg text-black font-medium">{user.name}</p>
                  <p className="text-sm text-gray-700">{user.email}</p>
                </div>
                <div className="space-y-2">
                  <Link
                    href="/settings"
                    className="block flex w-full text-left py-1 text-black hover:text-primary"
                    onClick={() => setDropdownOpen(false)}
                  >
                    <Settings />
                    Settings
                  </Link>
                  <button onClick={handleSignOut} className="block flex w-full text-left py-1 text-black hover:text-primary">
                    <LogOut />
                    Log out
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="flex items-center gap-4 mr-8">
            <Link href="/login" className="text-base font-medium text-black hover:text-primary">
              Login/Sign Up
            </Link>
          </div>
        )}
      </div>
    </header>
  )
}

