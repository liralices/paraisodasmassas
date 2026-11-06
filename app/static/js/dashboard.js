// Gráfico: produtos mais vendidos
fetch("/api/produto-mais-vendido")
    .then((res) => res.json())
    .then((dados) => {
        const ctx = document.getElementById("grafico-mais-vendidos");
        if (!dados.length) {
            ctx.replaceWith(criarMensagemVazia("Ainda não há vendas registradas."));
            return;
        }
        new Chart(ctx, {
            type: "bar",
            data: {
                labels: dados.map((d) => d.produto),
                datasets: [{ label: "Unidades vendidas", data: dados.map((d) => d.quantidade) }],
            },
            options: { responsive: true, plugins: { legend: { display: false } } },
        });
    });

// Gráfico: faturamento por dia
fetch("/api/faturamento-por-dia")
    .then((res) => res.json())
    .then((dados) => {
        const ctx = document.getElementById("grafico-faturamento");
        if (!dados.length) {
            ctx.replaceWith(criarMensagemVazia("Ainda não há faturamento registrado."));
            return;
        }
        new Chart(ctx, {
            type: "line",
            data: {
                labels: dados.map((d) => d.dia),
                datasets: [{ label: "Faturamento (R$)", data: dados.map((d) => d.faturamento) }],
            },
            options: { responsive: true },
        });
    });

// Lista de alertas de estoque baixo
fetch("/api/estoque-baixo")
    .then((res) => res.json())
    .then((insumos) => {
        const lista = document.getElementById("lista-alertas-estoque");
        const comAlerta = insumos.filter((i) => i.estoque_baixo);

        if (!comAlerta.length) {
            const item = document.createElement("li");
            item.textContent = "Nenhum insumo abaixo do mínimo no momento.";
            lista.appendChild(item);
            return;
        }

        comAlerta.forEach((i) => {
            const item = document.createElement("li");
            item.textContent = `${i.nome}: ${i.quantidade_atual}${i.unidade} (mínimo: ${i.quantidade_minima}${i.unidade})`;
            lista.appendChild(item);
        });
    });

function criarMensagemVazia(texto) {
    const p = document.createElement("p");
    p.textContent = texto;
    return p;
}
