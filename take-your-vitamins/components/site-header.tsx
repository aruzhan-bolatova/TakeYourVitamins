import Link from "next/link"
import { useAuth } from "@/contexts/auth-context"
import { Button } from "@/components/ui/button"
import { Pill, Home, Settings, LogOut, Menu, X, User, Search } from "lucide-react"
import { useState } from "react"
import { cn } from "@/lib/utils"

export function SiteHeader() {
  const { user, signOut } = useAuth()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="flex flex-1 items-center justify-between">
          {/* Logo and main navigation */}
          <div className="flex items-center gap-2">
            <Link 
              href="/" 
              className="flex items-center font-bold text-gold-500"
              onClick={() => setMobileMenuOpen(false)}
            >
              <Pill className="h-5 w-5 text-primary mr-2" />
              <span className="text-primary font-bold">TYV</span>
            </Link>
            
            {/* Desktop navigation */}
            <nav className="hidden md:flex gap-6 ml-6">
              <Link 
                href="/" 
                className="text-sm font-medium transition-colors hover:text-primary"
              >
                Home
              </Link>
              <Link 
                href="/dashboard" 
                className="text-sm font-medium transition-colors hover:text-primary"
              >
                Dashboard
              </Link>
              <Link 
                href="/dashboard/tracker" 
                className="text-sm font-medium transition-colors hover:text-primary"
              >
                My Supplements
              </Link>
              <Link 
                href="/supplements/search" 
                className="text-sm font-medium transition-colors hover:text-primary"
              >
                Search
              </Link>
            </nav>
          </div>

          {/* Right menu items */}
          <div className="flex items-center gap-2">
            {user ? (
              <>
                <Button 
                  variant="ghost" 
                  size="icon"
                  className="hidden md:flex" 
                  asChild
                >
                  <Link href="/profile">
                    <User className="h-5 w-5" />
                    <span className="sr-only">Profile</span>
                  </Link>
                </Button>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="hidden md:flex"
                  asChild
                >
                  <Link href="/settings">
                    <Settings className="h-5 w-5" />
                    <span className="sr-only">Settings</span>
                  </Link>
                </Button>
                <Button 
                  variant="ghost" 
                  size="icon"
                  className="hidden md:flex"
                  onClick={signOut}
                >
                  <LogOut className="h-5 w-5" />
                  <span className="sr-only">Log out</span>
                </Button>
              </>
            ) : (
              <Button asChild className="hidden md:flex">
                <Link href="/login">Log in</Link>
              </Button>
            )}
            
            {/* Mobile menu button */}
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? (
                <X className="h-5 w-5" />
              ) : (
                <Menu className="h-5 w-5" />
              )}
              <span className="sr-only">Toggle menu</span>
            </Button>
          </div>
        </div>
      </div>
      
      {/* Mobile menu */}
      <div
        className={cn(
          "fixed inset-x-0 top-14 z-50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b",
          "transform transition-transform duration-200 ease-in-out md:hidden",
          mobileMenuOpen ? "translate-y-0" : "-translate-y-full"
        )}
      >
        <div className="container py-4">
          <nav className="flex flex-col space-y-4">
            <Link
              href="/"
              className="flex items-center py-2 text-sm font-medium"
              onClick={() => setMobileMenuOpen(false)}
            >
              <Home className="mr-2 h-4 w-4" />
              Home
            </Link>
            <Link
              href="/dashboard"
              className="flex items-center py-2 text-sm font-medium"
              onClick={() => setMobileMenuOpen(false)}
            >
              <Pill className="mr-2 h-4 w-4" />
              Dashboard
            </Link>
            <Link
              href="/dashboard/tracker"
              className="flex items-center py-2 text-sm font-medium"
              onClick={() => setMobileMenuOpen(false)}
            >
              <Pill className="mr-2 h-4 w-4" />
              My Supplements
            </Link>
            <Link
              href="/supplements/search"
              className="flex items-center py-2 text-sm font-medium"
              onClick={() => setMobileMenuOpen(false)}
            >
              <Search className="mr-2 h-4 w-4" />
              Search
            </Link>
            
            {user && (
              <>
                <Link
                  href="/profile"
                  className="flex items-center py-2 text-sm font-medium"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <User className="mr-2 h-4 w-4" />
                  Profile
                </Link>
                <Link
                  href="/settings"
                  className="flex items-center py-2 text-sm font-medium"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <Settings className="mr-2 h-4 w-4" />
                  Settings
                </Link>
                <Button
                  variant="ghost"
                  className="flex justify-start px-2"
                  onClick={() => {
                    signOut();
                    setMobileMenuOpen(false);
                  }}
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  Log out
                </Button>
              </>
            )}
            
            {!user && (
              <Button
                asChild
                className="mt-2"
                onClick={() => setMobileMenuOpen(false)}
              >
                <Link href="/login">Log in</Link>
              </Button>
            )}
          </nav>
        </div>
      </div>
    </header>
  )
} 