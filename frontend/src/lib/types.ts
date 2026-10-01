export type Sensibilidade = "Pública" | "Interna" | "Confidencial" | "Crítica";
export type Risco = "Baixo" | "Médio" | "Alto" | "Crítico";
export type StatusAlerta = "Aberto" | "Em análise" | "Tratado";
export type StatusFerramenta = "Aprovada" | "Aprovada condicional" | "Não aprovada";
export type Papel = "admin" | "analista" | "leitor";

export const SENSIBILIDADES: Sensibilidade[] = ["Pública", "Interna", "Confidencial", "Crítica"];
export const RISCOS: Risco[] = ["Baixo", "Médio", "Alto", "Crítico"];
export const STATUS_ALERTA: StatusAlerta[] = ["Aberto", "Em análise", "Tratado"];
export const STATUS_FERRAMENTA: StatusFerramenta[] = ["Aprovada", "Aprovada condicional", "Não aprovada"];

export interface Usuario {
  id: number;
  email: string;
  nome: string;
  papel: Papel;
  ativo: boolean;
  provedor_auth: string;
}

export interface Ferramenta {
  id: number;
  nome: string;
  fornecedor: string;
  status: StatusFerramenta;
  observacoes: string;
}

export interface TipoInformacao {
  id: number;
  nome: string;
  descricao: string;
  classificacao_padrao: Sensibilidade;
}

export interface Evento {
  id: string;
  id_usuario: string;
  ferramenta_nome: string;
  tipo_informacao: string;
  tipos_detectados: string[];
  sensibilidade: Sensibilidade;
  finalidade: string;
  risco: Risco;
  evidencias: string[];
  classificador: string;
  conteudo_tamanho: number;
  data_hora: string;
  alerta: { id: number; status: StatusAlerta; severidade: Risco } | null;
}

export interface Alerta {
  id: number;
  evento_id: string;
  severidade: Risco;
  status: StatusAlerta;
  responsavel: string | null;
  observacao: string;
  criado_em: string;
  atualizado_em: string;
  evento: Evento;
}

export interface Pagina<T> {
  total: number;
  pagina: number;
  tamanho: number;
  itens: T[];
}

export interface Deteccao {
  regra: string;
  tipo_informacao: string;
  ocorrencias: number;
  amostras: string[];
}

export interface Classificacao {
  tipo_informacao: string;
  tipos_detectados: string[];
  sensibilidade: Sensibilidade;
  finalidade: string;
  risco: Risco;
  gera_alerta: boolean;
  evidencias: string[];
  deteccoes: Deteccao[];
  classificador: string;
}

export interface CasoValidacao {
  id: number;
  descricao: string;
  ferramenta_nome: string;
  texto_entrada: string;
  sensibilidade_esperada: Sensibilidade;
  risco_esperado: Risco;
}

export interface ExecucaoValidacao {
  total: number;
  aprovados: number;
  taxa_acerto: number;
  resultados: {
    caso: CasoValidacao;
    sensibilidade_obtida: Sensibilidade;
    risco_obtido: Risco;
    aprovado: boolean;
    evidencias: string[];
  }[];
}

export interface Contagem {
  rotulo: string;
  total: number;
}

export interface DashboardResumo {
  total_eventos: number;
  alertas_abertos: number;
  eventos_alto_critico: number;
  usuarios_distintos: number;
  eventos_ferramentas_nao_aprovadas: number;
  por_risco: Contagem[];
  por_sensibilidade: Contagem[];
  por_ferramenta: Contagem[];
  por_tipo_informacao: Contagem[];
  alertas_por_status: Contagem[];
  serie_diaria: { data: string; total: number; alto_critico: number }[];
}
