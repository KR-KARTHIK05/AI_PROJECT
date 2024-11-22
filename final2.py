#this is the final one
import random
import os
import json
from heapq import heappush, heappop
import networkx as nx
import matplotlib.pyplot as plt
from playsound import playsound



def visualize_game_state(game):
    if not hasattr(game, 'G'):
        game.G = nx.random_geometric_graph(24, 0.33)
        edges = list(game.G.edges())
        game.pos = nx.spring_layout(game.G, k=2, seed=100)  # Adjust 'k' for spacing

        
        # Ensure the graph is connected
        while not nx.is_connected(game.G):
            largest_cc = max(nx.connected_components(game.G), key=len)
            for node in game.G.nodes():
                if node not in largest_cc:
                    target = random.choice(list(largest_cc))
                    game.G.add_edge(node, target)
    
    # Clear previous plot
    plt.clf()
    
    # Draw edges
    nx.draw_networkx_edges(game.G, game.pos, edge_color='gray', width=1, alpha=0.5)
    
    # Draw all nodes as empty cells
    nx.draw_networkx_nodes(game.G, game.pos, node_color='white', 
                          node_size=500, edgecolors='gray')
    
    # Draw player position
    nx.draw_networkx_nodes(game.G, game.pos, 
                          nodelist=[game.player_position-1],
                          node_color='green', node_size=700, 
                          label='Player', node_shape='o')
    
    # Draw ghost position
    nx.draw_networkx_nodes(game.G, game.pos, 
                          nodelist=[game.ghost_position-1],
                          node_color='red', node_size=700, 
                          label='Ghost', node_shape='h')
    
    # Add node labels
    labels = {i: str(i+1) for i in game.G.nodes()}
    nx.draw_networkx_labels(game.G, game.pos, labels)
    
    # Add game stats
    plt.text(0.02, 0.004, f'Sanity: {game.sanity}', 
             transform=plt.gca().transAxes, verticalalignment='top')
    plt.text(0.02, 0.057, f'Current Score: {game.current_score}', 
             transform=plt.gca().transAxes, verticalalignment='top')
    
    plt.legend()
    
    difficulty_name = {1: 'Easy', 2: 'Medium', 3: 'Hard'}[game.difficulty]
    plt.title(f'Ghost Game - {difficulty_name} Mode')
    
    plt.axis('off')
    
    plt.pause(0.1)

