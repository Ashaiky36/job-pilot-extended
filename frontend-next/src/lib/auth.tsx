"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  type ReactNode,
} from "react";
import { useRouter, usePathname } from "next/navigation";
import {
  getMe,
  loginUser,
  registerUser,
  setToken,
  clearToken,
  getToken,
  type AuthUser,
} from "@/lib/api";

interface AuthContextType {
  user: AuthUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

const PUBLIC_PATHS = ["/", "/login"];

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  const refreshUser = useCallback(async () => {
    try {
      const token = getToken();
      if (!token) {
        setUser(null);
        return;
      }
      const me = await getMe();
      setUser(me);
    } catch {
      clearToken();
      setUser(null);
    }
  }, []);

  // Check auth on mount
  useEffect(() => {
    refreshUser().finally(() => setLoading(false));
  }, [refreshUser]);

  // Redirect logic
  useEffect(() => {
    if (loading) return;

    const isPublic = PUBLIC_PATHS.includes(pathname);

    if (!user && !isPublic) {
      // Not logged in and on protected route → go to login
      router.replace("/login");
    } else if (user && !user.is_onboarded && pathname !== "/onboarding") {
      // Logged in but not onboarded → go to onboarding
      if (!isPublic) router.replace("/onboarding");
    } else if (user && isPublic && pathname === "/login") {
      // Already logged in → go to dashboard or onboarding
      router.replace(user.is_onboarded ? "/dashboard" : "/onboarding");
    }
  }, [user, loading, pathname, router]);

  const login = useCallback(
    async (email: string, password: string) => {
      const data = await loginUser(email, password);
      setToken(data.token);
      setUser(data.user);
      router.push(data.user.is_onboarded ? "/dashboard" : "/onboarding");
    },
    [router]
  );

  const register = useCallback(
    async (email: string, password: string, name: string) => {
      const data = await registerUser(email, password, name);
      setToken(data.token);
      setUser(data.user);
      router.push("/onboarding");
    },
    [router]
  );

  const logout = useCallback(() => {
    clearToken();
    setUser(null);
    router.push("/");
  }, [router]);

  return (
    <AuthContext.Provider
      value={{ user, loading, login, register, logout, refreshUser }}
    >
      {children}
    </AuthContext.Provider>
  );
}
