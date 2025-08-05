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
        localStorage.removeItem("auth-storage");
      },

      setAccessToken: (token) => {
        set({ accessToken: token });
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
