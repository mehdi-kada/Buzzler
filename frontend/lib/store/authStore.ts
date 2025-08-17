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
        // server cleans http-only cookie while the client clean non http-only 
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

        // If we have both auth state and token, we're good
        if (isAuthenticated && accessToken) {
          set({ isLoading: false });
          return;
        }

        // If we think we're authenticated but don't have a token, try to refresh
        if (isAuthenticated && !accessToken) {
          try {
            // Import api dynamically to avoid circular imports
            const { default: api } = await import("../axios/auth_interceptor");
            const response = await api.post("/auth/refresh");
            set({ accessToken: response.data.access_token, isLoading: false });
            return;
          } catch (error) {
            // Refresh failed, clear auth state
            get().logout();
            return;
          }
        }

        // Not authenticated, ensure clean state
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
