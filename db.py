import mysql.connector

try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        port=8080
        
    )
    if connection.is_connected():
        print("Connected to MySQL!")
except mysql.connector.Error as e:
    print(f"Error: {e}")
finally:
    # Safely close the connection if it was established
    if 'connection' in locals() and connection.is_connected():
        connection.close()
