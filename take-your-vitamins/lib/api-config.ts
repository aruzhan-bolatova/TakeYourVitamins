// Central place to manage API endpoint configuration

// API base URL
// This can be changed to match the current backend server address
export const API_BASE_URL = "http://localhost:5001" // Default to localhost for development

// Alternative options:
// export const API_BASE_URL = "http://10.228.244.25:5001" // Fixed IP from previous code
// export const API_BASE_URL = "https://api.takeyourvitamins.com" // For production

// Helper function to get an API endpoint URL
export function getApiUrl(path: string): string {
  // Ensure path starts with a slash
  const formattedPath = path.startsWith('/') ? path : `/${path}`
  return `${API_BASE_URL}${formattedPath}`
}

// Helper to check if the API is accessible (for troubleshooting)
export async function checkApiConnection(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`, { 
      method: 'GET',
      // Set a short timeout to avoid long waits
      signal: AbortSignal.timeout(5000) 
    })
    return response.ok
  } catch (error) {
    console.error('API connection check failed:', error)
    return false
  }
} 