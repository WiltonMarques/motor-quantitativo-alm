import pandas as pd
import requests
import json
from datetime import datetime
from io import StringIO
import warnings

# Ignora os avisos de segurança de SSL
warnings.filterwarnings('ignore')

class ExtratorCurvaB3:
    """
    Robô de extração de dados da B3 - Versão Sem Paradoxo Temporal
    Busca sempre o último fechamento disponível no servidor, ignorando datas futuras.
    """
    def __init__(self):
        # Acessando a URL pura. A B3 automaticamente redireciona para o último dia útil disponível.
        self.url_b3 = "http://www2.bmf.com.br/pages/portal/bmfbovespa/boletim1/TxRef1.asp"
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml",
            "Connection": "keep-alive"
        }

    def executar_extracao(self, caminho_saida='curva_di_b3_atual.json'):
        print("🌐 Conectando ao servidor da B3 (Buscando último pregão disponível)...")
        
        try:
            resposta = requests.get(self.url_b3, headers=self.headers, verify=False, timeout=15)
            
            # Empacota e lê o HTML
            html_data = StringIO(resposta.text)
            tabelas = pd.read_html(html_data, decimal=',', thousands='.')
            
            # Procura a tabela do DI (Geralmente a primeira tabela com estrutura de 3 ou mais colunas)
            df_di = None
            for tb in tabelas:
                if len(tb.columns) >= 3 and len(tb) > 5:
                    df_di = tb
                    break
                    
            if df_di is None:
                raise ValueError("Nenhuma tabela válida encontrada. O Firewall da B3 pode ter bloqueado o IP.")

            # Isola as colunas: Dias Corridos, Dias Úteis, Taxa
            df_di = df_di.iloc[:, [0, 1, 2]]
            df_di.columns = ['Dias_Corridos', 'Dias_Uteis', 'Taxa_AA']
            
            # Limpeza cirúrgica
            df_di['Dias_Uteis'] = pd.to_numeric(df_di['Dias_Uteis'], errors='coerce')
            df_di['Taxa_AA'] = pd.to_numeric(df_di['Taxa_AA'], errors='coerce')
            df_di = df_di.dropna().astype({'Dias_Uteis': int})

            # Formatando o JSON
            vertices = []
            for index, row in df_di.iterrows():
                if row['Dias_Uteis'] > 0: # Ignora o vértice zero para evitar divisão por zero na matemática
                    vertices.append({
                        "du": int(row['Dias_Uteis']),
                        "vencimento": "N/A", 
                        "taxa_aa": round(float(row['Taxa_AA']), 2)
                    })

            if not vertices:
                raise ValueError("A tabela estava vazia após a limpeza.")

            banco_dados_json = {
                "nome_curva": "Curva DI1 Futuro (Live B3)",
                "data_extracao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "fonte": "B3 - Último Pregão Disponível",
                "vertices": vertices
            }

            with open(caminho_saida, 'w', encoding='utf-8') as f:
                json.dump(banco_dados_json, f, ensure_ascii=False, indent=4)

            print(f"✅ Extrato Concluído! {len(vertices)} vértices reais salvos com sucesso.")
            print(f"📁 Arquivo atualizado: {caminho_saida}")

        except Exception as e:
            print(f"❌ Falha Crítica na B3: {e}")
            print("⚠️ Dica: Se o erro persistir, a B3 está bloqueando requisições automáticas neste momento. O motor continuará funcionando com o JSON offline (parametros_curva.json).")

if __name__ == "__main__":
    robo = ExtratorCurvaB3()
    robo.executar_extracao()