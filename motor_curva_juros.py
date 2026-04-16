import pandas as pd
import numpy as np
import json
import os
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

class ConstrutorCurvaJuros:
    """
    Motor Matemático Quantitativo para precificação de Juros.
    Utiliza interpolação Linear para evitar Efeito Runge em curvas densas.
    """
    def __init__(self, caminho_json='curva_di_b3_atual.json'):
        self.caminho_json = caminho_json
        self.dados_vertices = None
        self.curva_matematica = None
        self.nome_curva = "Curva Desconhecida"
        
        self._carregar_dados()
        self._construir_curva()

    def _carregar_dados(self):
        if not os.path.exists(self.caminho_json):
            raise FileNotFoundError(f"Arquivo não encontrado: {self.caminho_json}")
        
        with open(self.caminho_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            self.nome_curva = dados.get('nome_curva', 'Curva DI Futuro')
            self.dados_vertices = pd.DataFrame(dados['vertices'])
            
            # Ordenação fundamental
            self.dados_vertices = self.dados_vertices.sort_values(by='du')
            
            # 🛡️ TRAVA DE SEGURANÇA: Se o robô salvou 10450 em vez de 10.45, divide por 1000.
            if self.dados_vertices['taxa_aa'].mean() > 100:
                print("⚠️ Aviso: As taxas vieram sem vírgula decimal do InfoMoney. Ajustando a escala automaticamente (/1000)...")
                self.dados_vertices['taxa_aa'] = self.dados_vertices['taxa_aa'] / 1000

    def _construir_curva(self):
        """Aplica Interpolação Linear para evitar oscilações em 41+ pontos."""
        x = self.dados_vertices['du'].values
        y = self.dados_vertices['taxa_aa'].values
        
        # Substituímos 'cubic' por 'linear' (Padrão ouro para curvas densas da B3)
        self.curva_matematica = interp1d(x, y, kind='linear', fill_value="extrapolate")

    def obter_taxa_para_prazo(self, du):
        if du < 0:
            raise ValueError("Prazo não pode ser negativo.")
        taxa = float(self.curva_matematica(du))
        return round(taxa, 4)

    def plotar_curva(self):
        print("📈 Renderizando o gráfico corrigido...")
        du_min, du_max = self.dados_vertices['du'].min(), self.dados_vertices['du'].max()
        
        prazos_simulados = np.linspace(du_min, du_max, 1000)
        taxas_simuladas = self.curva_matematica(prazos_simulados)

        plt.figure(figsize=(12, 6))
        plt.plot(prazos_simulados, taxas_simuladas, color='#1f77b4', linewidth=2, label="Curva Interpolada (Linear)")
        plt.scatter(self.dados_vertices['du'], self.dados_vertices['taxa_aa'], 
                    color='#d62728', marker='o', s=40, zorder=5, label="Vértices Reais (41 pontos)")
        
        plt.title(f"Estrutura a Termo de Taxas de Juros (ETTJ)\n{self.nome_curva}", fontsize=14, fontweight='bold')
        plt.xlabel("Prazo em Dias Úteis (DU)", fontsize=12)
        plt.ylabel("Taxa % ao Ano (Base 252)", fontsize=12)
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

# ==========================================
# EXECUÇÃO DO MOTOR
# ==========================================
if __name__ == "__main__":
    print("==================================================")
    print("🧠 INICIANDO MOTOR DE PRECIFICAÇÃO DE CURVA")
    print("==================================================")
    
    motor = ConstrutorCurvaJuros('curva_di_b3_atual.json')
    
    print(f"✅ Banco de dados carregado: {motor.nome_curva}")
    print(f"✅ Vértices Processados: {len(motor.dados_vertices)}")
    
    prazos_teste = [21, 63, 118, 252]
    print("\n🎯 TESTE DE INTERPOLAÇÃO (Prazos Aleatórios):")
    for prazo in prazos_teste:
        taxa = motor.obter_taxa_para_prazo(prazo)
        print(f" -> Taxa para {prazo:3d} DU: {taxa:.3f}% a.a.")
        
    print("==================================================\n")
    motor.plotar_curva()