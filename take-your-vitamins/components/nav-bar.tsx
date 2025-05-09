"use client"

import { useState, useRef, useEffect } from "react"
import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { Pill, ChevronDown, Settings, LogOut, LogIn, UserPlus } from "lucide-react"
import { useAuth } from "@/contexts/auth-context"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

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

  // Define navigation items - different sets for authenticated and non-authenticated users
  const authNavItems = [
    { name: "Search", href: "/" },
    { name: "Tracker", href: "/dashboard" },
  ]

  const nonAuthNavItems = [
    { name: "Search", href: "/" },
  ]

  // Select the appropriate nav items based on authentication status
  const navItems = user ? authNavItems : nonAuthNavItems

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
        </div>

        {/* Center: App title */}
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
          <h1 className="text-xl font-bold">Take Your Vitamins</h1>
        </div>

        {/* Right section: Profile dropdown for logged in users, or login/signup buttons */}
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
                    <Settings className="mr-2 h-5 w-5" />
                    Settings
                  </Link>
                  <button onClick={handleSignOut} className="block flex w-full text-left py-1 text-black hover:text-primary">
                    <LogOut className="mr-2 h-5 w-5" />
                    Log out
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="flex items-center gap-3 mr-8">
            <Button variant="ghost" size="sm" asChild>
              <Link href="/login" className="flex items-center">
                <LogIn className="mr-1 h-4 w-4" />
                Log In
              </Link>
            </Button>
            <Button size="sm" asChild>
              <Link href="/signup" className="flex items-center">
                <UserPlus className="mr-1 h-4 w-4" />
                Sign Up
            </Link>
            </Button>
          </div>
        )}
      </div>
    </header>
  )
}

