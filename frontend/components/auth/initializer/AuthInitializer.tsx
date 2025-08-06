"use client";

import { useEffect } from "react";
import { useAuthStore } from "@/lib/store/authStore";

export function AuthInitializer() {
  const { isHydrated, checkAuth } = useAuthStore();

  useEffect(() => {
    // Only run checkAuth after the store has been hydrated
    if (isHydrated) {
      checkAuth();
    }
  }, [isHydrated, checkAuth]);

  // This component doesn't render anything
  return null;
}
