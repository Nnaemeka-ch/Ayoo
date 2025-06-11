import tkinter as tk
import math
import time
import random


class Okwe:
    def __init__(self, root, canvas_width=800, canvas_height=500):
        self.root = root
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.game_rect_length = (3/4) * self.canvas_width
        self.game_rect_height = (1/3) * self.canvas_width

        self.root.title("Okwe Board")
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()

        # Calculate coordinates for the outer rectangle (game area)
        self.x1 = self.canvas_width / 8
        self.y1 = self.canvas_height / 4 
        self.x2 = self.x1 + self.game_rect_length
        self.y2 = self.y1 + self.game_rect_height

        # Calculate coordinates for the inner rectangle (game board border)
        self.x3 = self.x1 + 5
        self.y3 = self.y1 + 5
        self.x4 = self.x2 - 5
        self.y4 = self.y2 - 5

        # Calculate dimensions for pots
        self.inner_width = self.x4 - self.x3  # inner width
        self.num_circles = 6
        self.gap = self.inner_width/ 20
        self.diameter = (self.inner_width - (self.num_circles + 1) * self.gap) / self.num_circles
        self.radius = self.diameter / 2

        # Canvas center
        self.cx_canvas = self.canvas_width / 2
        self.cy_canvas = self.canvas_height / 2

        # Calculate vertical centers for pot rows
        self.y_center = (self.y3 + self.y4) / 2
        self.y_top_row_center = (self.y3 + self.y_center) / 2
        self.y_bottom_row_center = (self.y_center + self.y4) / 2

        # Pots and player setup
        self.game_pots = [{"owner": "player1", "pot_number": i, "seeds": 4} for i in range(1, 7)
        ] + [{"owner": "player2", "pot_number": i, "seeds": 4} for i in range(7, 13)] 

        # Initialize player
        self.player = 1
        self.selected_pot = None
        self.pot_information = []
        self.player_seed_count = {"player1": 0, "player2": 0}

        # Sum all seeds from each pot on the board
        self.total_seed = sum(pot["seeds"] for pot in self.game_pots)

        # Used to track and remove the previous highlight
        self.highlight_id = None  

        # Bind click event once
        self.canvas.bind("<Button-1>", self.player_move)


    def game_area_sqr(self):
        # Draw outer and inner rectangles
        self.canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, fill="#7E5514", outline="")
        self.canvas.create_rectangle(self.x3, self.y3, self.x4, self.y4, fill="#EDC9AF", outline="")
        self.show_player_turn()
        self.draw_scores()
    

    def draw_game_pot_at(self):
        #Resetting each round
        self.pot_information.clear()

        def draw_pot_and_seeds(cx, cy, pot_number):
            # Draw the pot
            self.canvas.create_oval(cx - self.radius, cy - self.radius, cx + self.radius, cy + self.radius, fill="#996D26", outline="")

            # Find the pot data from POTS
            pot_data = next((p for p in self.game_pots if p["pot_number"] == pot_number), None)
            if pot_data:
                num_seeds = pot_data["seeds"]

                # Distribute seeds evenly in a circle within the pot
                seed_radius = self.radius / 5
                for i in range(num_seeds):
                    angle = (2 * math.pi / num_seeds) * i
                    seed_cx = cx + (self.radius / 2) * math.cos(angle)
                    seed_cy = cy + (self.radius / 2) * math.sin(angle)
                    self.canvas.create_oval(seed_cx - seed_radius, seed_cy - seed_radius,
                                    seed_cx + seed_radius, seed_cy + seed_radius,
                                    fill="#EDC9AF", outline="")
                    
            # Save pot position for click detection
            self.pot_information.append((pot_number, cx, cy, self.radius))

        # Draw bottom row: 1 → 6 (left to right)
        for i in range(self.num_circles):
            cx = self.x3 + self.gap + self.radius + i * (self.diameter + self.gap)
            draw_pot_and_seeds(cx, self.y_bottom_row_center, i + 1)

        # Draw top row: 12 → 7 (right to left)
        for i in range(self.num_circles):
            cx = self.x3 + self.gap + self.radius + i * (self.diameter + self.gap)
            draw_pot_and_seeds(cx, self.y_top_row_center, 12 - i)


    def player_move(self, event):
        if self.player != 1:
            # Ignore clicks when it's not player's turn
            return

        x_click, y_click = event.x, event.y
        for pot_number, cx, cy, radius in self.pot_information:
            if math.hypot(x_click - cx, y_click - cy) <= radius:
                # Check if pot belongs to current player and has seeds
                pot = next((p for p in self.game_pots if p["pot_number"] == pot_number), None)
                if pot and pot["owner"] == f"player{self.player}" and pot["seeds"] > 0:
                    print(f"Clicked pot {pot_number} at ({cx}, {cy})!")
                    self.selected_pot = pot_number
                    self.highlight_selected_pot()
                    self.root.after(1000, self.game_play) 
                    
                    # Switch to computer
                    self.root.after(2000, self.switch_to_computer)
                    self.computer_move
                    return
                else:
                    print("Invalid pot selected. Select a pot with seeds that belongs to you.")
                    return

        print("You haven't selected a Pot. Please select a Pot.")


    def switch_to_computer(self):
        self.player = 2
        self.computer_move()


    def switch_to_player(self):
        self.player = 1


    def computer_move(self):
        if self.player != 2:
            return  # Not computer's turn

        if not self.has_playable_pots():
            print(f"Player {self.player} has no seeds. Skipping turn.")
            self.player = 1
            return

        # Computer picks a pot (avoid 3 seed pots if possible)
        computer_pots = [p for p in self.game_pots if p["owner"] == "player2" and p["seeds"] > 0]
        non_three_seed_pots = [p for p in computer_pots if p['seeds'] != 3]

        if non_three_seed_pots:
            chosen_pot = random.choice(non_three_seed_pots)["pot_number"]
        else:
            pots_with_three = [p for p in computer_pots if p['seeds'] == 3]
            chosen_pot = random.choice(pots_with_three)["pot_number"] if pots_with_three else None

        if chosen_pot is None:
            print("Computer has no valid pots to play. Skipping turn.")
            self.player = 1
            return

        print(f"Computer selected pot {chosen_pot}")
        self.selected_pot = chosen_pot
        self.highlight_selected_pot()
        self.root.after(2000, self.game_play)
        
        # Add game over check before switching to player
        self.root.after(2500, lambda: None if self.end_game_check() else self.switch_to_player())

    
    def game_play(self):
        self.pot_in_play = next((p for p in self.game_pots if p["pot_number"] == self.selected_pot), None)

        # Check if the pot has seeds
        if self.pot_in_play is None or self.pot_in_play["seeds"] == 0:
            print("This pot is empty or invalid. Please select a valid pot.")
            return
        
        # variable to track the number of seeds to distribute for a player round
        seeds_to_distribute = self.pot_in_play["seeds"] 
        self.pot_in_play["seeds"] = 0    # selected pot is now empty
        self.next_pot_number = (self.selected_pot % len(self.game_pots)) + 1    # Move to next pot

        self.distribute_seeds(seeds_to_distribute)
        self.clear_fours_in_players_pots() # Clear any 4s for this player
        # time.sleep(2) # Pause for effect

        # Reset board display
        self.canvas.delete("all")
        self.game_area_sqr()
        self.draw_game_pot_at()
        self.highlight_selected_pot()

        # Check end-game condition
        if self.end_game_check():
            return


    def highlight_selected_pot(self):
        # Clear previous highlight if it exists
        if self.highlight_id is not None:
            self.canvas.delete(self.highlight_id)
            self.highlight_id = None

        for pot_number, cx, cy, radius in self.pot_information:
            if pot_number == self.selected_pot:
                pot_data = next((p for p in self.game_pots if p["pot_number"] == pot_number), None)
                if pot_data and pot_data["owner"] == f"player{self.player}" and pot_data["seeds"] > 0:
                    highlight_margin = 6
                    self.highlight_id = self.canvas.create_oval(
                        cx - radius - highlight_margin,
                        cy - radius - highlight_margin,
                        cx + radius + highlight_margin,
                        cy + radius + highlight_margin,
                        outline="red",
                        width=3
                    )
                    return


    def  distribute_seeds(self, seeds_to_distribute):
        while seeds_to_distribute > 0:
            # Since indexes start at 0, a pot's index is its number minus 1
            next_pot_index = self.next_pot_number - 1 
            pot_in_action = self.game_pots[next_pot_index] 
            
            # If only 1 seed remains to play and pot to play into is empty or has 3 seeds, place it in pot and handle capture 
            if seeds_to_distribute == 1 and pot_in_action["seeds"] == 0:
                pot_in_action["seeds"] += 1
                seeds_to_distribute -= 1
                self.handle_capture(pot_in_action, sweet_capture=False)
                break

            elif seeds_to_distribute == 1 and pot_in_action["seeds"] == 3:
                pot_in_action["seeds"] += 1
                seeds_to_distribute -= 1
                self.handle_capture(pot_in_action, sweet_capture=True)
                break

            elif seeds_to_distribute == 1:
                # If only 1 seed remains to play, drop the seed, pick up all seeds in this pot, and continue
                pot_in_action["seeds"] += 1
                seeds_to_distribute = pot_in_action["seeds"]
                pot_in_action["seeds"] = 0
                self.next_pot_number = (self.next_pot_number % len(self.game_pots)) + 1

            else:
                # Otherwise, normal distribution: drop a seed and move on
                pot_in_action["seeds"] += 1
                seeds_to_distribute -= 1

                if pot_in_action["seeds"] == 4:
                    self.handle_capture(pot_in_action, sweet_capture=False)
                self.next_pot_number = (self.next_pot_number % len(self.game_pots)) + 1


    def handle_capture(self, pot_to_capture, sweet_capture):
        # First block: capture from the specified pot if it qualifies
        if pot_to_capture["seeds"] == 4:
            if sweet_capture:
                # Sweet rule: capture even if the pot belongs to opponent
                print(f"Sweet capture! 4 seeds captured from pot {pot_to_capture['pot_number']} by player{self.player}")
                self.player_seed_count[f"player{self.player}"] += 4
            else:
                owner = pot_to_capture["owner"]
                print(f"Regular capture: 4 seeds captured from pot {pot_to_capture['pot_number']} assigned to {owner}")
                self.player_seed_count[owner] += 4

            pot_to_capture["seeds"] = 0
            

    def clear_fours_in_players_pots(self):
        """
        Scans all pots owned by the current player and captures
        seeds from any pot (excluding the last played one) that contains exactly 4.
        """
        for pot in self.game_pots:
            if pot["owner"] == f"player{self.player}" and pot["seeds"] == 4 and pot["pot_number"] != self.next_pot_number:
                pot["seeds"] = 0
                self.player_seed_count[f"player{self.player}"] += 4


    def end_game_check(self):
        self.total_seed = sum(pot["seeds"] for pot in self.game_pots)
        if self.total_seed <= 4:
            self.player_seed_count[f"player{self.player}"] += self.total_seed
            print("Game Over!")
            self.draw_scores()
            self.declare_winner()
            # Unbind click to prevent further interaction
            self.canvas.unbind("<Button-1>")
            return True
        return False
    

    def declare_winner(self):
        p1 = self.player_seed_count["player1"]
        p2 = self.player_seed_count["player2"]

        if p1 > p2:
            message = "🎉 You Win!"
        elif p2 > p1:
            message = "🤖 Computer Wins!"
        else:
            message = "It's a tie!"

        self.canvas.create_text(
            self.cx_canvas,
            self.cy_canvas + 30,
            text=message,
            font=("Arial", 20, "bold"),
            fill="#996D26",
            anchor='center'
        )


    def has_playable_pots(self):
        # Returns True if the player has at least one pot with seeds.
        return any((pot for pot in self.game_pots if pot["owner"] == f"player{self.player}" and pot["seeds"] > 0))
    

    def show_player_turn(self):
        # Clear previous message area with a filled rectangle
        self.canvas.create_rectangle(
            self.cx_canvas - 180, self.cy_canvas - 20,
            self.cx_canvas + 180, self.cy_canvas + 40,
            fill="#EDC9AF", outline="#EDC9AF"
        )

        message = (
            "🧑 Your Turn! Make a move..." if self.player == 1
            else "🤖 Computer's Turn... 💭"
        )

        self.canvas.create_text(
            self.cx_canvas,
            self.cy_canvas,
            text=message,
            font=("Arial", 15),
            fill="#996D26",
            anchor='center'
        )


    def draw_scores(self):
        # Clear the top area where scores are shown to avoid overlapping of text
        self.canvas.create_rectangle(
            20, 20,
            self.canvas_width - 20, 40,
            fill="#EDC9AF", outline="#EDC9AF"
        )

        # Then draw the score
        self.canvas.create_text(
            self.cx_canvas,
            self.y1 + 20,
            text=f"You: {self.player_seed_count['player1']} | Computer: {self.player_seed_count['player2']}",
            font=("Arial", 10),
            fill="#996D26",
            anchor='center'
        )   



                

if __name__ == "__main__":
    root = tk.Tk()
    game = Okwe(root)
    game.game_area_sqr()
    game.draw_game_pot_at()
    root.mainloop()