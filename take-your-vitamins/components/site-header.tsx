import Link from "next/link"
import Image from "next/image"
import { useAuth } from "@/contexts/auth-context"
import { Button } from "@/components/ui/button"
import { Home, Settings, LogOut, Menu, X, User, Search } from "lucide-react"
import { useState, useEffect } from "react"
import { cn } from "@/lib/utils"

export function SiteHeader() {
  const { user, signOut } = useAuth()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  
  // Close mobile menu when screen size changes to medium or larger
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 768) {
        setMobileMenuOpen(false)
      }
    }
    
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return (
    <header className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="px-10 flex h-14 items-center">
        <div className="flex flex-1 items-center justify-between">
          {/* Logo and main navigation */}
          <div className="flex items-center gap-2">
            <Link 
              href="/" 
              className="flex items-center font-bold"
              onClick={() => setMobileMenuOpen(false)}
            >
              <div className="relative w-8 h-8 md:w-10 md:h-10">
                <Image
                  src="/images/logo-64.png"
                  alt="Take Your Vitamins"
                  className="object-contain"
                  fill
                  sizes="(max-width: 768px) 32px, 40px"
                  priority
                />
              </div>
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
              onClick={() => {
                setMobileMenuOpen(!mobileMenuOpen)
              }}
              aria-expanded={mobileMenuOpen}
              aria-controls="mobile-menu"
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
        id="mobile-menu"
        className={cn(
          "fixed inset-x-0 top-14 z-50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b md:hidden",
          mobileMenuOpen ? "block" : "hidden"
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
              <div className="relative w-4 h-4 mr-2">
                <Image
                  src="/images/logo-32.png"
                  alt="Dashboard"
                  fill
                  className="object-contain"
                />
              </div>
              Dashboard
            </Link>
            <Link
              href="/dashboard/tracker"
              className="flex items-center py-2 text-sm font-medium"
              onClick={() => setMobileMenuOpen(false)}
            >
              <div className="relative w-4 h-4 mr-2">
                <Image
                  src="/images/logo-32.png"
                  alt="My Supplements"
                  fill
                  className="object-contain"
                />
              </div>
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
                  className="flex items-center justify-start px-2 text-sm font-medium w-full"
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