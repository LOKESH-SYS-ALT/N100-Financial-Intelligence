import sqlite3

con = sqlite3.connect("data/nifty100.db")

for company in ["ABB", "AXISBANK"]:
    print("\n" + company)

    for table in ["profitandloss", "balancesheet", "cashflow"]:
        rows = con.execute(
            f"SELECT year FROM {table} "
            f"WHERE company_id = ? "
            f"ORDER BY rowid DESC LIMIT 5",
            (company,),
        ).fetchall()

        print(table + ":", rows)

con.close()