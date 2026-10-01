"use client";

import { useCallback, useEffect, useState } from "react";
import { Cabecalho, Erro } from "@/components/AppShell";
import { Badge } from "@/components/Badge";
import { Evidencias } from "@/components/Evidencias";
import { Paginacao } from "@/components/Paginacao";
import { api, query } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { RISCOS, STATUS_ALERTA, type Alerta, type Pagina, type StatusAlerta } from "@/lib/types";

const TAMANHO = 15;

export default function AlertasPage() {
  const { pode } = useAuth();
  const podeTratar = pode("admin", "analista");
  const [status, setStatus] = useState<string>("Aberto");
  const [severidade, setSeveridade] = useState("");
  const [pagina, setPagina] = useState(1);
  const [dados, setDados] = useState<Pagina<Alerta> | null>(null);
  const [selecionado, setSelecionado] = useState<Alerta | null>(null);
  const [observacao, setObservacao] = useState("");
  const [erro, setErro] = useState<string | null>(null);

  const carregar = useCallback(() => {
    api<Pagina<Alerta>>(`/alertas${query({ status, severidade, pagina, tamanho: TAMANHO })}`)
      .then(setDados)
      .catch((e: Error) => setErro(e.message));
  }, [status, severidade, pagina]);

  useEffect(carregar, [carregar]);

  async function atualizar(novoStatus: StatusAlerta) {
    if (!selecionado) return;
    try {
      const atualizado = await api<Alerta>(`/alertas/${selecionado.id}`, {
        method: "PATCH",
        body: JSON.stringify({ status: novoStatus, observacao }),
      });
      setSelecionado(atualizado);
      carregar();
    } catch (e) {
      setErro((e as Error).message);
    }
  }

  function selecionar(a: Alerta) {
    setSelecionado(a);
    setObservacao(a.observacao);
  }

  return (
    <>
      <Cabecalho titulo="Alertas" subtitulo="Workflow de tratamento de eventos de risco alto e crítico" />
      <Erro mensagem={erro} />
      <div className="card mb-4 flex gap-3">
        <select
          className="input w-48"
          value={status}
          onChange={(e) => {
            setStatus(e.target.value);
            setPagina(1);
          }}
        >
          <option value="">Todos os status</option>
          {STATUS_ALERTA.map((s) => (
            <option key={s}>{s}</option>
          ))}
        </select>
        <select
          className="input w-48"
          value={severidade}
          onChange={(e) => {
            setSeveridade(e.target.value);
            setPagina(1);
          }}
        >
          <option value="">Todas as severidades</option>
          {RISCOS.map((r) => (
            <option key={r}>{r}</option>
          ))}
        </select>
      </div>
      <div className="grid gap-6 xl:grid-cols-5">
        <div className="xl:col-span-3">
          <div className="card overflow-x-auto p-0">
            <table className="table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Criado em</th>
                  <th>Ferramenta</th>
                  <th>Tipo</th>
                  <th>Severidade</th>
                  <th>Status</th>
                  <th>Responsável</th>
                </tr>
              </thead>
              <tbody>
                {dados?.itens.map((a) => (
                  <tr
                    key={a.id}
                    onClick={() => selecionar(a)}
                    className={`cursor-pointer hover:bg-slate-50 ${selecionado?.id === a.id ? "bg-indigo-50" : ""}`}
                  >
                    <td>{a.id}</td>
                    <td className="whitespace-nowrap">{new Date(a.criado_em).toLocaleString("pt-BR")}</td>
                    <td>{a.evento.ferramenta_nome}</td>
                    <td>{a.evento.tipo_informacao}</td>
                    <td>
                      <Badge valor={a.severidade} />
                    </td>
                    <td>
                      <Badge valor={a.status} />
                    </td>
                    <td className="text-xs">{a.responsavel ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {dados && <Paginacao pagina={pagina} tamanho={TAMANHO} total={dados.total} onChange={setPagina} />}
        </div>
        <div className="xl:col-span-2">
          {selecionado ? (
            <div className="card space-y-3">
              <div className="flex items-center justify-between">
                <h2 className="font-semibold">Alerta #{selecionado.id}</h2>
                <Badge valor={selecionado.status} />
              </div>
              <dl className="grid grid-cols-2 gap-2 text-sm">
                <dt className="text-slate-500">Evento</dt>
                <dd className="font-mono text-xs">{selecionado.evento_id}</dd>
                <dt className="text-slate-500">Usuário</dt>
                <dd className="font-mono text-xs">{selecionado.evento.id_usuario}</dd>
                <dt className="text-slate-500">Ferramenta</dt>
                <dd>{selecionado.evento.ferramenta_nome}</dd>
                <dt className="text-slate-500">Sensibilidade</dt>
                <dd>
                  <Badge valor={selecionado.evento.sensibilidade} />
                </dd>
                <dt className="text-slate-500">Finalidade</dt>
                <dd>{selecionado.evento.finalidade}</dd>
              </dl>
              <div>
                <div className="mb-1 text-xs font-semibold text-slate-500">Evidências</div>
                <Evidencias itens={selecionado.evento.evidencias} />
              </div>
              <label className="block text-sm">
                Observação
                <textarea
                  className="input mt-1"
                  rows={3}
                  value={observacao}
                  disabled={!podeTratar}
                  onChange={(e) => setObservacao(e.target.value)}
                />
              </label>
              {podeTratar ? (
                <div className="flex gap-2">
                  <button className="btn-secondary" onClick={() => atualizar("Em análise")}>
                    Em análise
                  </button>
                  <button className="btn" onClick={() => atualizar("Tratado")}>
                    Marcar como tratado
                  </button>
                  <button className="btn-secondary" onClick={() => atualizar("Aberto")}>
                    Reabrir
                  </button>
                </div>
              ) : (
                <p className="text-xs text-slate-500">Seu perfil é somente leitura.</p>
              )}
            </div>
          ) : (
            <div className="card text-sm text-slate-500">Selecione um alerta para ver os detalhes e tratá-lo.</div>
          )}
        </div>
      </div>
    </>
  );
}
