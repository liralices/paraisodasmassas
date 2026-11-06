# Giro

Sistema web de gestão diária para a padaria **Paraíso das Massas** — vendas,
estoque de insumos, ficha técnica, fechamento de caixa e um dashboard de
indicadores.

Projeto Integrador em Computação II (PJI240) — Univesp.

## Identidade visual

O design foi construído a partir do logo da Paraíso das Massas:

- **Cores**: café escuro `#3D2314` (sidebar), marrom `#6E3B1C` (marca), dourado
  trigo `#E3BD7D` (destaques), creme `#FBF4E8` (fundo). O anel gradiente do
  logo (rosa → laranja → amarelo → roxo) aparece só em dois lugares: o item de
  menu ativo e o botão primário — um acento raro, não decoração espalhada.
- **Tipografia**: Fraunces (serif, títulos) + Work Sans (sans-serif, dados e
  tabelas).
- **Layout**: sidebar fixa com navegação, inspirada na estrutura de sistemas
  de gestão como o Hiper, usada como referência de usabilidade para o
  segmento de padaria.

## Funcionalidades — mapeadas a partir do sistema Hiper para padarias

Como parte do levantamento bibliográfico, o site
[hiper.com.br/solucoes-para-voce/padaria](https://hiper.com.br/solucoes-para-voce/padaria/)
foi usado como referência de mercado. Da lista de funcionalidades da Hiper,
o que entrou no escopo do Giro:

| Funcionalidade (Hiper) | No Giro | Status |
|---|---|---|
| Gestão de Vendas | Registro de vendas por produto | ✅ Implementado |
| Cadastro de clientes | Tela de Clientes (nome, telefone, localidade, CPF/CNPJ) | ✅ Implementado |
| Gestão de Estoque | Controle de insumos com alerta de estoque mínimo | ✅ Implementado |
| Ficha técnica | Vínculo insumo × produto (quanto cada produto consome) | ✅ Implementado |
| Financeiro / Raio-X | Fechamento de caixa (abertura, vendas do período, valor esperado × contado) | ✅ Implementado |
| Relatórios Hiper | Dashboard com produto mais vendido, faturamento por dia e alertas | ✅ Implementado |
| Fiscal (NF-e/cupom fiscal) | — | ⏸️ Fora de escopo — exige homologação e certificado digital reais |
| Meios de pagamento (maquininha) | — | ⏸️ Fora de escopo — exige integração com adquirente real |
| Balança integrada | — | ⏸️ Fora de escopo — depende de hardware específico |
| Loja online / Catálogo digital | — | ⏸️ Fora de escopo — não é o problema identificado na visita |

## Requisitos da ementa atendidos

- Framework web: Flask
- Banco de dados: SQLite (via SQLAlchemy)
- Script web: JavaScript (Chart.js + fetch para a API)
- API: endpoints REST em `/api/...`
- Acessibilidade: labels, `aria-live`, captions ocultas, foco visível, navegação por teclado
- Controle de versão: Git/GitHub
- Testes: pytest (`tests/test_models.py`) — 8 testes cobrindo vendas, estoque, caixa e ficha técnica
- Análise de dados (opcional): dashboard com produto mais vendido e faturamento por dia
- Nuvem: pendente de deploy (ver "Próximos passos")

## Como rodar localmente

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Acesse http://localhost:5000

## Como rodar os testes

```bash
pytest
```

## Estrutura

```
app/
├── __init__.py            # app factory, registra os blueprints
├── models.py               # Produto, Venda, Insumo, Cliente, FichaTecnica, FechamentoCaixa
├── routes/
│   ├── vendas.py            # CRUD de produtos + registro de vendas
│   ├── estoque.py            # CRUD de insumos
│   ├── clientes.py            # CRUD de clientes
│   ├── ficha_tecnica.py        # vínculo produto × insumo
│   ├── caixa.py                 # abertura/fechamento de caixa
│   └── api.py                    # endpoints JSON consumidos pelo dashboard
├── templates/
│   ├── base.html            # shell com sidebar
│   ├── _icons.html           # ícones SVG reutilizáveis (inclui a espiga de trigo)
│   └── ...                    # uma página por funcionalidade
└── static/
    ├── css/style.css        # sistema de design (tokens, componentes)
    └── js/                    # dashboard.js, estoque.js
tests/
run.py
```

## Próximos passos

- [ ] Deploy no Azure App Service
- [ ] Popular com dados reais da Paraíso das Massas
- [ ] Validar acessibilidade com leitor de tela
