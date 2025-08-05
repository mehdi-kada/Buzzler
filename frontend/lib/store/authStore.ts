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
  login: (accessToken: string, user: User) => void;
  logout: () => void;
  setAccessToken: (token: string) => void;
  initializeAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      isAuthenticated: false,
      user: null,
      accessToken: null,

      login: (accessToken, user) => {
        set({ isAuthenticated: true, accessToken, user });
      },

      logout: () => {
        set({ isAuthenticated: false, accessToken: null, user: null });
        // Clear any stored tokens
        localStorage.removeItem("auth-storage");
      },

      setAccessToken: (token) => {
        set({ accessToken: token });
      },

      initializeAuth: () => {
        // Check if we have a valid token on app startup
        const { accessToken } = get();
        if (accessToken) {
          // In a real app, you'd verify the token with the backend
          // For now, we assume it's valid if it exists
          set({ isAuthenticated: true });
        }
      },
    }),
    {
      name: "auth-storage",
      // Only persist user data, not sensitive tokens
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
