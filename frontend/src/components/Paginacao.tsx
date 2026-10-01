export function Paginacao({
  pagina,
  tamanho,
  total,
  onChange,
}: {
  pagina: number;
  tamanho: number;
  total: number;
  onChange: (p: number) => void;
}) {
  const ultima = Math.max(1, Math.ceil(total / tamanho));
  return (
    <div className="mt-4 flex items-center justify-between text-sm text-slate-600">
      <span>
        {total} registro(s) · página {pagina} de {ultima}
      </span>
      <div className="space-x-2">
        <button className="btn-secondary" disabled={pagina <= 1} onClick={() => onChange(pagina - 1)}>
          Anterior
        </button>
        <button className="btn-secondary" disabled={pagina >= ultima} onClick={() => onChange(pagina + 1)}>
          Próxima
        </button>
      </div>
    </div>
  );
}
