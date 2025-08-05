"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuthStore } from "@/lib/store/authStore";
import api from "@/lib/axios";

export default function OAuthCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const login = useAuthStore((state) => state.login);

  useEffect(() => {
    const handleOAuthCallback = async () => {
      const code = searchParams.get("code");
      const provider = "google"; // or get from URL if you support multiple providers

      if (code) {
        try {
          // Send the code to your backend
          const response = await api.post("/auth/oauth/callback", {
            code,
            provider,
          });

          const { access_token, user } = response.data;

          // Log the user in
          login(access_token, user);

          // Redirect to dashboard
          router.push("/dashboard");
        } catch (error) {
          console.error("OAuth callback failed:", error);
          router.push("/auth/login?error=oauth_error");
        }
      } else {
        router.push("/auth/login?error=oauth_error");
      }
    };

    handleOAuthCallback();
  }, [searchParams, login, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Completing your Google login...</p>
      </div>
    </div>
  );
}
