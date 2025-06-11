import tkinter as tk
import math


# Define some constants for the canvas size
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 500

# Define the size of the game rectangle relative to the canvas
GAME_RECT_LENGTH = (3/4) * CANVAS_WIDTH # 75% of canvas width
GAME_RECT_HEIGHT = (1/4) * CANVAS_WIDTH # 25% of canvas width (proportional to width)

POTS = [{"owner": "player1", "pot_number": i, "seeds": 4} for i in range(1, 7)
        ] + [{"owner": "player2", "pot_number": i, "seeds": 4} for i in range(7, 13)] # Generate 12 pots, initializing each pot with 4 seeds

# Global list to hold pot position data for click detection
POT_POSITIONS = []  # Each item: (pot_number, cx, cy, radius)

PLAYER = 1

# Dictionary to keep track of the number of seeds captured by each player
PLAYER_SEED_COUNT = {"player1": 0, "player2": 0}

seeds_to_distribute = 0

# Sum all seeds from each pot on the board
total_seed_on_board = sum(pot["seeds"] for pot in POTS)
 

def main():
    root = tk.Tk()
    root.title("Ayoo Board")
    canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
    canvas.pack()

    # Create a label below the canvas to show scores
    score_label = tk.Label(root, text="", font=("Arial", 14), bg="#996D26", fg="white")
    score_label.pack(pady=10)

    # Create a label to show current turn
    turn_label = tk.Label(root, text="", font=("Arial", 12), fg="white", bg="#996D26")
    turn_label.pack(pady=5)

    canvas.create_rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, fill="#996D26")

    # Draw the game area and get inner rectangle coordinates
    x3, x4, y3, y4 = game_area_sqr(canvas)

    # Draw the game pots using the game_area_sqr coordinates
    draw_game_pot_at(canvas, x3, x4, y3, y4)

    # Update the initial label text
    update_labels(score_label, turn_label)

    # Start the main game loop
    main_game(canvas, score_label, turn_label)

    root.mainloop()



def game_area_sqr(canvas):
    # Calculate coordinates for the outer rectangle (game area)
    x1 = CANVAS_WIDTH / 8
    y1 = CANVAS_HEIGHT / 4
    x2 = x1 + GAME_RECT_LENGTH 
    y2 = y1 + GAME_RECT_HEIGHT

    # Calculate coordinates for the inner rectangle (game board border)
    x3 = x1 + 5
    y3 = y1 + 5
    x4 = x2 - 5
    y4 = y2 - 5 

    canvas.create_rectangle(x1, y1, x2, y2, fill="#7E5514", outline="")
    canvas.create_rectangle(x3, y3, x4, y4, fill="#F7D49C", outline="")

    return x3, x4, y3, y4

   

def draw_game_pot_at(canvas, x3, x4, y3, y4):
    W = x4 - x3  # Inner rectangle width
    num_circles = 6
    gap = W / 20  # gap between circles
    diameter = (W - (num_circles + 1) * gap) / num_circles # from W = 6*d + 7*g
    radius = diameter / 2
    

    # Calculate the vertical centers for rows
    y_center = (y3 + y4) / 2
    y_top_row_center = (y3 + y_center) / 2
    y_bottom_row_center = (y_center + y4) / 2

    def draw_pot_and_seeds(cx, cy, pot_number):
        # Draw the pot
        canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill="#996D26", outline="")

        # Find the pot data from POTS
        pot_data = next((p for p in POTS if p["pot_number"] == pot_number), None)
        if pot_data:
            num_seeds = pot_data["seeds"]

            # Distribute seeds evenly in a circle within the pot
            seed_radius = radius / 5
            for i in range(num_seeds):
                angle = (2 * math.pi / num_seeds) * i
                seed_cx = cx + (radius / 2) * math.cos(angle)
                seed_cy = cy + (radius / 2) * math.sin(angle)
                canvas.create_oval(seed_cx - seed_radius, seed_cy - seed_radius,
                                   seed_cx + seed_radius, seed_cy + seed_radius,
                                   fill="#F7D49C", outline="black")
                
        # Save pot position for click detection
        POT_POSITIONS.append((pot_number, cx, cy, radius))
            
    # Draw top row of pots
    for i in range(num_circles):
        cx = x3 + gap + radius + i * (diameter + gap)
        draw_pot_and_seeds(cx, y_top_row_center, i + 1)

    # Draw bottom row of pots (pots 12 to 7 in reverse)
    for i in range(num_circles):
        cx = x3 + gap + radius + i * (diameter + gap)
        pot_number = 12 - i
        draw_pot_and_seeds(cx, y_bottom_row_center, pot_number)



def main_game(canvas, score_label, turn_label):
    # Bind a custom handler to the click event
    canvas.bind("<Button-1>", lambda event: handle_player_click(event, canvas, score_label, turn_label))


