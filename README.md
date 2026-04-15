# Projeto #1: Motor Quantitativo de Gestão de Tesouraria (ALM) 🚀

**Laboratório Público de Engenharia Financeira**

Este repositório contém a arquitetura e os algoritmos desenvolvidos para resolver o clássico dilema de *Asset Liability Management* (ALM) em tesourarias institucionais: maximizar a rentabilidade do *spread* sem asfixiar o capital regulatório e respeitando rigorosos limites de risco de liquidez.

## 📌 A Tese (O Problema)
A tesouraria atua como o "coração" na precificação dos produtos da instituição (*transfer pricing*). Modelos tradicionais baseados em alocações estáticas geram alto custo de oportunidade e expõem a instituição a riscos de descasamento de prazos. Nosso motor busca otimizar essa alocação dinamicamente, unindo o rigor acadêmico (FIPECAFI) com automação em Python.

## ⚙️ Arquitetura do Motor (A Solução)
A metodologia deste projeto é baseada no padrão CRISP-DM e dividida em três pilares principais:

### Pilar 1: Pipeline de Ingestão de Dados (PDF para JSON)
Algoritmo desenvolvido com a biblioteca `PyMuPDF` para transformar relatórios, regulamentos e políticas de tesouraria em texto estruturado e indexável, servindo como banco de dados NoSQL (JSON) para consumo de inteligência artificial.

### Pilar 2: Construtor da Curva a Termo (Curva Spot/Forward B3)
Motor matemático que utiliza a técnica de **Spline Cúbica** (`scipy.interpolate`) para capturar vértices de DI Futuro da B3 e construir uma curva de juros contínua. Isso permite a precificação exata de derivativos e o cálculo de *duration* em datas fracionadas.

### Pilar 3: Calculadora de Risco de Liquidez (LCR - Basileia)
Modelo que aplica simulações de estresse no fluxo de caixa (corrida bancária) para otimizar o *Liquidity Coverage Ratio* (LCR), garantindo matematicamente que o estoque de Ativos de Alta Liquidez (HQLA) seja suficiente para cenários de 30 dias.

## 🛠️ Stack Tecnológico
* **Linguagem:** Python 3.10+
* **Processamento de Documentos:** `PyMuPDF`
* **Computação Científica:** `numpy`, `scipy`
* **Manipulação de Dados:** `pandas`
* **Visualização:** `matplotlib`
* **Armazenamento de Metadados:** JSON (NoSQL)

## 📄 Licença
Este projeto faz parte de um laboratório público de pesquisa em Engenharia Financeira. (Sinta-se à vontade para clonar, estudar e contribuir).
