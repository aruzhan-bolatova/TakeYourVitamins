"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { PageContainer } from "@/components/page-container"
import { PageHeader } from "@/components/page-header"
import { Bell, Moon, LifeBuoy, AlertOctagon, ChevronLeft, UserCog } from "lucide-react"
import Link from "next/link"
import { useAuth } from "@/contexts/auth-context"

export default function SettingsPage() {
  const { signOut, deleteAccount } = useAuth()

  const handleDeleteAccount = async () => {
    if (confirm("Are you sure you want to delete your account? This action cannot be undone.")) {
      
      await deleteAccount()
      signOut()
    }
  }

  return (
    <PageContainer withGradient>
      <PageHeader 
        title="Settings" 
        description="Configure your account preferences"
        actions={
          <Button variant="ghost" size="sm" asChild>
            <Link href="/profile">
              <ChevronLeft className="mr-2 h-4 w-4" />
              Back to Profile
            </Link>
          </Button>
        }
      />

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="border-primary/20 shadow-md">
          <CardHeader className="bg-primary/5 rounded-t-lg">
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5 text-primary" />
              Notifications
            </CardTitle>
            <CardDescription>Configure how you want to be notified</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6 pt-6">
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="daily-reminder" className="text-base font-medium">Daily reminder</Label>
                <p className="text-sm text-muted-foreground">Get reminded to take your supplements</p>
              </div>
              <Switch id="daily-reminder" defaultChecked className="data-[state=checked]:bg-primary" />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="interaction-alerts" className="text-base font-medium">Interaction alerts</Label>
                <p className="text-sm text-muted-foreground">Warn about supplement interactions</p>
              </div>
              <Switch id="interaction-alerts" defaultChecked className="data-[state=checked]:bg-primary" />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="weekly-report" className="text-base font-medium">Weekly report</Label>
                <p className="text-sm text-muted-foreground">Receive a weekly summary</p>
              </div>
              <Switch id="weekly-report" defaultChecked className="data-[state=checked]:bg-primary" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-primary/20 shadow-md">
          <CardHeader className="bg-primary/5 rounded-t-lg">
            <CardTitle className="flex items-center gap-2">
              <UserCog className="h-5 w-5 text-primary" />
              Account Preferences
            </CardTitle>
            <CardDescription>Manage your account settings</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6 pt-6">
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="dark-mode" className="text-base font-medium">Dark mode</Label>
                <p className="text-sm text-muted-foreground">Switch to dark theme</p>
              </div>
              <Switch id="dark-mode" className="data-[state=checked]:bg-primary" />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="data-sharing" className="text-base font-medium">Data sharing</Label>
                <p className="text-sm text-muted-foreground">Share anonymous usage data</p>
              </div>
              <Switch id="data-sharing" className="data-[state=checked]:bg-primary" />
            </div>
            
            <div className="pt-4">
              <Button variant="destructive" className="w-full flex items-center justify-center"
              onClick={handleDeleteAccount}>
                <AlertOctagon className="mr-2 h-4 w-4" />
              Delete Account
            </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </PageContainer>
  )
}

