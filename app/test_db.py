
import mysql.connector

try:
    conexion = mysql.connector.connect(
        host="206.183.130.17",
        user="Meta5",
        password="Meta51",
        database="Meta5",
        port=7701
    )

    if conexion.is_connected():
        print("✅ Conexión exitosa a MySQL")

        cursor = conexion.cursor()
        cursor.execute("SELECT DATABASE();")
        db = cursor.fetchone()
        print("📂 Base de datos actual:", db[0])

except Exception as e:
    print("❌ Error de conexión:", e)

finally:
    if 'conexion' in locals() and conexion.is_connected():
        conexion.close()
        print("🔒 Conexión cerrada")


# import MetaTrader5 as mt5

# if not mt5.initialize():
#     print("initialize() failed")
#     print(mt5.last_error())
#     quit()

# account_info = mt5.account_info()
# print(account_info)