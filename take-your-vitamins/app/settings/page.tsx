import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"

export default function SettingsPage() {
  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-6">Settings</h1>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Notifications</CardTitle>
            <CardDescription>Configure how you want to be notified</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <Label htmlFor="daily-reminder">Daily reminder to take supplements</Label>
              <Switch id="daily-reminder" defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="interaction-alerts">Supplement interaction alerts</Label>
              <Switch id="interaction-alerts" defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="weekly-report">Weekly progress report</Label>
              <Switch id="weekly-report" defaultChecked />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Account Preferences</CardTitle>
            <CardDescription>Manage your account settings</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <Label htmlFor="dark-mode">Dark mode</Label>
              <Switch id="dark-mode" />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="data-sharing">Share anonymous data for research</Label>
              <Switch id="data-sharing" />
            </div>
            <Button variant="destructive" className="w-full mt-4">
              Delete Account
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

