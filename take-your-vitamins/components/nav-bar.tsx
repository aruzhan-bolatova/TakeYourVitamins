"use client"

import { useState, useRef, useEffect } from "react"
import Link from "next/link"
import Image from "next/image"
import { usePathname, useRouter } from "next/navigation"
import { 
  ChevronDown, 
  Settings, 
  LogOut, 
  LogIn, 
  UserPlus, 
  Home, 
  Pill, 
  Bell,
  Search,
  FileText,
  Award,
  BarChart2
} from "lucide-react"
import { useAuth } from "@/contexts/auth-context"
import { cn } from "@/lib/utils"
import { AlertsDropdown } from "@/components/alerts/alerts-dropdown"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

export function NavBar() {
  const { user, signOut } = useAuth()
  const router = useRouter()
  const pathname = usePathname()

  const handleSignOut = () => {
    signOut()
    router.push("/")
  }

  // Function to check if a link is active
  const isActiveLink = (href: string): boolean => {
    // For dashboard, only highlight if exactly at /dashboard
    if (href === "/dashboard") {
      return pathname === "/dashboard";
    }
    
    // For other links, use the startsWith approach to highlight sections
    return pathname === href || pathname.startsWith(`${href}/`);
  };

  // Navigation items for main nav
  const mainNavItems = [
    { name: "Search", href: "/", icon: <Search className="h-4 w-4 mr-1.5" /> },
    ...(user ? [
      { name: "Dashboard", href: "/dashboard", icon: <Home className="h-4 w-4 mr-1.5" /> },
      { name: "Tracker", href: "/dashboard/tracker", icon: <Pill className="h-4 w-4 mr-1.5" /> },
      { name: "Alerts", href: "/alerts", icon: <Bell className="h-4 w-4 mr-1.5" /> }
    ] : [])
  ]

  // Dashboard-specific nav items
  const dashboardNavItems = [
    { name: "Tracker", href: "/dashboard/tracker", icon: <Pill className="mr-2 h-4 w-4" /> },
    { name: "Daily Log", href: "/dashboard/tracker/log", icon: <FileText className="mr-2 h-4 w-4" /> },
    { name: "Reports", href: "/dashboard/reports", icon: <BarChart2 className="mr-2 h-4 w-4" /> },
    { name: "Streaks", href: "/dashboard/streaks", icon: <Award className="mr-2 h-4 w-4" /> }
  ];

  // Get user initials for avatar fallback
  const getUserInitials = () => {
    if (!user?.name) return "U";
    return user.name
      .split(" ")
      .map(part => part[0])
      .join("")
      .toUpperCase();
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-black text-white">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Left section: Logo and site name */}
          <div className="flex items-center">
            <Link href={user ? "/dashboard" : "/"} className="flex items-center gap-2">
              <div className="relative h-10 w-10">
                <Image 
                  src="/images/logo.png" 
                  alt="Take Your Vitamins Logo" 
                  width={40}
                  height={40}
                  priority
                  className="object-contain"
                />
              </div>
              <span className="font-medium text-lg hidden sm:inline-block">Take Your Vitamins</span>
            </Link>
          </div>

          {/* Center section: Main navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            {mainNavItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center text-sm font-medium transition-colors hover:text-primary",
                  isActiveLink(item.href) 
                    ? "text-primary" 
                    : "text-zinc-400 hover:text-white"
                )}
              >
                {item.icon}
                {item.name}
              </Link>
            ))}
          </nav>

          {/* Right section: Notifications and Profile */}
          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <AlertsDropdown />
                
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                      <Avatar className="h-8 w-8">
                        <AvatarFallback className="bg-primary/20 text-primary">
                          {getUserInitials()}
                        </AvatarFallback>
                      </Avatar>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-56">
                    <div className="flex items-center p-2">
                      <div className="ml-2 flex flex-col space-y-0.5">
                        {user.name && <p className="text-sm font-medium">{user.name}</p>}
                        {user.email && (
                          <p className="text-xs text-muted-foreground truncate">
                            {user.email}
                          </p>
                        )}
                      </div>
                    </div>
                    <DropdownMenuSeparator />
                    <DropdownMenuLabel>Navigation</DropdownMenuLabel>
                    {dashboardNavItems.map((item) => (
                      <DropdownMenuItem key={item.href} asChild>
                        <Link href={item.href} className="cursor-pointer">
                          {item.icon}
                          {item.name}
                        </Link>
                      </DropdownMenuItem>
                    ))}
                    <DropdownMenuSeparator />
                    <DropdownMenuItem asChild>
                      <Link href="/settings" className="cursor-pointer">
                        <Settings className="mr-2 h-4 w-4" />
                        Settings
                      </Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={handleSignOut} className="cursor-pointer text-red-600">
                      <LogOut className="mr-2 h-4 w-4" />
                      Log out
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </>
            ) : (
              <div className="flex items-center gap-3">
                <Link href="/login">
                  <Button variant="outline" size="sm" className="flex items-center gap-1 bg-transparent text-white border-white/20 hover:bg-white/10">
                    <LogIn className="h-4 w-4" />
                    <span>Log In</span>
                  </Button>
                </Link>
                <Link href="/signup">
                  <Button size="sm" className="flex items-center gap-1">
                    <UserPlus className="h-4 w-4" />
                    <span>Sign Up</span>
                  </Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}

