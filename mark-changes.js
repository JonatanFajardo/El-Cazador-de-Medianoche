/**
 * mark-changes.js
 * Colorea párrafos según su posición relativa de fecha (más reciente = color más llamativo).
 * El color indica CUÁNDO fue editado en relación a los demás cambios.
 * El estilo del borde indica QUÉ tipo de cambio fue:
 *   solid  → nuevo
 *   dashed → modificado
 *
 * Ranking de colores:
 *   1er más reciente  → verde   #22c55e
 *   2do más reciente  → cian    #06b6d4
 *   3er más reciente  → dorado  #eab308
 *   4to+ (resto)      → gris    #94a3b8
 */
(function () {
  const COLORES_RANKING = [
    "#22c55e", // 1ro — verde
    "#06b6d4", // 2do — cian
    "#eab308", // 3ro — dorado
  ];
  const COLOR_RESTO = "#94a3b8"; // 4to+ — gris

  // Recolectar elementos con data-updated (excluir "original")
  const elementos = Array.from(document.querySelectorAll("[data-updated]")).filter(function (el) {
    const status = el.getAttribute("data-status");
    return status === "new" || status === "modified";
  });

  if (elementos.length === 0) return;

  // Agrupar por fecha única y ordenar de más reciente a más antiguo
  const grupos = {};
  elementos.forEach(function (el) {
    const ts = new Date(el.getAttribute("data-updated")).getTime();
    if (!grupos[ts]) grupos[ts] = [];
    grupos[ts].push(el);
  });

  const fechasOrdenadas = Object.keys(grupos)
    .map(Number)
    .sort(function (a, b) { return b - a; }); // más reciente primero

  // Asignar color por posición en el ranking
  fechasOrdenadas.forEach(function (ts, idx) {
    const color = idx < COLORES_RANKING.length ? COLORES_RANKING[idx] : COLOR_RESTO;

    grupos[ts].forEach(function (el) {
      const status = el.getAttribute("data-status");
      const estilo  = status === "new" ? "solid" : "dashed";
      const label   = status === "new" ? "Nuevo" : "Modificado";
      const pos     = idx + 1;

      el.style.borderLeft = `3px ${estilo} ${color}`;
      el.style.paddingLeft = "8px";

      const fechaStr = new Date(ts).toLocaleString("es-ES", {
        day: "2-digit", month: "short",
        hour: "2-digit", minute: "2-digit", second: "2-digit"
      });
      el.title = `${label} · #${pos} más reciente · ${fechaStr}`;
    });
  });
})();
