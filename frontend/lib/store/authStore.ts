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
        // server cleans http-only cookie while the clinet clean non http-only 
        document.cookie =
          "csrf_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/";
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

        if (isAuthenticated && !accessToken) {
          try {
            const match = document.cookie.match(/csrf_token=([^;]+)/);
            const csrf = match ? match[1] : undefined;
            const response = await fetch("http://localhost:8000/auth/refresh", {
              method: "POST",
              credentials: "include",
              headers: csrf ? { "X-CSRF-Token": csrf } : undefined,
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

        if (isAuthenticated && accessToken) {
          set({ isLoading: false });
          return;
        }
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
      }),
      onRehydrateStorage: () => (state) => {
        state?.setHydrated(true);
        state?.checkAuth();
      },
    }
  )
);
