import json
import os
from datetime import datetime

class GeradorRelatorioAuditoria:
    """
    Módulo de Governança e Compliance (Pilar 4).
    Gera a Memória de Cálculo detalhada para o Banco Central e Auditoria Externa.
    """
    def __init__(self, arq_lcr='parametros_lcr.json', arq_curva='curva_di_b3_atual.json'):
        self.arq_lcr = arq_lcr
        self.arq_curva = arq_curva
        self.data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def _carregar_json(self, caminho):
        if not os.path.exists(caminho):
            return None
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)

    def gerar_memorial(self, prazo_taylor_made=118, arquivo_saida='Memorial_Auditoria_BACEN.txt'):
        print("🖨️ Compilando Memória de Cálculo Regulatório...")
        
        dados_lcr = self._carregar_json(self.arq_lcr)
        dados_curva = self._carregar_json(self.arq_curva)
        
        if not dados_lcr or not dados_curva:
            print("❌ Erro: Arquivos JSON base não encontrados. Rode os Pilares 1 e 2 primeiro.")
            return

        instituicao = dados_lcr.get('instituicao', 'Banco Desconhecido')
        
        with open(arquivo_saida, 'w', encoding='utf-8') as relatorio:
            # ==========================================
            # CABEÇALHO OFICIAL
            # ==========================================
            relatorio.write("======================================================================\n")
            relatorio.write("🏛️ MEMÓRIA DE CÁLCULO E TRILHA DE AUDITORIA (AUDIT TRAIL)\n")
            relatorio.write(f"Instituição Reportante: {instituicao}\n")
            relatorio.write(f"Data/Hora da Emissão: {self.data_geracao}\n")
            relatorio.write("Propósito: Comprovação Regulatória (Circular BACEN 3.749) e Precificação\n")
            relatorio.write("======================================================================\n\n")

            # ==========================================
            # SEÇÃO 1: RISCO DE LIQUIDEZ (LCR)
            # ==========================================
            relatorio.write("■ SEÇÃO I: CÁLCULO DO LCR (LIQUIDITY COVERAGE RATIO)\n")
            relatorio.write("-" * 70 + "\n")
            
            hqla = dados_lcr.get('hqla', 0)
            relatorio.write(f"1. Estoque HQLA (Ativos de Alta Liquidez): R$ {hqla:,.2f}\n\n".replace(",", "X").replace(".", ",").replace("X", "."))
            
            relatorio.write("2. Saídas de Caixa Estressadas (Outflows):\n")
            total_saidas = 0
            for item in dados_lcr.get('saidas_esperadas', []):
                saldo = item['saldo_total']
                taxa = item['taxa_fuga']
                ponderado = saldo * taxa
                total_saidas += ponderado
                relatorio.write(f"   -> {item['descricao']}:\n")
                relatorio.write(f"      Saldo Base: R$ {saldo:,.2f} | Fator de Estresse: {taxa*100:.1f}%\n".replace(",", "X").replace(".", ",").replace("X", "."))
                relatorio.write(f"      Saída Ponderada: R$ {ponderado:,.2f}\n".replace(",", "X").replace(".", ",").replace("X", "."))
            
            relatorio.write("\n3. Entradas de Caixa Estressadas (Inflows):\n")
            total_entradas = 0
            for item in dados_lcr.get('entradas_esperadas', []):
                saldo = item['saldo_total']
                taxa = item['taxa_recebimento']
                ponderado = saldo * taxa
                total_entradas += ponderado
                relatorio.write(f"   -> {item['descricao']}:\n")
                relatorio.write(f"      Saldo Base: R$ {saldo:,.2f} | Fator de Recebimento: {taxa*100:.1f}%\n".replace(",", "X").replace(".", ",").replace("X", "."))
                relatorio.write(f"      Entrada Ponderada: R$ {ponderado:,.2f}\n".replace(",", "X").replace(".", ",").replace("X", "."))

            # Regra do teto de 75%
            teto_entradas = total_saidas * 0.75
            entradas_validas = min(total_entradas, teto_entradas)
            saidas_liquidas = total_saidas - entradas_validas
            lcr_final = (hqla / saidas_liquidas) * 100 if saidas_liquidas > 0 else 0

            relatorio.write(f"\n4. Consolidação do Índice:\n")
            relatorio.write(f"   Total de Saídas Ponderadas: R$ {total_saidas:,.2f}\n".replace(",", "X").replace(".", ",").replace("X", "."))
            relatorio.write(f"   Entradas Elegíveis (Teto 75%): R$ {entradas_validas:,.2f}\n".replace(",", "X").replace(".", ",").replace("X", "."))
            relatorio.write(f"   Saídas Líquidas Estressadas: R$ {saidas_liquidas:,.2f}\n".replace(",", "X").replace(".", ",").replace("X", "."))
            relatorio.write(f"   >>> LCR REPORTADO: {lcr_final:.2f}%\n\n")

            # ==========================================
            # SEÇÃO 2: PRECIFICAÇÃO (CURVA DE JUROS)
            # ==========================================
            relatorio.write("■ SEÇÃO II: MEMÓRIA DE INTERPOLAÇÃO DE CURVA SPOT (TAYLOR-MADE)\n")
            relatorio.write("-" * 70 + "\n")
            relatorio.write(f"Fonte de Dados: {dados_curva.get('fonte')} ({dados_curva.get('data_extracao')})\n")
            relatorio.write(f"Prazo Alvo Solicitado: {prazo_taylor_made} Dias Úteis (DU)\n\n")

            vertices = sorted(dados_curva.get('vertices', []), key=lambda x: x['du'])
            v1, v2 = None, None
            
            # Encontra os vértices que "cercam" o prazo alvo
            for v in vertices:
                if v['du'] <= prazo_taylor_made:
                    v1 = v
                if v['du'] >= prazo_taylor_made and v2 is None:
                    v2 = v
                    break

            if v1 and v2 and v1['du'] != v2['du']:
                peso = (prazo_taylor_made - v1['du']) / (v2['du'] - v1['du'])
                taxa_final = v1['taxa_aa'] + peso * (v2['taxa_aa'] - v1['taxa_aa'])
                
                relatorio.write("Fórmula Aplicada: Interpolação Linear de 1º Grau\n")
                relatorio.write(f"Vértice Inferior (V1): {v1['du']} DU a {v1['taxa_aa']:.3f}%\n")
                relatorio.write(f"Vértice Superior (V2): {v2['du']} DU a {v2['taxa_aa']:.3f}%\n\n")
                
                relatorio.write("Passo a Passo Matemático:\n")
                relatorio.write(f"1. Fator de Tempo (Peso): ({prazo_taylor_made} - {v1['du']}) / ({v2['du']} - {v1['du']}) = {peso:.4f}\n")
                relatorio.write(f"2. Spread entre Vértices: {v2['taxa_aa']:.3f}% - {v1['taxa_aa']:.3f}% = {(v2['taxa_aa'] - v1['taxa_aa']):.3f}%\n")
                relatorio.write(f"3. Taxa Interpolada: {v1['taxa_aa']:.3f}% + ({peso:.4f} * {(v2['taxa_aa'] - v1['taxa_aa']):.3f}%)\n")
                relatorio.write(f"   >>> TAXA JUSTA DE PRECIFICAÇÃO: {taxa_final:.3f}% a.a.\n")
            else:
                relatorio.write("⚠️ Não foi possível encontrar vértices de contorno para a interpolação.\n")
                
            relatorio.write("\n======================================================================\n")
            relatorio.write("FIM DO RELATÓRIO\n")
            relatorio.write("Documento gerado automaticamente pelo Sistema ALM - Banco Alpha\n")
            relatorio.write("Assinatura Digital (Hash): Requisito não implementado na v1.0\n")
            relatorio.write("======================================================================")

        print(f"✅ Memorial Regulatório gerado com sucesso! Arquivo: {arquivo_saida}")

if __name__ == "__main__":
    gerador = GeradorRelatorioAuditoria()
    gerador.gerar_memorial()