"use client";

import { useCallback, useEffect, useState } from "react";
import { Cabecalho, Erro } from "@/components/AppShell";
import { Badge } from "@/components/Badge";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { SENSIBILIDADES, type Sensibilidade, type TipoInformacao } from "@/lib/types";

export default function TiposPage() {
  const { pode } = useAuth();
  const admin = pode("admin");
  const [itens, setItens] = useState<TipoInformacao[]>([]);
  const [erro, setErro] = useState<string | null>(null);

  const carregar = useCallback(() => {
    api<TipoInformacao[]>("/tipos-informacao")
      .then(setItens)
      .catch((e: Error) => setErro(e.message));
  }, []);
  useEffect(carregar, [carregar]);

  async function alterar(t: TipoInformacao, classificacao_padrao: Sensibilidade) {
    try {
      await api(`/tipos-informacao/${t.id}`, { method: "PATCH", body: JSON.stringify({ classificacao_padrao }) });
      carregar();
    } catch (e) {
      setErro((e as Error).message);
    }
  }

  return (
    <>
      <Cabecalho
        titulo="Tipos de informação"
        subtitulo="Classificação padrão por tipo de informação (Governança de Dados) — usada pelo motor DLP"
      />
      <Erro mensagem={erro} />
      <div className="card overflow-x-auto p-0">
        <table className="table">
          <thead>
            <tr>
              <th>Tipo</th>
              <th>Descrição</th>
              <th>Classificação padrão</th>
            </tr>
          </thead>
          <tbody>
            {itens.map((t) => (
              <tr key={t.id}>
                <td className="font-medium">{t.nome}</td>
                <td className="text-slate-600">{t.descricao}</td>
                <td>
                  {admin ? (
                    <select
                      className="input w-44"
                      value={t.classificacao_padrao}
                      onChange={(e) => alterar(t, e.target.value as Sensibilidade)}
                    >
                      {SENSIBILIDADES.map((s) => (
                        <option key={s}>{s}</option>
                      ))}
                    </select>
                  ) : (
                    <Badge valor={t.classificacao_padrao} />
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
