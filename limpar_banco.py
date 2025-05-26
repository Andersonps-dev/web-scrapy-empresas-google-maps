import sqlite3
import pandas as pd

def limpar_duplicatas_e_salvar(db_path, tabela, subset=None):
    conn = sqlite3.connect(db_path)

    try:
        df = pd.read_sql_query(f"SELECT * FROM {tabela}", conn)

        df_limpo = df.drop_duplicates(subset=subset, keep='first')

        df_limpo.to_sql(tabela, conn, if_exists='replace', index=False)

        print(f"Tabela '{tabela}' atualizada com {len(df_limpo)} registros (duplicatas removidas).")
    except Exception as e:
        print(f"Erro ao processar a tabela: {e}")
    finally:
        conn.close()

def coleta_aleatorio(db_path, tabela, n=None):
    conn = sqlite3.connect(db_path)

    df = pd.read_sql_query(f"SELECT * FROM {tabela}", conn)

    df_amostra = df.sample(n=n, random_state=42)

    df_amostra.to_excel('amostra_200_linhas.xlsx', index=False)

    conn.close()

if __name__ == "__main__":
    limpar_duplicatas_e_salvar(
        db_path='dados_google_maps.db',
        tabela='negocios',
        subset=['address']
    )

    # coleta_aleatorio(
    #     db_path='dados_google_maps.db',
    #     tabela='negocios',
    #     n=200
    # )

