"use client"

import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { 
  Home, Pill, Calendar, LogOut, BarChart3, 
  Award, TrendingUp, LineChart, FileText 
} from "lucide-react"
import { useAuth } from "@/contexts/auth-context"
import { ClassNames } from "react-day-picker"

interface User {
  id: string
  name: string
  email: string
  image?: string
}

interface DashboardNavProps {
  user: User
  className?: string; // Allow className to be passed as a prop
}

export function DashboardNav({ user }: DashboardNavProps) {
  const pathname = usePathname()
  const router = useRouter()
  const { signOut } = useAuth()

  // Update the navItems array to include the new reports pages
  const navItems = [
    {
      title: "Dashboard",
      href: "/dashboard",
      icon: <Home className="mr-2 h-4 w-4" />,
    },
    {
      title: "Supplement Tracker",
      href: "/dashboard/tracker",
      icon: <Pill className="mr-2 h-4 w-4" />,
    },
    {
      title: "Daily Log",
      href: "/dashboard/tracker/log",
      icon: <Calendar className="mr-2 h-4 w-4" />,
    },
    {
      title: "Reports",
      href: "/dashboard/reports",
      icon: <FileText className="mr-2 h-4 w-4" />,
    },
    {
      title: "Streaks",
      href: "/dashboard/streaks",
      icon: <Award className="mr-2 h-4 w-4" />,
    },
    {
      title: "Progress",
      href: "/dashboard/progress",
      icon: <TrendingUp className="mr-2 h-4 w-4" />,
    },
  ]

  const handleSignOut = () => {
    signOut()
    router.push("/")
  }

  return (
    <div className="flex items-center gap-4">
      <nav className="hidden md:flex items-center space-x-4">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`flex items-center text-sm font-medium transition-colors hover:text-primary ${
              pathname === item.href ? "text-primary" : "text-muted-foreground"
            }`}
          >
            {item.icon}
            {item.title}
          </Link>
        ))}
      </nav>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" className="relative h-8 w-8 rounded-full">
            <Avatar className="h-8 w-8">
              <AvatarImage src={user.image || ""} alt={user.name || ""} />
              <AvatarFallback>
                {user.name
                  ? user.name
                      .split(" ")
                      .map((n) => n[0])
                      .join("")
                  : "U"}
              </AvatarFallback>
            </Avatar>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <div className="flex items-center justify-start gap-2 p-2">
            <div className="flex flex-col space-y-1 leading-none">
              {user.name && <p className="font-medium">{user.name}</p>}
              {user.email && <p className="w-[200px] truncate text-sm text-muted-foreground">{user.email}</p>}
            </div>
          </div>
          <DropdownMenuSeparator />
          <DropdownMenuItem asChild>
            <Link href="/dashboard/reports">
              <FileText className="mr-2 h-4 w-4" />
              Reports
            </Link>
          </DropdownMenuItem>
          <DropdownMenuItem asChild>
            <Link href="/dashboard/streaks">
              <Award className="mr-2 h-4 w-4" />
              Streaks
            </Link>
          </DropdownMenuItem>
          <DropdownMenuItem asChild>
            <Link href="/dashboard/progress">
              <TrendingUp className="mr-2 h-4 w-4" />
              Progress
            </Link>
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem className="cursor-pointer" onClick={handleSignOut}>
            <LogOut className="mr-2 h-4 w-4" />
            Log out
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  )
}

