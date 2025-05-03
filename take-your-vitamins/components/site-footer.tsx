import Link from "next/link"
import Image from "next/image"

export function SiteFooter() {
  return (
    <footer className="w-full border-t bg-background">
      <div className="container flex flex-col sm:flex-row items-center justify-between py-4 md:py-6">
        <div className="flex items-center gap-2">
          <div className="relative w-5 h-5">
            <Image
              src="/images/logo-32.png"
              alt="Take Your Vitamins"
              fill
              className="object-contain"
            />
          </div>
          <span className="text-primary font-bold text-sm">Take Your Vitamins</span>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4 sm:gap-8 mt-4 sm:mt-0 items-center text-xs text-muted-foreground">
          <Link href="/terms" className="hover:underline">
            Terms of Service
          </Link>
          <Link href="/privacy" className="hover:underline">
            Privacy Policy
          </Link>
          <div className="flex items-center">
            <span className="text-amber-600 mr-2">⚕️</span>
            <span className="text-xs italic">Consult your doctor</span>
          </div>
          <span>© {new Date().getFullYear()} TYV Inc.</span>
        </div>
      </div>
    </footer>
  )
} 