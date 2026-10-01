"use client";

import { useEffect, useState } from "react";
import { Cabecalho, Erro } from "@/components/AppShell";
import { Barras, Rosca, SerieTemporal } from "@/components/Graficos";
import { api } from "@/lib/api";
import { COR_RISCO, COR_SENSIBILIDADE, COR_STATUS_ALERTA, PALETA } from "@/lib/cores";
import type { DashboardResumo } from "@/lib/types";

function Kpi({ titulo, valor, destaque }: { titulo: string; valor: number | string; destaque?: string }) {
  return (
    <div className="card">
      <div className="text-xs font-medium uppercase tracking-wide text-slate-500">{titulo}</div>
      <div className="mt-1 text-3xl font-bold" style={destaque ? { color: destaque } : undefined}>
        {valor}
      </div>
    </div>
  );
}

function Painel({ titulo, children, className = "" }: { titulo: string; children: React.ReactNode; className?: string }) {
  return (
    <div className={`card ${className}`}>
      <h2 className="mb-3 text-sm font-semibold text-slate-700">{titulo}</h2>
      <div className="h-64">{children}</div>
    </div>
  );
}

export default function DashboardPage() {
  const [dias, setDias] = useState(30);
  const [dados, setDados] = useState<DashboardResumo | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    api<DashboardResumo>(`/dashboard/resumo?dias=${dias}`)
      .then((d) => {
        setDados(d);
        setErro(null);
      })
      .catch((e: Error) => setErro(e.message));
  }, [dias]);

  const pctAlto = dados && dados.total_eventos ? Math.round((dados.eventos_alto_critico / dados.total_eventos) * 100) : 0;

  return (
    <>
      <Cabecalho
        titulo="Dashboard"
        subtitulo="Visão consolidada do uso de ferramentas de IA, sensibilidade e risco"
        acoes={
          <select className="input w-40" value={dias} onChange={(e) => setDias(Number(e.target.value))}>
            <option value={7}>Últimos 7 dias</option>
            <option value={30}>Últimos 30 dias</option>
            <option value={90}>Últimos 90 dias</option>
          </select>
        }
      />
      <Erro mensagem={erro} />
      {dados && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
            <Kpi titulo="Eventos de uso" valor={dados.total_eventos} />
            <Kpi titulo="Risco alto/crítico" valor={`${dados.eventos_alto_critico} (${pctAlto}%)`} destaque="#dc2626" />
            <Kpi titulo="Alertas pendentes" valor={dados.alertas_abertos} destaque="#f97316" />
            <Kpi titulo="Uso em IA não aprovada" valor={dados.eventos_ferramentas_nao_aprovadas} destaque="#be123c" />
            <Kpi titulo="Usuários distintos" valor={dados.usuarios_distintos} />
          </div>
          <Painel titulo="Eventos por dia" className="col-span-full">
            <SerieTemporal dados={dados.serie_diaria} />
          </Painel>
          <div className="grid gap-6 lg:grid-cols-3">
            <Painel titulo="Eventos por risco">
              <Rosca dados={dados.por_risco} mapa={COR_RISCO} />
            </Painel>
            <Painel titulo="Eventos por sensibilidade">
              <Barras dados={dados.por_sensibilidade} mapa={COR_SENSIBILIDADE} />
            </Painel>
            <Painel titulo="Alertas por status">
              <Rosca dados={dados.alertas_por_status} mapa={COR_STATUS_ALERTA} />
            </Painel>
          </div>
          <div className="grid gap-6 lg:grid-cols-2">
            <Painel titulo="Top ferramentas de IA">
              <Barras dados={dados.por_ferramenta} paleta={PALETA} horizontal />
            </Painel>
            <Painel titulo="Tipos de informação detectados">
              <Barras dados={dados.por_tipo_informacao} paleta={PALETA} horizontal />
            </Painel>
          </div>
        </div>
      )}
    </>
  );
}
