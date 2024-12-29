import socket
import threading
import time
import uuid
import re

# Ansh #Nishant
def get_mac_address():
    mac = uuid.getnode()
    mac_address = ':'.join(re.findall('..', '%012x' % mac))
    return mac_address
#Nishant
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("192.168.131.2", 5555))
    server.listen(3)  
    print("Server started. Waiting for players...")

    connections = []
    player_names = []
    lobby = []
    survival_times = {}  
    game_start_time = time.time()
    game_over = False
    ghost_speed = 1.0  

    # Ansh
    def display_lobby():
        lobby_table = "\nPlayer No | Player Name | MAC Addr           | Name in Game\n"
        lobby_table += "-" * 60 + "\n"
        for entry in lobby:
            lobby_table += f"{entry['player_no']}          | {entry['player_name']}       | {entry['mac_addr']} | {entry['name_in_game']}\n"
        return lobby_table

    for i in range(3):
        conn, addr = server.accept()
        print(f"Player {i+1} connected: {addr}")

        mac_addr = get_mac_address()

        conn.sendall("Enter your name: ".encode())
        name = conn.recv(1024).decode().strip()
        player_symbol = name[0].upper() if name else f"P{i+1}"  
        player_names.append(name)
        connections.append(conn)

        lobby.append({
            "player_no": i + 1,
            "player_name": name,
            "mac_addr": mac_addr,
            "name_in_game": player_symbol
        })
        survival_times[name] = 0 
        conn.sendall(f"Welcome, {name}! Waiting for other players...\n".encode())
        conn.sendall(display_lobby().encode())

    grid_size = 16
    player_positions = [[15, 15], [15, 0], [0, 15]]  
    ghost_position = [1, 1]
    caught_players = set()
    #Nishant
    def generate_grid():
        grid = [["." for _ in range(grid_size)] for _ in range(grid_size)]
        for i, pos in enumerate(player_positions):
            if player_names[i] not in caught_players:  
                grid[pos[0]][pos[1]] = lobby[i]['name_in_game']
        grid[ghost_position[0]][ghost_position[1]] = "G"
        return grid
    #Nishant
    def send_grid_and_timer():
        grid = generate_grid()
        grid_str = "\n".join([" ".join(row) for row in grid]) + "\n"
        elapsed_time = time.time() - game_start_time
        time_left = 60 - int(elapsed_time)
        
        if time_left > 0:
            timer_str = f"\nTime left: {time_left} seconds\n"
        else:
            timer_str = "\nTime's up!\n"

        message = timer_str + grid_str
        for conn in connections:
            if conn not in caught_players:
                conn.sendall(message.encode())
    
# Ansh
    def move_ghost():
        active_positions = [player_positions[i] for i in range(3) if player_names[i] not in caught_players]
        if not active_positions:
            return
        
        for _ in range(2):  
            distances = [abs(ghost_position[0] - p[0]) + abs(ghost_position[1] - p[1]) for p in active_positions]
            target = active_positions[distances.index(min(distances))]

            if ghost_position[0] < target[0]:
                ghost_position[0] += 1
            elif ghost_position[0] > target[0]:
                ghost_position[0] -= 1
            if ghost_position[1] < target[1]:
                ghost_position[1] += 1
            elif ghost_position[1] > target[1]:
                ghost_position[1] -= 1
    #Nishant
    def game_loop():
        nonlocal game_over, ghost_speed
        while not game_over:
            move_ghost()
            send_grid_and_timer()
            
            for i, pos in enumerate(player_positions):
                if player_names[i] not in caught_players and pos == ghost_position:
                    caught_players.add(player_names[i])
                    survival_times[player_names[i]] = int(time.time() - game_start_time)
                    for conn in connections:
                        conn.sendall(f"{player_names[i]} was caught by the ghost! Ghost speed doubled!\n".encode())
                    ghost_speed /= 1.25  
            
            if len(caught_players) == 3 or time.time() - game_start_time >= 60:
                game_over = True
                break
            
            time.sleep(ghost_speed)

        for player in player_names:
            if player not in caught_players:
                survival_times[player] = 60
        leaderboard = sorted(survival_times.items(), key=lambda x: x[1], reverse=True)

        final_message = "\nGame Over! Final Leaderboard:\n"
        final_message += "Player Name | Survival Time (s)\n"
        final_message += "-" * 30 + "\n"
        for name, time_spent in leaderboard:
            final_message += f"{name}       | {time_spent}\n"
        for conn in connections:
            conn.sendall(final_message.encode())
    
# Ansh    
    def handle_player_input(player_id, conn):
        while not game_over:
            try:
                move = conn.recv(1024).decode().strip().upper()
                if player_names[player_id] in caught_players:
                    continue
                if move == "W" and player_positions[player_id][0] > 0:
                    player_positions[player_id][0] -= 1
                elif move == "S" and player_positions[player_id][0] < grid_size - 1:
                    player_positions[player_id][0] += 1
                elif move == "A" and player_positions[player_id][1] > 0:
                    player_positions[player_id][1] -= 1
                elif move == "D" and player_positions[player_id][1] < grid_size - 1:
                    player_positions[player_id][1] += 1
                elif move == "EXIT":
                    conn.sendall("You disconnected from the game.\n".encode())
                    break
            except Exception:
                break

    threading.Thread(target=game_loop, daemon=True).start()
    for i, conn in enumerate(connections):
        threading.Thread(target=handle_player_input, args=(i, conn), daemon=True).start()

    while not game_over:
        time.sleep(1)

    for conn in connections:
        conn.close()
    server.close()

if __name__ == "__main__":
    start_server()
