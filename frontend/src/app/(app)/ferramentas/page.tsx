"use client";

import { useCallback, useEffect, useState } from "react";
import { Cabecalho, Erro } from "@/components/AppShell";
import { Badge } from "@/components/Badge";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { STATUS_FERRAMENTA, type Ferramenta, type StatusFerramenta } from "@/lib/types";

const VAZIO = { nome: "", fornecedor: "", status: "Não aprovada" as StatusFerramenta, observacoes: "" };

export default function FerramentasPage() {
  const { pode } = useAuth();
  const admin = pode("admin");
  const [itens, setItens] = useState<Ferramenta[]>([]);
  const [nova, setNova] = useState(VAZIO);
  const [erro, setErro] = useState<string | null>(null);

  const carregar = useCallback(() => {
    api<Ferramenta[]>("/ferramentas")
      .then(setItens)
      .catch((e: Error) => setErro(e.message));
  }, []);
  useEffect(carregar, [carregar]);

  async function alterarStatus(f: Ferramenta, status: StatusFerramenta) {
    try {
      await api(`/ferramentas/${f.id}`, { method: "PATCH", body: JSON.stringify({ status }) });
      carregar();
    } catch (e) {
      setErro((e as Error).message);
    }
  }

  async function criar(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api("/ferramentas", { method: "POST", body: JSON.stringify(nova) });
      setNova(VAZIO);
      carregar();
    } catch (err) {
      setErro((err as Error).message);
    }
  }

  return (
    <>
      <Cabecalho titulo="Ferramentas de IA" subtitulo="Inventário e status de aprovação pela Governança de IA" />
      <Erro mensagem={erro} />
      <div className="card overflow-x-auto p-0">
        <table className="table">
          <thead>
            <tr>
              <th>Ferramenta</th>
              <th>Fornecedor</th>
              <th>Status</th>
              <th>Observações</th>
            </tr>
          </thead>
          <tbody>
            {itens.map((f) => (
              <tr key={f.id}>
                <td className="font-medium">{f.nome}</td>
                <td>{f.fornecedor}</td>
                <td>
                  {admin ? (
                    <select
                      className="input w-52"
                      value={f.status}
                      onChange={(e) => alterarStatus(f, e.target.value as StatusFerramenta)}
                    >
                      {STATUS_FERRAMENTA.map((s) => (
                        <option key={s}>{s}</option>
                      ))}
                    </select>
                  ) : (
                    <Badge valor={f.status} />
                  )}
                </td>
                <td className="text-xs text-slate-600">{f.observacoes}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {admin && (
        <form onSubmit={criar} className="card mt-6 grid gap-3 md:grid-cols-5">
          <input
            className="input"
            placeholder="Nome"
            value={nova.nome}
            onChange={(e) => setNova({ ...nova, nome: e.target.value })}
            required
          />
          <input
            className="input"
            placeholder="Fornecedor"
            value={nova.fornecedor}
            onChange={(e) => setNova({ ...nova, fornecedor: e.target.value })}
          />
          <select
            className="input"
            value={nova.status}
            onChange={(e) => setNova({ ...nova, status: e.target.value as StatusFerramenta })}
          >
            {STATUS_FERRAMENTA.map((s) => (
              <option key={s}>{s}</option>
            ))}
          </select>
          <input
            className="input"
            placeholder="Observações"
            value={nova.observacoes}
            onChange={(e) => setNova({ ...nova, observacoes: e.target.value })}
          />
          <button className="btn">Adicionar ferramenta</button>
        </form>
      )}
    </>
  );
}
