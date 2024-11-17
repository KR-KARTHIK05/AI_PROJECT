import random
import os
import json
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class BaseGame:
    def __init__(self, player_name):
        self.player_name = player_name
        self.load_user_stats()
        self.reset_stats()
        self.difficulty = 1  # Default difficulty

    def reset_stats(self):
        self.sanity = 0
        self.hearts_of_dead = self.user_stats.get('hearts_of_dead', 0)
        self.total_score = self.user_stats.get('total_score', 0)
        self.booster_chance = 45
        self.heart_of_dead_chance = 10
        self.player_position = random.randint(1, 25)
        self.ghost_position = random.randint(1, 25)
        while self.ghost_position == self.player_position:
            self.ghost_position = random.randint(1, 25)
        self.ghost_hunt = False
        self.hunt_duration = 0
        self.ghost_move_counter = 0

    def load_user_stats(self):
        try:
            if os.path.exists("user_stats.json"):
                with open("user_stats.json", "r") as file:
                    stats = json.load(file)
                self.user_stats = stats.get(self.player_name, {"games_played": 0, "total_score": 0, "best_score": 0, "hearts_of_dead": 0})
            else:
                self.user_stats = {"games_played": 0, "total_score": 0, "best_score": 0, "hearts_of_dead": 0}
        except Exception as e:
            print(f"Error loading stats: {e}")
            self.user_stats = {"games_played": 0, "total_score": 0, "best_score": 0, "hearts_of_dead": 0}

    def save_user_stats(self):
        try:
            if os.path.exists("user_stats.json"):
                with open("user_stats.json", "r") as file:
                    stats = json.load(file)
            else:
                stats = {}
            
            self.user_stats['total_score'] = self.total_score
            self.user_stats['hearts_of_dead'] = self.hearts_of_dead
            stats[self.player_name] = self.user_stats
            
            with open("user_stats.json", "w") as file:
                json.dump(stats, file, indent=4)
        except Exception as e:
            print(f"Error saving stats: {e}")

    def store(self):
        print("\nWelcome to the store!")
        print("You can exchange 2000 points for 1 Heart of the Dead.")
        print(f"Current Score: {self.total_score}")
        print(f"Current Hearts of the Dead: {self.hearts_of_dead}")

        if self.total_score < 2000:
            print("\nYou don't have enough points to exchange for a Heart of the Dead.")
            print("You need at least 2000 points.\n")
            return

        while True:
            choice = input("Do you want to exchange points for Hearts of the Dead? (y/n): ").strip().lower()
            if choice == 'y':
                possible_exchanges = self.total_score // 2000
                print(f"You can exchange up to {possible_exchanges} Hearts of the Dead.")
                num_exchanges = input(f"How many Hearts of the Dead would you like to purchase (1-{possible_exchanges})? ").strip()

                if num_exchanges.isdigit():
                    num_exchanges = int(num_exchanges)
                    if 1 <= num_exchanges <= possible_exchanges:
                        self.total_score -= num_exchanges * 2000
                        self.hearts_of_dead += num_exchanges
                        self.save_user_stats()
                        print(f"You successfully exchanged {num_exchanges * 2000} points for {num_exchanges} Hearts of the Dead!")
                        print(f"Remaining Score: {self.total_score}")
                        print(f"Current Hearts of the Dead: {self.hearts_of_dead}")
                    else:
                        print("Invalid number of exchanges. Please enter a valid amount.")
                else:
                    print("Invalid input. Please enter a valid number.")

                continue_shopping = input("Do you want to continue shopping? (y/n): ").strip().lower()
                if continue_shopping == 'n':
                    break
            elif choice == 'n':
                break
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

    def update_stats_on_game_over(self):
        self.user_stats["games_played"] += 1
        self.user_stats["total_score"] = self.total_score
        self.user_stats["hearts_of_dead"] = self.hearts_of_dead
        if self.total_score > self.user_stats["best_score"]:
            self.user_stats["best_score"] = self.total_score
        self.save_user_stats()

    def display_user_stats(self):
        print(f"\nUser Stats for {self.player_name}:")
        print(f"Games Played: {self.user_stats['games_played']}")
        print(f"Total Score: {self.user_stats['total_score']}")
        print(f"Hearts of the Dead Collected: {self.user_stats['hearts_of_dead']}")
        print(f"Best Score: {self.user_stats['best_score']}")

    def handle_ghost_encounter(self):
        print("The ghost caught you!")
        if self.hearts_of_dead > 0:
            while True:
                respawn_choice = input("You have a Heart of the Dead. Do you want to respawn? (y/n): ").strip().lower()
                if respawn_choice in ('y', 'n'):
                    break
                print("Invalid input. Please enter 'y' or 'n'.")
            
            if respawn_choice == 'y':
                self.hearts_of_dead -= 1
                respawn_sanity = {
                    1: 50,  # Easy
                    2: 35,  # Medium
                    3: 25   # Hard
                }
                self.sanity = respawn_sanity[self.difficulty]
                print(f"You have been respawned with {self.sanity} sanity points!")
                print(f"Remaining Hearts of the Dead: {self.hearts_of_dead}")
                # Move ghost to a new random position
                self.ghost_position = random.randint(1, 25)
                while self.ghost_position == self.player_position:
                    self.ghost_position = random.randint(1, 25)
                return True
            else:
                print("You chose not to respawn. Game Over.")
                return False
        else:
            print("You have no Hearts of the Dead to respawn. Game Over.")
            return False

    def get_available_moves(self, position):
        moves = [position + 1, position - 1, position + 5, position - 5, position + 4]
        valid_moves = []
        for move in moves:
            # Check if move is within board boundaries
            if 1 <= move <= 25:
                # Check if move doesn't cross board edges incorrectly
                if move == position + 1 and position % 5 == 0:  # Right edge
                    continue
                if move == position - 1 and position % 5 == 1:  # Left edge
                    continue
                if move == position + 4 and position % 5 == 1:  # Diagonal move check
                    continue
                valid_moves.append(move)
        return valid_moves

    def collect_powerup(self):
        if random.randint(1, 100) <= self.booster_chance:
            print("You found a booster tablet! Your sanity is restored.")
            self.sanity += 20
        elif random.randint(1, 100) <= self.heart_of_dead_chance:
            print("You found a Heart of the Dead!")
            self.hearts_of_dead += 1