class Game:
    def __init__(self, player_name):
        self.player_name = player_name
        self.load_user_stats()
        self.reset_stats()
        self.difficulty = 1  # Default difficulty
        
    def reset_stats(self):
        self.sanity = 0
        self.hearts_of_dead = self.user_stats.get('hearts_of_dead', 0)
        self.current_score = 0  # Reset current game score to 0
        self.booster_chance = 45
        self.heart_of_dead_chance = 10
        self.player_position = random.randint(1, 25)
        self.ghost_position = self.get_distant_ghost_position()
        self.ghost_hunt = False
        self.hunt_duration = 0
        self.ghost_move_counter = 0

    def get_distant_ghost_position(self):
        while True:
            pos = random.randint(1, 25)
            if self.manhattan_distance(pos, self.player_position) >= 4:
                return pos

    def manhattan_distance(self, pos1, pos2):
        if hasattr(self, 'G'):
            try:
                return nx.shortest_path_length(self.G, pos1-1, pos2-1)
            except nx.NetworkXNoPath:
                return float('inf')
        return abs((pos1-1) - (pos2-1))  # Fallback if graph not initialized

    def get_neighbors(self, position):
        if hasattr(self, 'G'):
            return [n+1 for n in self.G.neighbors(position-1)]
        return []

    def astar_pathfinding(self, start, goal):
        if not hasattr(self, 'G'):
            return start
            
        try:
            path = nx.shortest_path(self.G, start-1, goal-1)
            return path[1]+1 if len(path) > 1 else start
        except nx.NetworkXNoPath:
            return start

    def move_ghost(self):
        if self.ghost_hunt:
            self.hunt_duration -= 1
            self.ghost_position = self.astar_pathfinding(self.ghost_position, self.player_position)
            if self.hunt_duration == 0:  # End hunt mode after duration
                self.ghost_hunt = False
                self.ghost_move_counter = 0
                print("The ghost has stopped hunting. You're safe... for now.")
        else:
            if self.ghost_move_counter >= 5:
                if not self.ghost_hunt:  # Only play the sound when the hunt starts
                    print("The ghost is hunting you! Sanity will decrease by 6 each move.")
                    playsound("/Sound/iseeyou.mp3")
                self.ghost_hunt = True
                self.hunt_duration = random.randint(2, 5)
            else:
                self.ghost_move_counter += 1
                if self.difficulty == 1:  # Easy
                    if random.random() < 0.6:
                        self.ghost_position = self.astar_pathfinding(self.ghost_position, self.player_position)
                elif self.difficulty == 2:  # Medium
                    if random.random() < 0.8:
                        self.ghost_position = self.astar_pathfinding(self.ghost_position, self.player_position)
                else:  # Hard
                    self.ghost_position = self.astar_pathfinding(self.ghost_position, self.player_position)


    def load_user_stats(self):
        try:
            if os.path.exists("user_stats.json"):
                with open("user_stats.json", "r") as file:
                    stats = json.load(file)
                self.user_stats = stats.get(self.player_name, {
                    "games_played": 0,
                    "total_score": 0,
                    "best_score": 0,
                    "hearts_of_dead": 0
                })
            else:
                self.user_stats = {
                    "games_played": 0,
                    "total_score": 0,
                    "best_score": 0,
                    "hearts_of_dead": 0
                }
        except Exception as e:
            print(f"Error loading stats: {e}")
            self.user_stats = {
                "games_played": 0,
                "total_score": 0,
                "best_score": 0,
                "hearts_of_dead": 0
            }

    def save_user_stats(self):
        try:
            if os.path.exists("user_stats.json"):
                with open("user_stats.json", "r") as file:
                    stats = json.load(file)
            else:
                stats = {}
            
            # Update the user's total score by adding the current game's score
            self.user_stats['total_score'] += self.current_score
            self.user_stats['hearts_of_dead'] = self.hearts_of_dead
            stats[self.player_name] = self.user_stats
            
            with open("user_stats.json", "w") as file:
                json.dump(stats, file, indent=4)
        except Exception as e:
            print(f"Error saving stats: {e}")

    def store(self):
        print("\nWelcome to the store!")
        print("You can exchange 2000 points for 1 Heart of the Dead.")
        print(f"Total Score: {self.user_stats['total_score']}")
        print(f"Current Hearts of the Dead: {self.hearts_of_dead}")

        if self.user_stats['total_score'] < 2000:
            print("\nYou don't have enough points to exchange for a Heart of the Dead.")
            print("You need at least 2000 points.\n")
            return

        while True:
            choice = input("Do you want to exchange points for Hearts of the Dead? (y/n): ").strip().lower()
            if choice == 'y':
                possible_exchanges = self.user_stats['total_score'] // 2000
                print(f"You can exchange up to {possible_exchanges} Hearts of the Dead.")
                num_exchanges = input(f"How many Hearts of the Dead would you like to purchase (1-{possible_exchanges})? ").strip()

                if num_exchanges.isdigit():
                    num_exchanges = int(num_exchanges)
                    if 1 <= num_exchanges <= possible_exchanges:
                        self.user_stats['total_score'] -= num_exchanges * 2000
                        self.hearts_of_dead += num_exchanges
                        self.save_user_stats()
                        playsound("/Sound/revive.mp3")
                        print(f"You successfully exchanged {num_exchanges * 2000} points for {num_exchanges} Hearts of the Dead!")
                        print(f"Remaining Total Score: {self.user_stats['total_score']}")
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
        
        # Update best score if current score is higher
        if self.current_score > self.user_stats["best_score"]:
            self.user_stats["best_score"] = self.current_score
            print(f"New Best Score: {self.current_score}!")
        
        # Add current game's score to total score
        self.user_stats["total_score"] += self.current_score
        self.user_stats["hearts_of_dead"] = self.hearts_of_dead
        self.save_user_stats()

    def display_user_stats(self):
        print(f"\nUser Stats for {self.player_name}:")
        print(f"Games Played: {self.user_stats['games_played']}")
        print(f"Total Score: {self.user_stats['total_score']}")
        print(f"Best Score: {self.user_stats['best_score']}")
        print(f"Hearts of the Dead Collected: {self.user_stats['hearts_of_dead']}")

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

    def handle_ghost_encounter(self):
        print("The ghost caught you!")
        if self.hearts_of_dead > 0:
            while True:
                respawn_choice = input("You have a Heart of the Dead. Do you want to respawn? (y/n): ").strip().lower()
                if respawn_choice in ('y', 'n'):
                    break
                print("Invalid input. Please enter 'y' or 'n'.")
            
            if respawn_choice == 'y':
                playsound("/Sound/breath.mp3")
                self.hearts_of_dead -= 1
                respawn_sanity = {
                    1: 50,  # Easy
                    2: 35,  # Medium
                    3: 25   # Hard
                }
                self.sanity = respawn_sanity[self.difficulty]
                print(f"You have been respawned with {self.sanity} sanity points!")
                print(f"Remaining Hearts of the Dead: {self.hearts_of_dead}")
                self.ghost_position = self.get_distant_ghost_position()
                return True
            else:
                print("You chose not to respawn. Game Over.")
                return False
        else:
            print("You have no Hearts of the Dead to respawn. Game Over.")
            return False

    def collect_powerup(self):
        if random.randint(1, 100) <= self.booster_chance:
            print("You found a booster tablet! Your sanity is restored.")
            self.sanity += 20
        elif random.randint(1, 100) <= self.heart_of_dead_chance:
            print("You found a Heart of the Dead!")
            playsound("/Sound/revive.mp3")
            self.hearts_of_dead += 1

    def play(self):
        plt.figure(figsize=(10, 10))
        
        while self.sanity > 0:
            visualize_game_state(self)
            
            print(f"\nCurrent Position: {self.player_position}")
            print(f"Current Score: {self.current_score}")
            print(f"Ghost Position: {self.ghost_position}")
            print(f"Sanity: {self.sanity}")

            available_moves = self.get_neighbors(self.player_position)
            print(f"Available Moves: {available_moves}")
            
            user_move = input("Enter your move: ")
            if not user_move.isdigit():
                print("Invalid input. Please enter a number corresponding to one of the available moves.")
                continue
            
            user_move = int(user_move)
            if user_move in available_moves:
                self.player_position = user_move
                self.collect_powerup()
                
                self.move_ghost()
                
                distance_to_ghost = self.manhattan_distance(self.player_position, self.ghost_position)
                base_sanity_loss = {1: 8, 2: 10, 3: 12}.get(self.difficulty, 8)
                proximity_penalty = max(0, (5 - distance_to_ghost) * 2)
                self.sanity -= (base_sanity_loss + proximity_penalty)

                if self.ghost_hunt:
                    self.sanity -= 6  # Additional sanity loss during hunt

                self.current_score += 10  # Update current game score

                if self.player_position == self.ghost_position:
                    if not self.handle_ghost_encounter():
                        break
            else:
                print("Invalid move! Try again.")
        
        print("Game Over!")
        playsound("/Sound/end.mp3")
        print(f"Final Score this game: {self.current_score}")
        plt.close()
        self.update_stats_on_game_over()


if __name__ == "__main__":
    player_name = input("Enter your name: ")
    print(f"User name is set to: {player_name}")
    game = Game(player_name)
    game.start_game()