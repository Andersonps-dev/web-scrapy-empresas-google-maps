import sqlite3
import pandas as pd

def limpar_duplicatas_e_salvar(db_path, tabela, subset=None):
    """
    Lê uma tabela do SQLite, remove duplicatas mantendo a primeira linha e sobrescreve a tabela no banco.

    Parâmetros:
        db_path (str): Caminho para o arquivo do banco SQLite.
        tabela (str): Nome da tabela a ser processada.
        subset (list ou str, opcional): Colunas a considerar para definir duplicatas. Se None, considera todas.
    """
    # Conecta ao banco
    conn = sqlite3.connect(db_path)

    try:
        # Lê a tabela com pandas
        df = pd.read_sql_query(f"SELECT * FROM {tabela}", conn)

        # Remove duplicatas
        df_limpo = df.drop_duplicates(subset=subset, keep='first')

        # Sobrescreve a tabela no banco
        df_limpo.to_sql(tabela, conn, if_exists='replace', index=False)

        print(f"Tabela '{tabela}' atualizada com {len(df_limpo)} registros (duplicatas removidas).")
    except Exception as e:
        print(f"Erro ao processar a tabela: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # Exemplo de uso
    limpar_duplicatas_e_salvar(
        db_path='dados_google_maps.db',
        tabela='negocios',
        subset=['address']  # ou use None para considerar todas as colunas
    )

