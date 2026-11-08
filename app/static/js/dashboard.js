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

// Lista exclusiva de alertas de estoque
fetch("/api/estoque-baixo")
    .then((res) => res.json())
    .then((alertas) => {
        const lista = document.getElementById("lista-alertas-estoque");

        if (!alertas.length) {
            const item = document.createElement("li");
            item.className = "alerta-vazio";
            item.textContent = "Nenhum item em alerta de compra no momento.";
            lista.appendChild(item);
            return;
        }

        alertas.forEach((alerta) => {
            const item = document.createElement("li");
            item.className = "alerta-item";

            const label = document.createElement("strong");
            label.textContent = `${alerta.tipo}: ${alerta.nome}`;

            const meta = document.createElement("span");
            meta.textContent = `${alerta.quantidade_atual} ${alerta.unidade} / mínimo ${alerta.quantidade_minima} ${alerta.unidade}`;

            const fornecedor = document.createElement("small");
            fornecedor.textContent = `Fornecedor: ${alerta.fornecedor}`;

            const detalhe = document.createElement("small");
            detalhe.textContent = `Obs.: ${alerta.observacao}`;

            if (alerta.dado_faltante) {
                item.classList.add("alerta-falta-dado");
            }

            item.appendChild(label);
            item.appendChild(meta);
            item.appendChild(fornecedor);
            item.appendChild(detalhe);
            lista.appendChild(item);
        });
    });

function criarMensagemVazia(texto) {
    const p = document.createElement("p");
    p.textContent = texto;
    return p;
}
