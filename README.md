# 🏛️ Laboratório de Engenharia Financeira: Motor ALM Quantitativo

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Status](https://img.shields.io/badge/Status-Produção_Simulada-success)
![Mercado](https://img.shields.io/badge/Mercado-ALM%20%7C%20Tesouraria-orange)

Este repositório contém o **Projeto #1** do meu portfólio de Engenharia Financeira: um ecossistema quantitativo em Python projetado para automatizar a Gestão de Ativos e Passivos (ALM), calcular o Risco de Liquidez (LCR - Basileia III) e precificar derivativos *Taylor-Made* utilizando a Curva Spot de Juros.

## 🏗️ Arquitetura do Sistema (Os 4 Pilares)

O sistema foi desenhado com base em arquitetura desacoplada e alta Tolerância a Falhas (*Fault Tolerance*):

1. **Ingestor de Regras (PDF ➡️ JSON):** Extrai normativos do Banco Central e os converte em parâmetros dinâmicos. O código Python nunca é alterado em caso de mudança regulatória.
2. **Motor de Curva de Juros (ETTJ):** Robôs de *Web Scraping* blindados extraem as taxas do DI Futuro ao vivo (B3/InfoMoney). O cálculo numérico de Interpolação Linear gera a curva contínua.
3. **Calculadora LCR (Basileia III):** Algoritmo de estresse de caixa que cruza o balanço da instituição com as regras de *Run-off* do BACEN.
4. **Governança (Audit Trail):** Módulo gerador de relatórios formais em `.txt` para comprovação de Memória de Cálculo perante auditorias.

## 💼 Casos de Uso Executados

### 🔴 Caso 1: Risco de Liquidez Institucional
Processamento do Balanço Simulativo (Banco Alpha - Case FIPECAFI):
* **HQLA:** R$ 165.2 Bilhões
* **Resultado:** O motor identificou um estrangulamento de caixa de Atacado, cravando o **LCR em 83.83%** (Abaixo do mínimo de 100%), emitindo um alerta regulatório de rebalanceamento.

### 🟢 Caso 2: Precificação Taylor-Made (OTC)
Demanda de mesa para precificar uma captação em prazo "cego" de bolsa: exatos **118 Dias Úteis**.
* **Mecânica:** O motor ingere 41 vértices ativos, localiza os nós de contorno (97 DU e 120 DU) e aplica a fórmula de Interpolação Linear.
* **Preço Justo:** O algoritmo cravou a taxa em **14.149% a.a.**, permitindo agilidade no fechamento de *spread*.

## 🚀 Como Executar

Clone o repositório e instale as dependências:
```bash
pip install pandas numpy scipy matplotlib requests pyperclip
