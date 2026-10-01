import type { Risco, Sensibilidade, StatusAlerta, StatusFerramenta } from "@/lib/types";

export const COR_RISCO: Record<Risco, string> = {
  Baixo: "#22c55e",
  Médio: "#eab308",
  Alto: "#f97316",
  Crítico: "#dc2626",
};

export const COR_SENSIBILIDADE: Record<Sensibilidade, string> = {
  Pública: "#38bdf8",
  Interna: "#6366f1",
  Confidencial: "#a855f7",
  Crítica: "#be123c",
};

export const COR_STATUS_ALERTA: Record<StatusAlerta, string> = {
  Aberto: "#dc2626",
  "Em análise": "#f59e0b",
  Tratado: "#16a34a",
};

export const COR_STATUS_FERRAMENTA: Record<StatusFerramenta, string> = {
  Aprovada: "#16a34a",
  "Aprovada condicional": "#f59e0b",
  "Não aprovada": "#dc2626",
};

export const PALETA = ["#6366f1", "#06b6d4", "#22c55e", "#eab308", "#f97316", "#ef4444", "#a855f7", "#ec4899", "#14b8a6", "#64748b"];
