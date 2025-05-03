import type { Metadata } from "next"
import { Montserrat } from "next/font/google"
import { cn } from "@/lib/utils"
import { AuthProvider } from "@/contexts/auth-context"
import { TrackerProvider } from "@/contexts/tracker-context"
import { RootLayoutClient } from "@/components/root-layout-client"
import { ThemeProvider } from "@/components/theme-provider"
import { Toaster } from "@/components/ui/toaster"
import "@/app/globals.css"
import { Inter } from "next/font/google"

const montserrat = Montserrat({ 
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
  variable: "--font-montserrat",
  display: "swap"
})

export const metadata = {
  title: "Take Your Vitamins",
  description: "Find information about supplements, their interactions, and best practices",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="h-full">
      <body
        className={cn(
          montserrat.variable,
          "relative h-full min-h-screen font-sans",
        )}
      >
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
          <AuthProvider>
            <TrackerProvider>
              <RootLayoutClient>{children}</RootLayoutClient>
            </TrackerProvider>
          </AuthProvider>
        </ThemeProvider>
        <Toaster />
      </body>
    </html>
  )
}

