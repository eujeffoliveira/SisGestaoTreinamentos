import pyodbc

conn_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=NOLASCO1640\\NOLASCO;"
    "DATABASE=DBTREINAMENTOS;"
    "UID=dbtreina;"
    "PWD=dbtreina;"
    "TrustServerCertificate=yes;"
)

try:
    conn = pyodbc.connect(conn_string)
    print("Conexão realizada com sucesso!")
    
    # Cria um cursor para executar consultas
    cursor = conn.cursor()
    
    # Executa a consulta na tabela TBCARGO
    cursor.execute("SELECT * FROM TBCARGO")
    
    # Recupera todas as linhas retornadas
    rows = cursor.fetchall()
    
    # Exibe cada registro
    for row in rows:
        print(row)

except pyodbc.Error as e:
    print("Erro ao conectar ou executar consulta:", e)
finally:
    conn.close()
    print("Conexão encerrada.")
