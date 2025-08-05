"use client";

import { useEffect, useRef } from "react";
import { useAuthStore } from "@/lib/store/authStore";
import { usePathname } from "next/navigation";
import api from "@/lib/axios";

// Pages that don't require authentication
const PUBLIC_ROUTES = [
  "/",
  "/auth/login",
  "/auth/register",
  "/auth/forgot-password",
  "/auth/reset-password",
  "/about",
  "/contact",
  "/pricing",
];

async function fetchUser() {
  try {
    const response = await api.get("/users/me");
    return response.data;
  } catch (error) {
    console.error("Failed to fetch user", error);
    return null;
  }
}

export function AuthInitializer({ children }: { children: React.ReactNode }) {
  const { setAccessToken, login, logout } = useAuthStore();
  const initialized = useRef(false);
  const pathname = usePathname();

  useEffect(() => {
    if (!initialized.current) {
      initialized.current = true;

      // Skip auth initialization for public routes
      if (PUBLIC_ROUTES.includes(pathname)) {
        console.log("Public route detected, skipping auth initialization");
        return;
      }

      const initializeAuth = async () => {
        try {
          const { data } = await api.post("/auth/refresh");
          if (data.access_token) {
            const user = await fetchUser();
            if (user) {
              login(data.access_token, user);
            } else {
              logout();
            }
          }
        } catch (error) {
          console.log("Auth initialization failed, redirecting to login");
          logout();
        }
      };

      initializeAuth();
    }
  }, [setAccessToken, login, logout, pathname]);

  return <>{children}</>;
}
