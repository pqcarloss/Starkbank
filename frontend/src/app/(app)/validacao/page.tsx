"use client";

import { useEffect, useState } from "react";
import { Cabecalho, Erro } from "@/components/AppShell";
import { Badge } from "@/components/Badge";
import { api } from "@/lib/api";
import type { CasoValidacao, ExecucaoValidacao } from "@/lib/types";

export default function ValidacaoPage() {
  const [casos, setCasos] = useState<CasoValidacao[]>([]);
  const [execucao, setExecucao] = useState<ExecucaoValidacao | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [executando, setExecutando] = useState(false);

  useEffect(() => {
    api<CasoValidacao[]>("/casos-validacao")
      .then(setCasos)
      .catch((e: Error) => setErro(e.message));
  }, []);

  async function executar() {
    setExecutando(true);
    try {
      setExecucao(await api<ExecucaoValidacao>("/casos-validacao/executar", { method: "POST" }));
    } catch (e) {
      setErro((e as Error).message);
    } finally {
      setExecutando(false);
    }
  }

  const resultado = (id: number) => execucao?.resultados.find((r) => r.caso.id === id);

  return (
    <>
      <Cabecalho
        titulo="Casos de validação"
        subtitulo="Referências de negócio (Segurança/Compliance) para testar o motor de classificação"
        acoes={
          <button className="btn" onClick={executar} disabled={executando}>
            {executando ? "Executando…" : "Executar validação"}
          </button>
        }
      />
      <Erro mensagem={erro} />
      {execucao && (
        <div className="card mb-4 text-sm">
          <span className="text-2xl font-bold">{Math.round(execucao.taxa_acerto * 100)}%</span> de acerto ·{" "}
          {execucao.aprovados} de {execucao.total} casos aprovados
        </div>
      )}
      <div className="card overflow-x-auto p-0">
        <table className="table">
          <thead>
            <tr>
              <th>Caso</th>
              <th>Ferramenta</th>
              <th>Entrada</th>
              <th>Esperado</th>
              <th>Obtido</th>
              <th>Resultado</th>
            </tr>
          </thead>
          <tbody>
            {casos.map((c) => {
              const r = resultado(c.id);
              return (
                <tr key={c.id}>
                  <td className="font-medium">{c.descricao}</td>
                  <td>{c.ferramenta_nome}</td>
                  <td className="max-w-xs whitespace-pre-wrap font-mono text-xs text-slate-600">
                    {c.texto_entrada.length > 140 ? `${c.texto_entrada.slice(0, 140)}…` : c.texto_entrada}
                  </td>
                  <td className="space-y-1">
                    <Badge valor={c.sensibilidade_esperada} /> <Badge valor={c.risco_esperado} />
                  </td>
                  <td className="space-y-1">
                    {r ? (
                      <>
                        <Badge valor={r.sensibilidade_obtida} /> <Badge valor={r.risco_obtido} />
                      </>
                    ) : (
                      "—"
                    )}
                  </td>
                  <td>
                    {r ? (
                      <span className={r.aprovado ? "font-semibold text-green-700" : "font-semibold text-red-700"}>
                        {r.aprovado ? "Aprovado" : "Reprovado"}
                      </span>
                    ) : (
                      "—"
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </>
  );
}
