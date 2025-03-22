import type React from "react"
import "@/app/globals.css"
import { Inter } from "next/font/google"
import { ThemeProvider } from "@/components/theme-provider"
import { AuthProvider } from "@/contexts/auth-context"
import { TrackerProvider } from "@/contexts/tracker-context"
import { NavBar } from "@/components/nav-bar"

const inter = Inter({ subsets: ["latin"] })

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
    <html lang="en">
      <body className={inter.className}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
          <AuthProvider>
            <TrackerProvider>
              <div className="flex min-h-screen flex-col">
                <NavBar />
                <main className="flex-1">{children} </main>
              </div>
            </TrackerProvider>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}

