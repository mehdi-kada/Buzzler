import { create } from "zustand";
import { persist } from "zustand/middleware";

interface User {
  email: string;
  first_name: string;
}

interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  accessToken: string | null;
  isLoading: boolean;
  isHydrated: boolean;
  login: (accessToken: string, user: User) => void;
  logout: () => void;
  setAccessToken: (token: string) => void;
  setLoading: (loading: boolean) => void;
  setHydrated: (hydrated: boolean) => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      isAuthenticated: false,
      user: null,
      accessToken: null,
      isLoading: true,
      isHydrated: false,

      login: (accessToken, user) => {
        set({ isAuthenticated: true, accessToken, user, isLoading: false });
      },

      logout: () => {
        set({
          isAuthenticated: false,
          accessToken: null,
          user: null,
          isLoading: false,
        });
        // Clear cookies
        document.cookie =
          "refresh_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=localhost";
        document.cookie =
          "csrf_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=localhost";
      },

      setAccessToken: (token) => {
        set({ accessToken: token });
      },

      setLoading: (loading) => {
        set({ isLoading: loading });
      },

      setHydrated: (hydrated) => {
        set({ isHydrated: hydrated });
      },

      checkAuth: async () => {
        const { isAuthenticated, accessToken } = get();

        // If we think we're authenticated but have no access token, try to refresh
        if (isAuthenticated && !accessToken) {
          try {
            const response = await fetch("http://localhost:8000/auth/refresh", {
              method: "POST",
              credentials: "include",
            });

            if (response.ok) {
              const data = await response.json();
              set({ accessToken: data.access_token, isLoading: false });
              return;
            }
          } catch (error) {
            console.log("Token refresh failed during auth check");
          }

          get().logout();
          return;
        }

        // If we have both isAuthenticated and accessToken, we re good
        if (isAuthenticated && accessToken) {
          set({ isLoading: false });
          return;
        }

        // Otherwise, we re not authenticated
        set({
          isAuthenticated: false,
          accessToken: null,
          user: null,
          isLoading: false,
        });
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        // Don't persist accessToken for security - it will be refreshed
      }),
      onRehydrateStorage: () => (state) => {
        state?.setHydrated(true);
        // Check auth status after rehydration
        state?.checkAuth();
      },
    }
  )
);
