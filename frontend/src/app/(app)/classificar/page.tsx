"use client";

import { useEffect, useState } from "react";
import { Cabecalho, Erro } from "@/components/AppShell";
import { Badge } from "@/components/Badge";
import { Evidencias } from "@/components/Evidencias";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { Classificacao, Evento, Ferramenta } from "@/lib/types";

const EXEMPLOS = [
  "Resuma o comunicado público sobre o lançamento do novo app.",
  "Analise os clientes: 529.982.247-25 e 111.444.777-35, cartão 4111 1111 1111 1111.",
  "Corrija o erro:\napi_key = 'sk-live-123456789abc'\ndef main():\n    pass",
  "Prepare o resumo da due diligence para a aquisição da fintech Alfa (estritamente confidencial).",
];

export default function ClassificarPage() {
  const { pode } = useAuth();
  const [ferramentas, setFerramentas] = useState<Ferramenta[]>([]);
  const [texto, setTexto] = useState(EXEMPLOS[1]);
  const [ferramenta, setFerramenta] = useState("ChatGPT Enterprise");
  const [finalidade, setFinalidade] = useState("");
  const [idUsuario, setIdUsuario] = useState("");
  const [resultado, setResultado] = useState<Classificacao | null>(null);
  const [registrado, setRegistrado] = useState<Evento | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [carregando, setCarregando] = useState(false);

  useEffect(() => {
    api<Ferramenta[]>("/ferramentas").then(setFerramentas).catch(() => undefined);
  }, []);

  const corpo = () => ({ texto, ferramenta, finalidade: finalidade || null });

  async function analisar() {
    setErro(null);
    setRegistrado(null);
    setCarregando(true);
    try {
      setResultado(await api<Classificacao>("/classificar", { method: "POST", body: JSON.stringify(corpo()) }));
    } catch (e) {
      setErro((e as Error).message);
    } finally {
      setCarregando(false);
    }
  }

  async function registrar() {
    setErro(null);
    try {
      const ev = await api<Evento>("/eventos", {
        method: "POST",
        body: JSON.stringify({ ...corpo(), id_usuario: idUsuario }),
      });
      setRegistrado(ev);
    } catch (e) {
      setErro((e as Error).message);
    }
  }

  return (
    <>
      <Cabecalho
        titulo="Analisar conteúdo (DLP)"
        subtitulo="Classificação determinística por regras: detecção de dados sensíveis, sensibilidade e risco"
      />
      <Erro mensagem={erro} />
      <div className="grid gap-6 xl:grid-cols-2">
        <div className="card space-y-3">
          <label className="block text-sm">
            Conteúdo enviado à ferramenta de IA (prompt/arquivo)
            <textarea className="input mt-1 font-mono" rows={10} value={texto} onChange={(e) => setTexto(e.target.value)} />
          </label>
          <div className="flex flex-wrap gap-2">
            {EXEMPLOS.map((ex, i) => (
              <button key={i} className="btn-secondary text-xs" onClick={() => setTexto(ex)}>
                Exemplo {i + 1}
              </button>
            ))}
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            <label className="block text-sm">
              Ferramenta
              <input
                className="input mt-1"
                list="ferramentas"
                value={ferramenta}
                onChange={(e) => setFerramenta(e.target.value)}
              />
              <datalist id="ferramentas">
                {ferramentas.map((f) => (
                  <option key={f.id} value={f.nome} />
                ))}
              </datalist>
            </label>
            <label className="block text-sm">
              Finalidade declarada (opcional)
              <input className="input mt-1" value={finalidade} onChange={(e) => setFinalidade(e.target.value)} />
            </label>
          </div>
          <button className="btn" onClick={analisar} disabled={carregando || !texto || !ferramenta}>
            {carregando ? "Analisando…" : "Analisar (simulação)"}
          </button>
          {pode("admin", "analista") && (
            <div className="flex items-end gap-2 border-t border-slate-100 pt-3">
              <label className="block flex-1 text-sm">
                ID corporativo do usuário (será pseudonimizado)
                <input className="input mt-1" value={idUsuario} onChange={(e) => setIdUsuario(e.target.value)} />
              </label>
              <button className="btn-secondary" onClick={registrar} disabled={!idUsuario || !texto || !ferramenta}>
                Registrar evento
              </button>
            </div>
          )}
          {registrado && (
            <div className="rounded-lg bg-green-50 px-3 py-2 text-sm text-green-800">
              Evento {registrado.id} registrado para {registrado.id_usuario}
              {registrado.alerta ? ` · alerta #${registrado.alerta.id} aberto` : ""}.
            </div>
          )}
        </div>
        {resultado && (
          <div className="card space-y-4">
            <div className="grid grid-cols-3 gap-3 text-sm">
              <div>
                <div className="text-xs text-slate-500">Sensibilidade</div>
                <Badge valor={resultado.sensibilidade} />
              </div>
              <div>
                <div className="text-xs text-slate-500">Risco</div>
                <Badge valor={resultado.risco} />
              </div>
              <div>
                <div className="text-xs text-slate-500">Gera alerta?</div>
                <span className="font-semibold">{resultado.gera_alerta ? "Sim" : "Não"}</span>
              </div>
              <div className="col-span-2">
                <div className="text-xs text-slate-500">Tipo de informação</div>
                {resultado.tipo_informacao}
              </div>
              <div>
                <div className="text-xs text-slate-500">Finalidade</div>
                {resultado.finalidade}
              </div>
            </div>
            <table className="table">
              <thead>
                <tr>
                  <th>Regra</th>
                  <th>Tipo</th>
                  <th>Ocorrências</th>
                  <th>Amostras (mascaradas)</th>
                </tr>
              </thead>
              <tbody>
                {resultado.deteccoes.map((d) => (
                  <tr key={d.regra}>
                    <td>{d.regra}</td>
                    <td>{d.tipo_informacao}</td>
                    <td>{d.ocorrencias}</td>
                    <td className="font-mono text-xs">{d.amostras.join(", ")}</td>
                  </tr>
                ))}
                {resultado.deteccoes.length === 0 && (
                  <tr>
                    <td colSpan={4} className="text-slate-500">
                      Nenhum dado sensível detectado.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
            <div>
              <div className="mb-1 text-xs font-semibold text-slate-500">Evidências</div>
              <Evidencias itens={resultado.evidencias} />
            </div>
            <div className="text-xs text-slate-400">Classificador: {resultado.classificador}</div>
          </div>
        )}
      </div>
    </>
  );
}
