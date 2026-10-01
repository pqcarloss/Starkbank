"use client";

import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
} from "chart.js";
import { Bar, Doughnut, Line } from "react-chartjs-2";
import type { Contagem } from "@/lib/types";

ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, LineElement, PointElement, Tooltip, Legend, Filler);

function cores(itens: Contagem[], mapa?: Record<string, string>, paleta?: string[]): string[] {
  return itens.map((c, i) => mapa?.[c.rotulo] ?? paleta?.[i % paleta.length] ?? "#6366f1");
}

export function Rosca({ dados, mapa, paleta }: { dados: Contagem[]; mapa?: Record<string, string>; paleta?: string[] }) {
  return (
    <Doughnut
      data={{
        labels: dados.map((d) => d.rotulo),
        datasets: [{ data: dados.map((d) => d.total), backgroundColor: cores(dados, mapa, paleta), borderWidth: 1 }],
      }}
      options={{ maintainAspectRatio: false, plugins: { legend: { position: "right" } }, cutout: "60%" }}
    />
  );
}

export function Barras({
  dados,
  mapa,
  paleta,
  horizontal = false,
  rotulo = "Eventos",
}: {
  dados: Contagem[];
  mapa?: Record<string, string>;
  paleta?: string[];
  horizontal?: boolean;
  rotulo?: string;
}) {
  return (
    <Bar
      data={{
        labels: dados.map((d) => d.rotulo),
        datasets: [{ label: rotulo, data: dados.map((d) => d.total), backgroundColor: cores(dados, mapa, paleta), borderRadius: 4 }],
      }}
      options={{
        maintainAspectRatio: false,
        indexAxis: horizontal ? "y" : "x",
        plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true }, y: { beginAtZero: true } },
      }}
    />
  );
}

export function SerieTemporal({ dados }: { dados: { data: string; total: number; alto_critico: number }[] }) {
  const labels = dados.map((d) => d.data.slice(8, 10) + "/" + d.data.slice(5, 7));
  return (
    <Line
      data={{
        labels,
        datasets: [
          {
            label: "Total de eventos",
            data: dados.map((d) => d.total),
            borderColor: "#6366f1",
            backgroundColor: "#6366f122",
            fill: true,
            tension: 0.3,
          },
          {
            label: "Risco alto/crítico",
            data: dados.map((d) => d.alto_critico),
            borderColor: "#dc2626",
            backgroundColor: "#dc262622",
            fill: true,
            tension: 0.3,
          },
        ],
      }}
      options={{
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        scales: { y: { beginAtZero: true } },
      }}
    />
  );
}
