"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/lib/auth";

const NAV = [
  { href: "/dashboard", rotulo: "Dashboard" },
  { href: "/eventos", rotulo: "Eventos de uso de IA" },
  { href: "/alertas", rotulo: "Alertas" },
  { href: "/classificar", rotulo: "Analisar conteúdo (DLP)" },
  { href: "/ferramentas", rotulo: "Ferramentas de IA" },
  { href: "/tipos", rotulo: "Tipos de informação" },
  { href: "/validacao", rotulo: "Casos de validação" },
];

const PAPEL: Record<string, string> = { admin: "Administrador", analista: "Analista", leitor: "Leitor" };

export function AppShell({ children }: { children: React.ReactNode }) {
  const { usuario, carregando, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!carregando && !usuario) router.replace("/login");
  }, [carregando, usuario, router]);

  if (carregando || !usuario) {
    return <div className="flex h-screen items-center justify-center text-slate-500">Carregando…</div>;
  }

  return (
    <div className="flex min-h-screen">
      <aside className="flex w-64 shrink-0 flex-col bg-slate-900 text-slate-200">
        <div className="border-b border-slate-800 px-5 py-5">
          <div className="text-lg font-bold text-white">Starkbank DLP</div>
          <div className="text-xs text-slate-400">Governança de uso de IA</div>
        </div>
        <nav className="flex-1 space-y-1 px-3 py-4">
          {NAV.map((item) => {
            const ativo = pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`block rounded-lg px-3 py-2 text-sm ${ativo ? "bg-indigo-600 text-white" : "hover:bg-slate-800"}`}
              >
                {item.rotulo}
              </Link>
            );
          })}
        </nav>
        <div className="border-t border-slate-800 px-5 py-4 text-sm">
          <div className="font-medium text-white">{usuario.nome}</div>
          <div className="text-xs text-slate-400">
            {usuario.email} · {PAPEL[usuario.papel]}
          </div>
          <button onClick={logout} className="mt-3 text-xs text-indigo-300 hover:text-white">
            Sair
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-x-auto p-8">{children}</main>
    </div>
  );
}

export function Cabecalho({ titulo, subtitulo, acoes }: { titulo: string; subtitulo?: string; acoes?: React.ReactNode }) {
  return (
    <div className="mb-6 flex items-end justify-between gap-4">
      <div>
        <h1 className="text-2xl font-bold">{titulo}</h1>
        {subtitulo && <p className="text-sm text-slate-500">{subtitulo}</p>}
      </div>
      {acoes}
    </div>
  );
}

export function Erro({ mensagem }: { mensagem: string | null }) {
  if (!mensagem) return null;
  return <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">{mensagem}</div>;
}
