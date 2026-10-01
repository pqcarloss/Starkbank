import { COR_RISCO, COR_SENSIBILIDADE, COR_STATUS_ALERTA, COR_STATUS_FERRAMENTA } from "@/lib/cores";

const TODAS: Record<string, string> = {
  ...COR_RISCO,
  ...COR_SENSIBILIDADE,
  ...COR_STATUS_ALERTA,
  ...COR_STATUS_FERRAMENTA,
};

export function Badge({ valor }: { valor: string }) {
  const cor = TODAS[valor] ?? "#64748b";
  return (
    <span
      className="inline-block whitespace-nowrap rounded-full px-2 py-0.5 text-xs font-semibold"
      style={{ color: cor, backgroundColor: `${cor}1a`, border: `1px solid ${cor}55` }}
    >
      {valor}
    </span>
  );
}
