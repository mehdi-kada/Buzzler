"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuthStore } from "@/lib/store/authStore";
import axios from "axios";

export default function OAuthSuccessPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const login = useAuthStore((state) => state.login);

  useEffect(() => {
    const token = searchParams.get("token");
    const userParam = searchParams.get("user");

    if (token && userParam) {
      const setupSession = async () => {
        try {
          // Parse user data from URL parameter
          const userSearchParams = new URLSearchParams(userParam);
          const userData = {
            email: userSearchParams.get("email") || "",
            first_name: userSearchParams.get("first_name") || "",
          };

          console.log("Parsed user data:", userData);

          // Log the user in with the OAuth data first
          login(token, userData);

          // Setup session with refresh token and CSRF token
          await axios.post(
            "http://localhost:8000/auth/setup-session",
            {},
            {
              headers: {
                Authorization: `Bearer ${token}`,
              },
              withCredentials: true,
            }
          );

          console.log("Session setup completed successfully");

          // Redirect to dashboard
          router.push("/dashboard");
        } catch (error) {
          console.error("Failed to setup session:", error);
          router.push("/auth/login?error=session_setup_failed");
        }
      };

      setupSession();
    } else {
      // No token or user data, redirect to login with error
      console.log("Missing token or user data, redirecting to login");
      router.push("/auth/login?error=oauth_error");
    }
  }, [searchParams, login, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Completing your login...</p>
      </div>
    </div>
  );
}
