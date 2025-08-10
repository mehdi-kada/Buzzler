"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/store/authStore";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, user, isLoading, isHydrated, checkAuth } =
    useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (isHydrated && !isLoading) {
      if (!isAuthenticated || !user) {
        router.push("/auth/login");
      }
    }
  }, [isAuthenticated, user, isLoading, isHydrated, router]);

  if (!isHydrated || isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-2">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-2">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
