"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api, getToken, setToken } from "@/lib/api";
import type { Papel, Usuario } from "@/lib/types";

interface AuthState {
  usuario: Usuario | null;
  carregando: boolean;
  login: (email: string, senha: string) => Promise<void>;
  logout: () => void;
  pode: (...papeis: Papel[]) => boolean;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    if (!getToken()) {
      setCarregando(false);
      return;
    }
    api<Usuario>("/auth/me")
      .then(setUsuario)
      .catch(() => setToken(null))
      .finally(() => setCarregando(false));
  }, []);

  const login = useCallback(async (email: string, senha: string) => {
    const body = new URLSearchParams({ username: email, password: senha });
    const { access_token } = await api<{ access_token: string }>("/auth/login", {
      method: "POST",
      body,
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    setToken(access_token);
    setUsuario(await api<Usuario>("/auth/me"));
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setUsuario(null);
    window.location.href = "/login";
  }, []);

  const pode = useCallback((...papeis: Papel[]) => !!usuario && papeis.includes(usuario.papel), [usuario]);

  return (
    <AuthContext.Provider value={{ usuario, carregando, login, logout, pode }}>{children}</AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth deve ser usado dentro de AuthProvider");
  return ctx;
}
