// Reforça visualmente (além do CSS já aplicado no server) quais insumos
// estão com estoque baixo, consultando a API em tempo real.
fetch("/api/estoque-baixo")
    .then((res) => res.json())
    .then((insumos) => {
        insumos.forEach((insumo) => {
            const linha = document.getElementById(`insumo-${insumo.id}`);
            if (!linha) return;
            if (insumo.estoque_baixo) {
                linha.classList.add("alerta");
                linha.setAttribute("aria-label", `${insumo.nome}: estoque abaixo do mínimo`);
            } else {
                linha.classList.remove("alerta");
            }
        });
    });
