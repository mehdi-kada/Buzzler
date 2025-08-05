"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuthStore } from "@/lib/store/authStore";

export default function OAuthSuccessPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const login = useAuthStore((state) => state.login);

  useEffect(() => {
    const token = searchParams.get("token");
    const userParam = searchParams.get("user");

    if (token && userParam) {
      try {
        // Parse user data from URL parameter
        const userData = JSON.parse(userParam);

        console.log("Parsed user data:", userData);

        // Log the user in with the OAuth data
        login(token, userData);

        // Redirect to dashboard
        router.push("/dashboard");
      } catch (error) {
        console.error("Failed to parse OAuth user data:", error);
        router.push("/auth/login?error=oauth_error");
      }
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
