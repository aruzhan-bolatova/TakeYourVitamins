"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import { useRouter } from "next/navigation"
import { getApiUrl } from "@/lib/api-config"
import { handleError } from "@/lib/error-handler"
import { fetchWithErrorHandling } from "@/lib/error-handler"
import { useNotification } from "@/contexts/notification-context"
import { tryCatch } from "@/lib/error-handling"

type User = {
  id: string
  name: string
  email: string
  gender: string
  age: string
}

type AuthContextType = {
  user: User | null
  isLoading: boolean
  signIn: (email: string, password: string) => Promise<boolean>
  signUp: (name: string, email: string, password: string, age: string, gender: string) => Promise<boolean>
  signOut: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()
  const notification = useNotification()

  // Load user and token from localStorage on initial render
  useEffect(() => {
    const storedUser = localStorage.getItem("user")
    const storedToken = localStorage.getItem("token")
    if (storedUser && storedToken) {
      setUser(JSON.parse(storedUser))
    }
    setIsLoading(false)
  }, [])

  // Sign in function using the backend auth/login endpoint
  const signIn = async (email: string, password: string) => {
    setIsLoading(true)

    try {
      // Make a POST request to the auth/login endpoint
      const [response, loginError] = await tryCatch(async () => {
        const resp = await fetch(getApiUrl("/api/auth/login"), {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ email, password }),
        });
        
        if (!resp.ok) {
          const errorData = await resp.json().catch(() => ({}));
          throw { 
            ...errorData,
            error: errorData.message || "Invalid email or password",
            status: resp.status, 
            statusText: resp.statusText 
          };
        }
        
        return resp.json();
      });

      if (loginError) {
        throw loginError;
      }

      // Save the token in localStorage
      const { access_token, message, userId } = response;
      localStorage.setItem("token", access_token);

      // Fetch the user details from the database using the access_token
      const [userData, userError] = await tryCatch<User>(async () => {
        return fetchWithErrorHandling<User>(getApiUrl("/api/auth/me"), {
          method: "GET",
          headers: {
            Authorization: `Bearer ${access_token}`,
          },
        });
      });

      if (userError) {
        // If user details fetch fails, clear the token
        localStorage.removeItem("token");
        handleError(userError, {
          defaultMessage: "Failed to load user details after successful login.",
          showToast: false // Don't show toast, let login page handle UI
        });
        return false;
      }

      // Set the user state and save it in localStorage
      setUser(userData);
      localStorage.setItem("user", JSON.stringify(userData));

      // Show success notification
      notification.notifySuccess("Login successful!");
      
      // Redirect to dashboard after a short delay to allow toast to be seen
      setTimeout(() => {
        router.push("/dashboard");
      }, 1000);
      
      return true;
    } catch (err) {
      handleError(err, {
        defaultMessage: "Login failed. Please check your credentials.",
        context: "Authentication",
        showToast: false // Don't show toast, let login page handle UI
      });
      return false;
    } finally {
      setIsLoading(false);
    }
  }

  // Sign up function using the backend auth/register endpoint
  const signUp = async (name: string, email: string, password: string, age: string, gender: string) => {
    setIsLoading(true)

    try {
      // Make a POST request to the auth/register endpoint
      const [response, signupError] = await tryCatch(async () => {
        const resp = await fetch(getApiUrl("/api/auth/register"), {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ name, email, password, age, gender }),
        });

        if (!resp.ok) {
          const errorData = await resp.json().catch(() => ({}));
          throw { 
            ...errorData, 
            status: resp.status, 
            statusText: resp.statusText 
          };
        }

        return resp.json();
      });

      if (signupError) {
        throw signupError;
      }
      
      // Show success notification - only display this toast here, not in the signup page
      notification.notifySuccess("Account created successfully! Please log in.");
      
      return true;
    } catch (error) {
      handleError(error, {
        defaultMessage: "Registration failed. Please check your details.",
        context: "Registration",
        showToast: false // Let the signup page handle the error display
      });
      return false;
    } finally {
      setIsLoading(false);
    }
  }

  // Sign out function
  const signOut = () => {
    // Clear the token and user from localStorage
    localStorage.removeItem("token");
    localStorage.removeItem("user");

    // Clear the user state
    setUser(null);

    // Show success notification
    notification.notifySuccess("You have been logged out successfully.");

    // Redirect to the login page
    router.push("/login");
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, signIn, signUp, signOut }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}