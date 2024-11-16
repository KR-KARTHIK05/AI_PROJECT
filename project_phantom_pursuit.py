import random
import os
import json

# Game class
class Game:
    def __init__(self, player_name):
        self.player_name = player_name
        self.reset_stats()

    def reset_stats(self):
        self.sanity = 0
        self.total_score = 0
        self.hearts_of_dead = 0
        self.booster_chance = 45  # 45% chance to find a booster
        self.heart_of_dead_chance = 10  # 10% chance to find a Heart of the Dead
        self.player_position = random.randint(1, 25)
        self.ghost_position = random.randint(1, 25)
        while self.ghost_position == self.player_position:
            self.ghost_position = random.randint(1, 25)
        self.load_user_stats()
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

            # Update only the current user's stats
            stats[self.player_name] = self.user_stats
            
            with open("user_stats.json", "w") as file:
                json.dump(stats, file, indent=4)
        except Exception as e:
            print(f"Error saving stats: {e}")

    def update_stats_on_game_over(self):
        self.user_stats["games_played"] += 1
        self.user_stats["total_score"] += self.total_score
        self.user_stats["hearts_of_dead"] += self.hearts_of_dead
        if self.total_score > self.user_stats["best_score"]:
            self.user_stats["best_score"] = self.total_score

    def display_user_stats(self):
        print(f"\nUser Stats for {self.player_name}:")
        print(f"Games Played: {self.user_stats['games_played']}")
        print(f"Total Score: {self.user_stats['total_score']}")
        print(f"Hearts of the Dead Collected: {self.user_stats['hearts_of_dead']}")
        print(f"Best Score: {self.user_stats['best_score']}")

    def start_game(self):
        self.display_user_stats()

        store_choice = input("\nWould you like to visit the store and exchange points for Hearts of the Dead? (y/n): ").strip().lower()
        if store_choice == 'y':
            self.store()

        self.reset_stats()

        difficulty = int(input("Select difficulty level (1-Easy, 2-Medium, 3-Hard): "))
        self.sanity = {1: 100, 2: 70, 3: 50}.get(difficulty, 50)
        self.play()

    def play(self):
        while self.sanity > 0:
            print(f"\nCurrent Position: {self.player_position}")
            print(f"Remaining Sanity: {self.sanity}")
            print(f"Current Score: {self.total_score}")
            print(f"Hearts of the Dead: {self.hearts_of_dead}")
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
                self.sanity -= 10
                self.total_score += 50

                if self.ghost_move_counter >= 5:
                    self.ghost_hunt = True
                    self.hunt_duration = random.randint(2, 5)
                    print("The ghost is hunting you! Sanity will decrease by 6 each move.")
                else:
                    self.ghost_move_counter += 1

                if self.player_position == self.ghost_position:
                    print("The ghost caught you!")
                    if self.hearts_of_dead > 0:
                        while True:
                            respawn_choice = input("You have a Heart of the Dead. Do you want to respawn? (y/n): ").strip().lower()
                            if respawn_choice in ('y', 'n'):
                                break
                            print("Invalid input. Please enter 'y' or 'n'.")
                        if respawn_choice == 'y':
                            self.hearts_of_dead -= 1
                            self.sanity = 50
                            print("You have been respawned with 50 sanity points!")
                            print(f"Remaining Hearts of the Dead: {self.hearts_of_dead}")
                            continue
                        else:
                            print("You chose not to respawn. Game Over.")
                            break
                    else:
                        print("You have no Hearts of the Dead to respawn. Game Over.")                            
                        break


                if self.ghost_hunt:
                    self.sanity -= 6
                    self.hunt_duration -= 1
                    if self.hunt_duration == 0:
                        self.ghost_hunt = False

            else:
                print("Invalid move! Try again.")
        
        print("Game Over!")
        self.update_stats_on_game_over()
        self.save_user_stats()

    def get_available_moves(self, position):
        moves = [position + 1, position - 1, position + 5, position - 5, position + 4]
        return [move for move in moves if 1 <= move <= 25]

    def collect_powerup(self):
        if random.randint(1, 100) <= self.booster_chance:
            print("You found a booster tablet! Your sanity is restored.")
            self.sanity += 20
        elif random.randint(1, 100) <= self.heart_of_dead_chance:
            print("You found a Heart of the Dead!")
            self.hearts_of_dead += 1

if __name__ == "__main__":
    player_name = input("Enter your name: ")
    print(f"User name is set to: {player_name}")
    game = Game(player_name)
    game.start_game()
