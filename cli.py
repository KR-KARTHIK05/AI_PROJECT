import socket
import threading
import os

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(("192.168.131.2", 5555))  
    except Exception as e:
        print(f"Unable to connect to the server: {e}")
        return

    def receive_data():
        while True:
            try:
                data = client.recv(4096).decode()
                if not data:
                    print("Disconnected from the server.")
                    break
                os.system("cls" if os.name == "nt" else "clear") 
                print(data)
            except Exception as e:
                print(f"Error receiving data: {e}")
                break

    threading.Thread(target=receive_data, daemon=True).start()
    # Ansh
    try:
        name = input("Enter your name: ").strip()
        if not name:
            name = "Player"
        client.sendall(name.encode())  

        print(f"Your name representation in the game: {name[0].upper()}")
    except Exception as e:
        print(f"Error sending name: {e}")
        return
    
# Ansh
    while True:
        try:
            move = input("Move (W/A/S/D or EXIT to quit): ").strip().upper()
            if move in ["W", "A", "S", "D", "EXIT"]:
                client.sendall(move.encode())
                if move == "EXIT":
                    print("You have exited the game.")
                    break
            else:
                print("Invalid move! Use W, A, S, D, or EXIT.")
        except Exception as e:
            print(f"Error sending data: {e}")
            break

    client.close()

if __name__ == "__main__":
    start_client()
