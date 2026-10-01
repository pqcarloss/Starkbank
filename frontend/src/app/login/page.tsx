"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth";

export default function LoginPage() {
  const { login, usuario } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    if (usuario) router.replace("/dashboard");
  }, [usuario, router]);

  async function entrar(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);
    setEnviando(true);
    try {
      await login(email, senha);
      router.replace("/dashboard");
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Falha no login");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-900 p-4">
      <form onSubmit={entrar} className="w-full max-w-sm space-y-4 rounded-2xl bg-white p-8 shadow-xl">
        <div>
          <h1 className="text-xl font-bold">Starkbank DLP</h1>
          <p className="text-sm text-slate-500">Governança de uso de IA — acesse com sua conta</p>
        </div>
        {erro && <div className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{erro}</div>}
        <label className="block text-sm">
          E-mail
          <input className="input mt-1" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoFocus />
        </label>
        <label className="block text-sm">
          Senha
          <input className="input mt-1" type="password" value={senha} onChange={(e) => setSenha(e.target.value)} required />
        </label>
        <button className="btn w-full" disabled={enviando}>
          {enviando ? "Entrando…" : "Entrar"}
        </button>
        <button type="button" className="btn-secondary w-full" disabled title="Disponível na próxima fase (SSO/OAuth2)">
          Entrar com SSO corporativo (em breve)
        </button>
      </form>
    </div>
  );
}