class VisualGame(BaseGame):
    def __init__(self, player_name):
        super().__init__(player_name)
        self.setup_visualization()
        
    def setup_visualization(self):
        self.G = nx.Graph()
        # Add nodes (positions 1-25)
        for i in range(1, 26):
            self.G.add_node(i)
        
        # Add edges based on valid moves
        for pos in range(1, 26):
            if pos % 5 != 0:  # Right move
                self.G.add_edge(pos, pos + 1)
            if pos % 5 != 1:  # Left move
                self.G.add_edge(pos, pos - 1)
            if pos + 5 <= 25:  # Down move
                self.G.add_edge(pos, pos + 5)
            if pos - 5 >= 1:  # Up move
                self.G.add_edge(pos, pos - 5)
            if pos + 4 <= 25 and pos % 5 != 1:  # Diagonal move
                self.G.add_edge(pos, pos + 4)
        
        # Create a 5x5 grid layout
        self.pos = {}
        for i in range(1, 26):
            row = (i-1) // 5
            col = (i-1) % 5
            self.pos[i] = (col, -row)
        
        plt.ion()  # Enable interactive mode
        self.fig, self.ax = plt.subplots(figsize=(12, 12))
        
    def update_visualization(self):
        self.ax.clear()
        
        # Draw all nodes in light blue
        node_colors = ['lightblue' for _ in range(25)]
        
        # Highlight available moves in green
        available_moves = self.get_available_moves(self.player_position)
        for move in available_moves:
            node_colors[move-1] = 'lightgreen'
        
        # Highlight player position in blue
        node_colors[self.player_position-1] = 'blue'
        
        # Highlight ghost position in red
        node_colors[self.ghost_position-1] = 'red'
        
        # Draw the network
        nx.draw(self.G, pos=self.pos, 
                node_color=node_colors,
                node_size=1000,
                with_labels=True,
                font_size=16,
                font_weight='bold',
                width=2,
                edge_color='gray')
        
        # Add game status
        status_text = f"Sanity: {self.sanity}\n"
        status_text += f"Score: {self.total_score}\n"
        status_text += f"Hearts: {self.hearts_of_dead}\n"
        status_text += f"Ghost Hunt: {'Active' if self.ghost_hunt else 'Inactive'}"
        
        plt.title("Ghost Game Board", pad=20, size=16)
        plt.text(2.5, -6, status_text, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.7))
        
        plt.draw()
        plt.pause(0.1)

    def start_game(self):
        self.display_user_stats()

        store_choice = input("\nWould you like to visit the store and exchange points for Hearts of the Dead? (y/n): ").strip().lower()
        if store_choice == 'y':
            self.store()

        self.reset_stats()

        while True:
            try:
                self.difficulty = int(input("Select difficulty level (1-Easy, 2-Medium, 3-Hard): "))
                if self.difficulty in [1, 2, 3]:
                    break
                print("Please enter a valid difficulty level (1, 2, or 3)")
            except ValueError:
                print("Please enter a valid number")

        self.sanity = {1: 100, 2: 70, 3: 50}.get(self.difficulty, 50)
        self.play()
    
    def play(self):
        while self.sanity > 0:
            self.update_visualization()
            
            print(f"\nCurrent Position: {self.player_position}")
            print(f"Remaining Sanity: {self.sanity}")
            print(f"Current Score: {self.total_score}")
            print(f"Hearts of the Dead: {self.hearts_of_dead}")
            print(f"Difficulty Level: {'Easy' if self.difficulty == 1 else 'Medium' if self.difficulty == 2 else 'Hard'}")
            available_moves = self.get_available_moves(self.player_position)
            print(f"Available Moves: {available_moves}")
            
            user_move = input("Enter your move: ")
            if not user_move.isdigit():
                print("Invalid input. Please enter a number corresponding to one of the available moves.")
                continue
            
            user_move = int(user_move)
            if user_move in available_moves:
                self.player_position = user_move
                self.collect_powerup()
                
                base_sanity_loss = {1: 10, 2: 12, 3: 15}.get(self.difficulty, 10)
                self.sanity -= base_sanity_loss
                self.total_score += 50

                if self.ghost_move_counter >= 5:
                    self.ghost_hunt = True
                    self.hunt_duration = random.randint(2, 5)
                    print("The ghost is hunting you! Sanity will decrease faster.")
                else:
                    self.ghost_move_counter += 1

                if self.player_position == self.ghost_position:
                    if not self.handle_ghost_encounter():
                        break

                if self.ghost_hunt:
                    hunt_sanity_loss = {1: 6, 2: 8, 3: 10}.get(self.difficulty, 6)
                    self.sanity -= hunt_sanity_loss
                    self.hunt_duration -= 1
                    if self.hunt_duration == 0:
                        self.ghost_hunt = False
                        self.ghost_move_counter = 0

            else:
                print("Invalid move! Try again.")
        
        print("Game Over!")
        self.update_visualization()
        plt.pause(2)
        plt.close()
        self.update_stats_on_game_over()
        self.save_user_stats()

if __name__ == "__main__":
    player_name = input("Enter your name: ")
    print(f"User name is set to: {player_name}")
    game = VisualGame(player_name)
    game.start_game()