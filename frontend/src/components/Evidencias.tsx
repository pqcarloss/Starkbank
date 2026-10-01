export function Evidencias({ itens }: { itens: string[] }) {
  return (
    <ul className="list-disc space-y-0.5 pl-4 text-xs text-slate-600">
      {itens.map((e, i) => (
        <li key={i}>{e}</li>
      ))}
    </ul>
  );
}
