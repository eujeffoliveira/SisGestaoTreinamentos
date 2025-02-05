from sqlalchemy import create_engine, text

engine = create_engine(
    "mssql+pyodbc://dbtreina:dbtreina@NOLASCO1640\\NOLASCO/DBTREINAMENTOS?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&Encrypt=no"
)

with engine.connect() as conn:
    result = conn.execute(text("SELECT TOP 1 * FROM TBCARGO"))
    for row in result:
        print(row)
