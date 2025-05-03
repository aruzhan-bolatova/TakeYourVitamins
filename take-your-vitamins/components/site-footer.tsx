import Link from "next/link"
import { Pill } from "lucide-react"

export function SiteFooter() {
  return (
    <footer className="w-full border-t bg-background">
      <div className="container flex flex-col sm:flex-row items-center justify-between py-4 md:py-6">
        <div className="flex items-center gap-2">
          <Pill className="h-4 w-4 text-primary" />
          <span className="text-primary font-bold text-sm">Take Your Vitamins</span>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4 sm:gap-8 mt-4 sm:mt-0 items-center text-xs text-muted-foreground">
          <Link href="/terms" className="hover:underline">
            Terms of Service
          </Link>
          <Link href="/privacy" className="hover:underline">
            Privacy Policy
          </Link>
          <span>© {new Date().getFullYear()} TYV Inc.</span>
        </div>
      </div>
    </footer>
  )
} 