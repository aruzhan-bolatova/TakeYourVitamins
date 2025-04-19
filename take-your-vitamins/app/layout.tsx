import type React from "react"
import "@/app/globals.css"
import { Montserrat } from "next/font/google"
import { ThemeProvider } from "@/components/theme-provider"
import { AuthProvider } from "@/contexts/auth-context"
import { TrackerProvider } from "@/contexts/tracker-context"
import { AlertsProvider } from "@/contexts/alerts-context"
import { NotificationProvider } from "@/contexts/notification-context"
import { NavBar } from "@/components/nav-bar"
import { Toaster } from "@/components/ui/toaster"
import { ErrorBoundary, DefaultErrorFallback } from "@/components/error-boundary"

const montserrat = Montserrat({ subsets: ["latin"] })

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
      <body className={montserrat.className}>
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem disableTransitionOnChange>
          <ErrorBoundary fallback={DefaultErrorFallback}>
            <NotificationProvider>
              <AuthProvider>
                <AlertsProvider>
                  <TrackerProvider>
                    <div className="flex min-h-screen flex-col px-10">
                      <NavBar />
                      <main className="flex-1">{children}</main>
                    </div>
                    <Toaster />
                  </TrackerProvider>
                </AlertsProvider>
              </AuthProvider>
            </NotificationProvider>
          </ErrorBoundary>
        </ThemeProvider>
      </body>
    </html>
  )
}

