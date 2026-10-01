"use client";

import { Fragment, useEffect, useState } from "react";
import { Cabecalho, Erro } from "@/components/AppShell";
import { Badge } from "@/components/Badge";
import { Evidencias } from "@/components/Evidencias";
import { Paginacao } from "@/components/Paginacao";
import { api, query } from "@/lib/api";
import { RISCOS, SENSIBILIDADES, type Evento, type Ferramenta, type Pagina, type TipoInformacao } from "@/lib/types";

const TAMANHO = 20;

export default function EventosPage() {
  const [filtros, setFiltros] = useState({ risco: "", sensibilidade: "", ferramenta: "", tipo_informacao: "" });
  const [pagina, setPagina] = useState(1);
  const [dados, setDados] = useState<Pagina<Evento> | null>(null);
  const [ferramentas, setFerramentas] = useState<Ferramenta[]>([]);
  const [tipos, setTipos] = useState<TipoInformacao[]>([]);
  const [aberto, setAberto] = useState<string | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    api<Ferramenta[]>("/ferramentas").then(setFerramentas).catch(() => undefined);
    api<TipoInformacao[]>("/tipos-informacao").then(setTipos).catch(() => undefined);
  }, []);

  useEffect(() => {
    api<Pagina<Evento>>(`/eventos${query({ ...filtros, pagina, tamanho: TAMANHO })}`)
      .then(setDados)
      .catch((e: Error) => setErro(e.message));
  }, [filtros, pagina]);

  function filtrar(campo: keyof typeof filtros, valor: string) {
    setFiltros((f) => ({ ...f, [campo]: valor }));
    setPagina(1);
  }

  return (
    <>
      <Cabecalho titulo="Eventos de uso de IA" subtitulo="Rastreabilidade de cada interação com ferramentas de IA" />
      <Erro mensagem={erro} />
      <div className="card mb-4 grid grid-cols-2 gap-3 lg:grid-cols-4">
        <select className="input" value={filtros.risco} onChange={(e) => filtrar("risco", e.target.value)}>
          <option value="">Todos os riscos</option>
          {RISCOS.map((r) => (
            <option key={r}>{r}</option>
          ))}
        </select>
        <select className="input" value={filtros.sensibilidade} onChange={(e) => filtrar("sensibilidade", e.target.value)}>
          <option value="">Todas as sensibilidades</option>
          {SENSIBILIDADES.map((s) => (
            <option key={s}>{s}</option>
          ))}
        </select>
        <select className="input" value={filtros.ferramenta} onChange={(e) => filtrar("ferramenta", e.target.value)}>
          <option value="">Todas as ferramentas</option>
          {ferramentas.map((f) => (
            <option key={f.id}>{f.nome}</option>
          ))}
        </select>
        <select className="input" value={filtros.tipo_informacao} onChange={(e) => filtrar("tipo_informacao", e.target.value)}>
          <option value="">Todos os tipos</option>
          {tipos.map((t) => (
            <option key={t.id}>{t.nome}</option>
          ))}
        </select>
      </div>
      <div className="card overflow-x-auto p-0">
        <table className="table">
          <thead>
            <tr>
              <th>ID evento</th>
              <th>Data/hora</th>
              <th>ID usuário</th>
              <th>Ferramenta</th>
              <th>Tipo informação</th>
              <th>Sensibilidade</th>
              <th>Finalidade</th>
              <th>Risco</th>
              <th>Alerta</th>
            </tr>
          </thead>
          <tbody>
            {dados?.itens.map((ev) => (
              <Fragment key={ev.id}>
                <tr className="cursor-pointer hover:bg-slate-50" onClick={() => setAberto(aberto === ev.id ? null : ev.id)}>
                  <td className="font-mono text-xs">{ev.id}</td>
                  <td className="whitespace-nowrap">{new Date(ev.data_hora).toLocaleString("pt-BR")}</td>
                  <td className="font-mono text-xs">{ev.id_usuario}</td>
                  <td>{ev.ferramenta_nome}</td>
                  <td>{ev.tipo_informacao}</td>
                  <td>
                    <Badge valor={ev.sensibilidade} />
                  </td>
                  <td className="text-xs">{ev.finalidade}</td>
                  <td>
                    <Badge valor={ev.risco} />
                  </td>
                  <td>{ev.alerta ? <Badge valor={ev.alerta.status} /> : <span className="text-slate-400">—</span>}</td>
                </tr>
                {aberto === ev.id && (
                  <tr className="bg-slate-50">
                    <td colSpan={9}>
                      <div className="grid gap-4 py-2 md:grid-cols-3">
                        <div className="md:col-span-2">
                          <div className="mb-1 text-xs font-semibold text-slate-500">Evidências</div>
                          <Evidencias itens={ev.evidencias} />
                        </div>
                        <div className="text-xs text-slate-600">
                          <div>Tipos detectados: {ev.tipos_detectados.join(", ") || "—"}</div>
                          <div>Classificador: {ev.classificador}</div>
                          <div>Tamanho do conteúdo: {ev.conteudo_tamanho} caracteres</div>
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </Fragment>
            ))}
          </tbody>
        </table>
      </div>
      {dados && <Paginacao pagina={pagina} tamanho={TAMANHO} total={dados.total} onChange={setPagina} />}
    </>
  );
}
