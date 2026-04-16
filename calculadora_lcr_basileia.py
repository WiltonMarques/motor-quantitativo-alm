import pandas as pd
import json
import os

class CalculadoraLCR:
    """
    Motor Quantitativo de Liquidity Coverage Ratio (LCR) - Padrão Basileia III.
    Alimentado dinamicamente via banco de dados JSON.
    """
    def __init__(self, nome_instituicao="Instituição Padrão"):
        self.nome_instituicao = nome_instituicao
        self.hqla = 0.0 
        self.saidas_caixa = [] 
        self.entradas_caixa = [] 
        
    def carregar_ativos_liquidos(self, valor_hqla):
        self.hqla = valor_hqla
        
    def adicionar_saida_potencial(self, descricao, saldo_total, taxa_fuga_estresse):
        saida_ponderada = saldo_total * taxa_fuga_estresse
        self.saidas_caixa.append({
            'Descricao': descricao,
            'Saldo_Original': saldo_total,
            'Taxa_Estresse': taxa_fuga_estresse,
            'Saida_Ponderada': saida_ponderada
        })
        
    def adicionar_entrada_potencial(self, descricao, saldo_total, taxa_recebimento_estresse):
        entrada_ponderada = saldo_total * taxa_recebimento_estresse
        self.entradas_caixa.append({
            'Descricao': descricao,
            'Saldo_Original': saldo_total,
            'Taxa_Estresse': taxa_recebimento_estresse,
            'Entrada_Ponderada': entrada_ponderada
        })

    def calcular_lcr(self):
        """Calcula o LCR com base na trava de 75% para entradas (Basileia)"""
        df_saidas = pd.DataFrame(self.saidas_caixa)
        df_entradas = pd.DataFrame(self.entradas_caixa)
        
        total_saidas_ponderadas = df_saidas['Saida_Ponderada'].sum() if not df_saidas.empty else 0
        total_entradas_ponderadas = df_entradas['Entrada_Ponderada'].sum() if not df_entradas.empty else 0
        
        entradas_elegiveis = min(total_entradas_ponderadas, 0.75 * total_saidas_ponderadas)
        saidas_liquidas_estresse = total_saidas_ponderadas - entradas_elegiveis
        
        if saidas_liquidas_estresse <= 0:
            lcr_percentual = float('inf') 
        else:
            lcr_percentual = (self.hqla / saidas_liquidas_estresse) * 100
            
        status = "✅ CONFORME (Saudável)" if lcr_percentual >= 100 else "❌ ALERTA: RISCO REGULATÓRIO (Abaixo de 100%)"

        print(f"==================================================")
        print(f"🏛️ RELATÓRIO DE ESTRESSE DE LIQUIDEZ (LCR) - 30 DIAS")
        print(f"Instituição: {self.nome_instituicao}")
        print(f"==================================================")
        print(f"💰 1. Ativos de Alta Liquidez (HQLA): R$ {self.hqla:,.2f}")
        print(f"💸 2. Saídas Potenciais Ponderadas:   R$ {total_saidas_ponderadas:,.2f}")
        print(f"📥 3. Entradas Elegíveis Ponderadas:  R$ {entradas_elegiveis:,.2f}")
        print(f"🩸 4. Saídas Líquidas Estressadas:    R$ {saidas_liquidas_estresse:,.2f}")
        print(f"--------------------------------------------------")
        print(f"📊 ÍNDICE LCR FINAL: {lcr_percentual:.2f}%")
        print(f"🚦 STATUS: {status}")
        print(f"==================================================\n")
        
        return lcr_percentual

def orquestrar_motor(caminho_json):
    """Lê o banco de dados JSON e alimenta a classe da Calculadora"""
    if not os.path.exists(caminho_json):
        print(f"❌ Erro: Arquivo banco de dados '{caminho_json}' não encontrado.")
        return

    print("🔍 Lendo banco de dados JSON...")
    with open(caminho_json, 'r', encoding='utf-8') as arquivo:
        dados = json.load(arquivo)

    # 1. Inicializa o motor com o nome do banco
    motor = CalculadoraLCR(nome_instituicao=dados['instituicao'])
    
    # 2. Carrega o HQLA
    motor.carregar_ativos_liquidos(dados['hqla'])
    
    # 3. Carrega dinamicamente as saídas de caixa
    for saida in dados['saidas_esperadas']:
        motor.adicionar_saida_potencial(
            descricao=saida['descricao'], 
            saldo_total=saida['saldo_total'], 
            taxa_fuga_estresse=saida['taxa_fuga']
        )
        
    # 4. Carrega dinamicamente as entradas de caixa
    for entrada in dados['entradas_esperadas']:
        motor.adicionar_entrada_potencial(
            descricao=entrada['descricao'], 
            saldo_total=entrada['saldo_total'], 
            taxa_recebimento_estresse=entrada['taxa_recebimento']
        )
        
    print("⚙️ Dados ingeridos com sucesso. Rodando simulação...\n")
    # 5. Executa a simulação
    motor.calcular_lcr()


# ==========================================
# EXECUÇÃO DO SCRIPT
# ==========================================
if __name__ == "__main__":
    ARQUIVO_BANCO_DADOS = 'parametros_lcr.json'
    orquestrar_motor(ARQUIVO_BANCO_DADOS)