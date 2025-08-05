"use client"

import { useEffect, useRef } from 'react';
import { useAuthStore } from '@/lib/store/authStore';
import api from '@/lib/axios';

async function fetchUser() {
    try {
        const response = await api.get('/users/me'); 
        return response.data;
    } catch (error) {
        console.error("Failed to fetch user", error);
        return null;
    }
}

export function AuthInitializer({ children }: { children: React.ReactNode }) {
  const { setAccessToken, login, logout } = useAuthStore();
  const initialized = useRef(false);

  useEffect(() => {
    if (!initialized.current) {
      initialized.current = true;

      const initializeAuth = async () => {
        try {
          const { data } = await api.post('/auth/refresh');
          if (data.access_token) {
            setAccessToken(data.access_token);
            const user = await fetchUser();
            if (user) {
                login(data.access_token, user);
            } else {
                logout();
            }
          }
        } catch (error) {
          logout();
        }
      };

      initializeAuth();
    }
  }, [setAccessToken, login, logout]);

  return <>{children}</>;
}
