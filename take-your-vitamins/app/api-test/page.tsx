"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Loader2, CheckCircle, XCircle } from "lucide-react"
import { API_BASE_URL, checkApiConnection, getApiUrl } from "@/lib/api-config"

export default function ApiTestPage() {
  const [loading, setLoading] = useState(false)
  const [testResults, setTestResults] = useState<Record<string, boolean>>({})
  const [customUrl, setCustomUrl] = useState("")
  const [customUrlResult, setCustomUrlResult] = useState<boolean | null>(null)
  const [customUrlLoading, setCustomUrlLoading] = useState(false)

  // List of endpoints to test
  const endpointsToTest = [
    "/api/health",
    "/api/supplements",
    "/api/auth/me",
    "/api/alerts"
  ]

  // Run tests for all endpoints
  const runAllTests = async () => {
    setLoading(true)
    const results: Record<string, boolean> = {}

    // Test the base connection first
    const baseConnected = await testEndpoint("")
    results["Base URL"] = baseConnected

    // Test each endpoint
    for (const endpoint of endpointsToTest) {
      const success = await testEndpoint(endpoint)
      results[endpoint] = success
    }

    setTestResults(results)
    setLoading(false)
  }

  // Test a specific endpoint
  const testEndpoint = async (endpoint: string): Promise<boolean> => {
    try {
      const url = endpoint ? getApiUrl(endpoint) : API_BASE_URL
      console.log(`Testing endpoint: ${url}`)
      
      const response = await fetch(url, {
        method: "GET",
        headers: {
          "Accept": "application/json"
        },
        // Add a timeout to avoid hanging
        signal: AbortSignal.timeout(5000)
      })
      
      console.log(`Response for ${url}:`, response.status)
      return response.status < 500 // Consider non-server errors as "reachable"
    } catch (error) {
      console.error(`Error testing ${endpoint}:`, error)
      return false
    }
  }

  // Test a custom URL
  const testCustomUrl = async () => {
    if (!customUrl) return
    
    setCustomUrlLoading(true)
    setCustomUrlResult(null)
    
    try {
      const response = await fetch(customUrl, {
        method: "GET",
        headers: {
          "Accept": "application/json"
        },
        signal: AbortSignal.timeout(5000)
      })
      
      setCustomUrlResult(response.status < 500)
    } catch (error) {
      console.error("Error testing custom URL:", error)
      setCustomUrlResult(false)
    } finally {
      setCustomUrlLoading(false)
    }
  }

  // Auto-run tests on first load
  useEffect(() => {
    runAllTests()
  }, [])

  return (
    <div className="container py-6">
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>API Connection Tester</CardTitle>
          <CardDescription>
            Check connectivity to the backend API endpoints
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="mb-6">
            <p className="text-sm text-muted-foreground mb-2">
              Current API Base URL: <code className="bg-muted px-1 py-0.5 rounded">{API_BASE_URL}</code>
            </p>
            <p className="text-sm text-muted-foreground">
              To change the API URL, update the <code className="bg-muted px-1 py-0.5 rounded">API_BASE_URL</code> in <code className="bg-muted px-1 py-0.5 rounded">lib/api-config.ts</code>
            </p>
          </div>

          <h3 className="text-lg font-medium mb-2">Test Results</h3>
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : (
            <div className="space-y-2">
              {Object.entries(testResults).map(([endpoint, success]) => (
                <div 
                  key={endpoint} 
                  className="flex items-center justify-between border p-3 rounded"
                >
                  <div>
                    <span className="font-medium">{endpoint}</span>
                  </div>
                  <div>
                    {success ? (
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-500" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="mt-6">
            <h3 className="text-lg font-medium mb-3">Test Custom URL</h3>
            <div className="flex gap-2">
              <Input 
                placeholder="Enter a URL to test" 
                value={customUrl}
                onChange={(e) => setCustomUrl(e.target.value)}
              />
              <Button 
                onClick={testCustomUrl}
                disabled={!customUrl || customUrlLoading}
              >
                {customUrlLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Test"}
              </Button>
            </div>
            {customUrlResult !== null && (
              <div className="mt-2 flex items-center">
                {customUrlResult ? (
                  <>
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    <span className="text-sm text-green-600">Connection successful</span>
                  </>
                ) : (
                  <>
                    <XCircle className="h-4 w-4 text-red-500 mr-2" />
                    <span className="text-sm text-red-600">Connection failed</span>
                  </>
                )}
              </div>
            )}
          </div>
        </CardContent>
        <CardFooter>
          <Button onClick={runAllTests} disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Testing...
              </>
            ) : "Run Tests Again"}
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
} 