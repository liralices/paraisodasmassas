(function () {
    const modal = document.getElementById("modal-nova-venda");
    const btnAbrir = document.getElementById("btn-nova-venda");
    const btnFechar = document.getElementById("btn-fechar-modal");
    const btnCancelar = document.getElementById("btn-cancelar-venda");
    const btnAddItem = document.getElementById("btn-add-item");
    const corpoItens = document.getElementById("corpo-itens-venda");
    const totalValor = document.getElementById("total-venda-valor");
    const formaPagamento = document.getElementById("forma_pagamento");
    const valorRecebido = document.getElementById("valor_recebido");
    const trocoInput = document.getElementById("troco");
    const trocoExibicao = document.getElementById("troco_exibicao");
    const form = document.getElementById("form-nova-venda");

    if (!modal) return;

    function formatarMoeda(valor) {
        return "R$ " + valor.toFixed(2).replace(".", ",");
    }

    function atualizarTroco() {
        const total = Array.from(corpoItens.querySelectorAll("tr")).reduce((soma, linha) => {
            const select = linha.querySelector("select[name='produto_id[]']");
            const quantidadeInput = linha.querySelector("input[name='quantidade[]']");
            const produto = PRODUTOS_VENDA.find((p) => p.id === Number(select.value));
            const quantidade = Number(quantidadeInput.value) || 0;
            return soma + (produto ? produto.preco * quantidade : 0);
        }, 0);

        const metodo = formaPagamento ? formaPagamento.value : "Dinheiro";
        if (metodo !== "Dinheiro") {
            trocoInput.value = "0";
            trocoExibicao.value = "R$ 0,00";
            if (valorRecebido) valorRecebido.disabled = true;
            return;
        }

        if (valorRecebido) valorRecebido.disabled = false;
        const recebido = Number(valorRecebido ? valorRecebido.value : 0) || 0;
        const troco = Math.max(recebido - total, 0);
        trocoInput.value = troco.toFixed(2);
        trocoExibicao.value = formatarMoeda(troco);
    }

    function recalcularTotal() {
        let total = 0;
        corpoItens.querySelectorAll("tr").forEach((linha) => {
            const select = linha.querySelector("select[name='produto_id[]']");
            const quantidadeInput = linha.querySelector("input[name='quantidade[]']");
            const produto = PRODUTOS_VENDA.find((p) => p.id === Number(select.value));
            const quantidade = Number(quantidadeInput.value) || 0;
            const subtotal = produto ? produto.preco * quantidade : 0;
            linha.querySelector(".subtotal-item").textContent = formatarMoeda(subtotal);
            total += subtotal;
        });
        totalValor.textContent = formatarMoeda(total);
        atualizarTroco();
    }

    function criarLinhaItem() {
        const linha = document.createElement("tr");

        const tdProduto = document.createElement("td");
        const select = document.createElement("select");
        select.name = "produto_id[]";
        select.required = true;
        const optVazia = document.createElement("option");
        optVazia.value = "";
        optVazia.textContent = "Selecione um produto";
        select.appendChild(optVazia);
        PRODUTOS_VENDA.forEach((p) => {
            const opt = document.createElement("option");
            opt.value = p.id;
            opt.textContent = p.nome + " — " + formatarMoeda(p.preco);
            select.appendChild(opt);
        });
        select.addEventListener("change", recalcularTotal);
        tdProduto.appendChild(select);

        const tdQuantidade = document.createElement("td");
        const inputQuantidade = document.createElement("input");
        inputQuantidade.type = "number";
        inputQuantidade.name = "quantidade[]";
        inputQuantidade.min = "1";
        inputQuantidade.value = "1";
        inputQuantidade.required = true;
        inputQuantidade.addEventListener("input", recalcularTotal);
        tdQuantidade.appendChild(inputQuantidade);

        const tdSubtotal = document.createElement("td");
        tdSubtotal.className = "subtotal-item";
        tdSubtotal.textContent = formatarMoeda(0);

        const tdRemover = document.createElement("td");
        const btnRemover = document.createElement("button");
        btnRemover.type = "button";
        btnRemover.className = "botao-secundario botao-remover-item";
        btnRemover.textContent = "Remover";
        btnRemover.addEventListener("click", () => {
            linha.remove();
            if (!corpoItens.querySelector("tr")) criarLinhaItem();
            recalcularTotal();
        });
        tdRemover.appendChild(btnRemover);

        linha.append(tdProduto, tdQuantidade, tdSubtotal, tdRemover);
        corpoItens.appendChild(linha);
        recalcularTotal();
    }

    function abrirModal() {
        corpoItens.innerHTML = "";
        if (formaPagamento) formaPagamento.value = "Dinheiro";
        if (valorRecebido) {
            valorRecebido.value = "";
            valorRecebido.disabled = false;
        }
        if (trocoInput) trocoInput.value = "0";
        if (trocoExibicao) trocoExibicao.value = "R$ 0,00";
        criarLinhaItem();
        modal.showModal();
    }

    function fecharModal() {
        modal.close();
    }

    btnAbrir.addEventListener("click", abrirModal);
    btnFechar.addEventListener("click", fecharModal);
    btnCancelar.addEventListener("click", fecharModal);
    btnAddItem.addEventListener("click", criarLinhaItem);

    if (formaPagamento) {
        formaPagamento.addEventListener("change", atualizarTroco);
    }
    if (valorRecebido) {
        valorRecebido.addEventListener("input", atualizarTroco);
    }

    form.addEventListener("submit", (event) => {
        const linhasValidas = Array.from(corpoItens.querySelectorAll("tr")).filter((linha) => {
            return linha.querySelector("select[name='produto_id[]']").value !== "";
        });
        if (!linhasValidas.length) {
            event.preventDefault();
            alert("Adicione ao menos um item à venda.");
        }
    });
})();