def handle_player_click(event, canvas, score_label, turn_label):
    global total_seed_on_board, PLAYER

    pot_num_selected = on_click(event)
    if pot_num_selected is None:
        return

    selected_pot = POTS[pot_num_selected - 1]

    # Restriction: only let the current player play their pots
    if selected_pot["owner"] != f"player{PLAYER}":
        print(f"Invalid move! It's Player {PLAYER}'s turn. Please select your own pot.")
        return

    # Check if the pot has seeds
    seeds_to_distribute = selected_pot["seeds"]
    if seeds_to_distribute == 0:
        print("This pot is empty. Please select a pot with seeds.")
        return

    # Proceed with normal seed distribution
    POTS[pot_num_selected - 1]["seeds"] = 0

    next_pot = (pot_num_selected + 1) % len(POTS)
    distribute_seeds_across_pots(POTS, next_pot, seeds_to_distribute, PLAYER, PLAYER_SEED_COUNT)

    # Clear any 4s for this player
    clear_fours_in_players_pots(POTS, PLAYER, next_pot, PLAYER_SEED_COUNT)

    # Update the total seeds on board
    total_seed_on_board = sum(pot["seeds"] for pot in POTS)

    # Check if we need to switch players
    if total_seed_on_board >= 8:
        PLAYER = 2 if PLAYER == 1 else 1
        clear_fours_in_players_pots(POTS, PLAYER, next_pot, PLAYER_SEED_COUNT)
    else:
        # Only 4 seeds left, give them to the current player and end
        PLAYER_SEED_COUNT[f"player{PLAYER}"] += 4
        total_seed_on_board = 0
        print("Game Over!")
        declare_winner(score_label, turn_label)
        return

    # Update the labels
    update_labels(score_label, turn_label)

    # Redraw the board
    refresh_canvas(canvas)


def on_click(event):
    x_click, y_click = event.x, event.y
    for pot_number, cx, cy, radius in POT_POSITIONS:
        dist = math.sqrt((x_click - cx) ** 2 + (y_click - cy) ** 2)
        if dist <= radius:
            print(f"Clicked pot {pot_number} at ({cx}, {cy})!")
            return pot_number
    # If we get here, no pot was clicked
    print("You haven't selected a Pot. Please select a Pot")

    


def distribute_seeds_across_pots(pots, pot_selected, seeds_to_distribute, player, player_seed_count):
    """
    Distributes seeds one by one into pots starting from start_index.
    If the final seed lands in a pot with 0 or 3 seeds, perform capture and exit early.
    
    Returns the final pot index after distribution.
    """
    while seeds_to_distribute > 0:

        # If only 1 seed remains and pot is empty or has 3 seeds, place it in pot and handle capture 
        if seeds_to_distribute == 1 and pots[pot_selected - 1]["seeds"] in (0, 3):
            pots[pot_selected - 1]["seeds"] += 1
            seeds_to_distribute -= 1
            handle_capture(pots, player, pot_selected - 1, player_seed_count)
            break

        elif seeds_to_distribute == 1:
            # Drop the last seed, pick up all seeds in this pot, and continue
            pots[pot_selected - 1]["seeds"] += 1
            seeds_to_distribute = pots[pot_selected - 1]["seeds"]
            pots[pot_selected - 1]["seeds"] = 0
            pot_selected = (pot_selected + 1) % len(pots)

        else:
            # Otherwise, normal distribution: drop a seed and move on
            pots[pot_selected - 1]["seeds"] += 1
            seeds_to_distribute -= 1

            if pots[pot_selected - 1]["seeds"] == 4:
                handle_capture(pots, player, pot_selected - 1, player_seed_count)

            pot_selected = (pot_selected + 1) % len(pots)
        
    return pot_selected



def handle_capture(pots, player, pot_index, player_seed_count):
    """
    If the pot at pot_index has exactly 4 seeds, capture them.
    Then, in all pots owned by the player that have exactly 4 seeds, capture those too.
    If the pot at pot_index does not have 4 seeds, only sweep other pots with 4 seeds.
    """

    # First block: capture from the specified pot if it qualifies
    if pot_index >= 0 and pots[pot_index]["seeds"] == 4:
        player_seed_count[f"player{player}"] += 4
        pots[pot_index]["seeds"] = 0
            

def refresh_canvas(canvas):
    # Clear the canvas
    canvas.delete("all")
    
    # Redraw the background
    canvas.create_rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, fill="#996D26")
    
    # Redraw game area
    x3, x4, y3, y4 = game_area_sqr(canvas)
    
    # Redraw pots and seeds
    draw_game_pot_at(canvas, x3, x4, y3, y4)


def clear_fours_in_players_pots(pots, player, pot_index, player_seed_count):
    """
    Checks all of the players other pots and captures any that have exactly 4 seeds.
    """
    for i, pot in enumerate(pots):
        if i != pot_index and pot["owner"] == f"player{player}" and pot["seeds"] == 4:
            pot["seeds"] = 0
            player_seed_count[f"player{player}"] += 4


def update_labels(score_label, turn_label):
    score_label.config(text=f"Player 1 points: {PLAYER_SEED_COUNT['player1']} | Player 2 points: {PLAYER_SEED_COUNT['player2']}")
    turn_label.config(text=f"Player {PLAYER}'s Turn!")


def declare_winner(score_label, turn_label):
    p1 = PLAYER_SEED_COUNT['player1']
    p2 = PLAYER_SEED_COUNT['player2']
    if p1 > p2:
        winner = "Player 1"
    elif p2 > p1:
        winner = "Player 2"
    else:
        winner = "It's a Tie!"
    turn_label.config(text=f"Game Over! {winner} wins!")
    score_label.config(text=f"Final Score - Player 1: {p1} | Player 2: {p2}")


            
            



if __name__ == "__main__":
    main()