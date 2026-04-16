import pandas as pd
import json
from datetime import datetime
import numpy as np
from io import StringIO
import warnings
import pyperclip  # <-- A nova biblioteca definitiva para a memória!

# Ignora avisos de formatação
warnings.filterwarnings('ignore')

class ExtratorCurvaClipboard:
    """
    Robô de extração de dados via Área de Transferência (Versão Super Blindada).
    Usa 'pyperclip' para garantir leitura nativa da memória sem depender do Pandas.
    """
    def executar_extracao(self, caminho_saida='curva_di_b3_atual.json'):
        print("📋 Lendo a sua Área de Transferência via Pyperclip...")
        
        try:
            # 1. Captura o texto bruto direto do Windows com segurança máxima
            texto_bruto = pyperclip.paste()
            
            if not texto_bruto or len(texto_bruto) < 10:
                raise ValueError("Sua área de transferência parece estar vazia. Dê um Ctrl+C na tabela do InfoMoney primeiro!")

            # 2. Força a leitura por TAB ('\t') e ignora as linhas corrompidas
            try:
                df_di = pd.read_csv(StringIO(texto_bruto), sep='\t', on_bad_lines='skip', decimal='.', thousands=',')
            except TypeError:
                df_di = pd.read_csv(StringIO(texto_bruto), sep='\t', error_bad_lines=False, warn_bad_lines=False, decimal=',', thousands='.')

            # 3. Limpeza: Padroniza os cabeçalhos
            df_di.columns = [str(col).strip().upper() for col in df_di.columns]

            # 4. Busca Dinâmica das Colunas
            col_venc = next((col for col in df_di.columns if 'VENCIMENTO' in col), None)
            col_taxa = next((col for col in df_di.columns if 'TAXA' in col and 'JUROS' in col), None)

            if not col_venc or not col_taxa:
                raise ValueError(f"Cabeçalhos não identificados. Colunas lidas: {list(df_di.columns)}\nCertifique-se de copiar desde a palavra 'CÓDIGO'.")

            # Isola os dados e força numérico
            df_di = df_di[[col_venc, col_taxa]].copy()
            df_di.columns = ['VENCIMENTO', 'TAXA_JUROS']
            df_di = df_di.dropna()
            df_di['TAXA_JUROS'] = pd.to_numeric(df_di['TAXA_JUROS'], errors='coerce')
            df_di = df_di.dropna()

            hoje = datetime.now().date()
            vertices = []

            print("⚙️ Processando matriz e calculando Dias Úteis (DU)...")
            # Loop de conversão Data -> DU
            for index, row in df_di.iterrows():
                vencimento_str = str(row['VENCIMENTO']).strip()
                try:
                    # Transformação temporal
                    venc_date = datetime.strptime(vencimento_str, "%d/%m/%Y").date()
                    du = int(np.busday_count(hoje, venc_date))
                    
                    if du > 0:
                        vertices.append({
                            "du": du,
                            "vencimento": venc_date.strftime("%Y-%m-%d"),
                            "taxa_aa": round(float(row['TAXA_JUROS']), 3)
                        })
                except Exception:
                    continue

            if not vertices:
                raise ValueError("Nenhum dado numérico extraído. Tente copiar novamente.")

            # Montagem do JSON final para o Banco Alpha
            banco_dados_json = {
                "nome_curva": "Curva DI1 Futuro (Banco Alpha - Live Clipboard)",
                "data_extracao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "fonte": "InfoMoney - Área de Transferência (Pyperclip)",
                "vertices": vertices
            }

            with open(caminho_saida, 'w', encoding='utf-8') as f:
                json.dump(banco_dados_json, f, ensure_ascii=False, indent=4)

            print(f"✅ Motor Super Blindado! {len(vertices)} vértices limpos e salvos com sucesso.")
            print(f"📁 Banco de dados gerado: {caminho_saida}")

        except Exception as e:
            print(f"❌ Falha de Leitura: {e}")

# ==========================================
# EXECUÇÃO DA CONTINGÊNCIA
# ==========================================
if __name__ == "__main__":
    robo = ExtratorCurvaClipboard()
    robo.executar_extracao()