import random
import os
import networkx as nx
import matplotlib.pyplot as plt 

# PlayerStats class to manage and save player stats
class PlayerStats:
    def __init__(self, name):
        self.name = name
        self.games_played = 0
        self.total_score = 0
        self.best_score = 0
        self.hearts_of_dead = 0
        self.load_stats()

    def load_stats(self):
        try:
            if os.path.exists("player_stats.txt"):
                with open("player_stats.txt", "r") as file:
                    lines = file.readlines()
                    for line in lines:
                        player_data = line.strip().split(": ")
                        if player_data[0] == self.name:
                            stats = player_data[1].split(", ")
                            self.games_played = int(stats[0].split("=")[1])
                            self.total_score = int(stats[1].split("=")[1])
                            self.best_score = int(stats[2].split("=")[1])
                            self.hearts_of_dead = int(stats[3].split("=")[1])
                            return
        except Exception as e:
            print(f"Error loading stats: {e}")

    def save_stats(self):
        try:
            stats_line = f"{self.name}: games_played={self.games_played}, total_score={self.total_score}, best_score={self.best_score}, hearts_of_dead={self.hearts_of_dead}\n"
            
            if os.path.exists("player_stats.txt"):
                with open("player_stats.txt", "r") as file:
                    lines = file.readlines()
                with open("player_stats.txt", "w") as file:
                    updated = False
                    for line in lines:
                        if line.startswith(self.name):
                            file.write(stats_line)
                            updated = True
                        else:
                            file.write(line)
                    if not updated:
                        file.write(stats_line)
            else:
                with open("player_stats.txt", "w") as file:
                    file.write(stats_line)
        except Exception as e:
            print(f"Error saving stats: {e}")

    def display_stats(self):
        print(f"Player: {self.name}")
        print(f"Games Played: {self.games_played}")
        print(f"Total Score: {self.total_score}")
        print(f"Best Score: {self.best_score}")
        print(f"Hearts of the Dead: {self.hearts_of_dead}")

    def update_games_played(self):
        self.games_played += 1
        self.save_stats()

    def update_score(self, score):
        self.total_score += score
        if score > self.best_score:
            self.best_score = score
        self.save_stats()

# Game class
class Game:
    def __init__(self, player_name):
        self.player_name = player_name
        self.player_stats = PlayerStats(player_name)
        self.player_stats.display_stats()  # Display stats upon initialization
        self.difficulty = self.get_difficulty()  # Ask player for difficulty
        self.reset_stats()

    def get_difficulty(self):
        while True:
            try:
                choice = int(input("Choose difficulty: Easy-1, Medium-2, Hard-3: "))
                if choice in [1, 2, 3]:
                    return choice
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def reset_stats(self):
        print("Initializing Game...")
        self.sanity = 100
        self.hearts_of_dead = self.player_stats.hearts_of_dead
        self.current_score = 0
        self.player_position = random.randint(0, 23)
        self.ghost_position = self.get_distant_ghost_position()
        self.G = nx.random_geometric_graph(24, 0.33)
        self.pos = nx.spring_layout(self.G, k=2, seed=100)
        print("Game initialized.")

    def get_distant_ghost_position(self):
        while True:
            pos = random.randint(0, 23)
            if self.manhattan_distance(pos, self.player_position) >= 4:
                return pos

    def manhattan_distance(self, pos1, pos2):
        return abs(pos1 - pos2)

    def visualize_game_state(self):
        plt.clf()  # Clear the plot
        nx.draw_networkx_edges(self.G, self.pos, edge_color='gray', width=1, alpha=0.5)
        nx.draw_networkx_nodes(self.G, self.pos, node_color='white', node_size=500, edgecolors='gray')

        nx.draw_networkx_nodes(self.G, self.pos, 
                              nodelist=[self.player_position],  
                              node_color='green', node_size=700, 
                              label='Player', node_shape='o')

        nx.draw_networkx_nodes(self.G, self.pos, 
                              nodelist=[self.ghost_position],  
                              node_color='red', node_size=700, 
                              label='Ghost', node_shape='h')

        labels = {i: str(i+1) for i in self.G.nodes()}
        nx.draw_networkx_labels(self.G, self.pos, labels)

        plt.text(0.02, 0.02, f'Sanity: {self.sanity}', 
                 transform=plt.gca().transAxes, verticalalignment='top')
        plt.text(0.02, 0.05, f'Current Score: {self.current_score}', 
                 transform=plt.gca().transAxes, verticalalignment='top')
        
        plt.title(f'Ghost Game - Difficulty: {["Easy", "Medium", "Hard"][self.difficulty - 1]}')
        plt.axis('off')

        plt.draw()
        plt.pause(0.1)

    def ghost_move_towards_player(self):
        if self.player_position > self.ghost_position:
            self.ghost_position += 1
        elif self.player_position < self.ghost_position:
            self.ghost_position -= 1

    def check_ghost_catch(self):
        if self.player_position == self.ghost_position:
            print("The ghost caught you!")
            self.player_stats.update_games_played()
            self.player_stats.update_score(self.current_score)
            return True
        return False

    def on_click(self, event):
        print(f"Mouse clicked at: ({event.xdata}, {event.ydata})")
        if event.inaxes is not None:
            x, y = event.xdata, event.ydata
            closest_node = None
            min_distance = float('inf')
            
            for node, (nx, ny) in self.pos.items():
                dist = (x - nx)**2 + (y - ny)**2
                if dist < min_distance:
                    min_distance = dist
                    closest_node = node
            
            if closest_node is not None:
                self.player_position = closest_node
                self.current_score += 10
                print(f"Player moved to position: {self.player_position + 1}")
                self.visualize_game_state()

def main():
    player_name = input("Enter your player name: ")
    game = Game(player_name)

    fig, ax = plt.subplots(figsize=(8, 8))
    fig.canvas.mpl_connect('button_press_event', game.on_click)

    while True:
        plt.pause(1)  # Pause for 1 second between ghost moves
        game.ghost_move_towards_player()
        game.visualize_game_state()
        if game.check_ghost_catch():
            break

    print("Game Over!")

if __name__ == "__main__":
    main()
