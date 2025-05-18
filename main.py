def main():
    print("Game of Ayoo!")
    """
    Ayoo, also known as Oware, or Mancala in various regions is a traditional African board game 
    played with a wooden board containing pits (called houses) and small seeds or stones (called seeds or beans). 
    It is especially popular in West Africa.

    The goal is typically to capture more seeds than your opponent, and players take turns distributing seeds 
    around the board in a process called sowing. The gameplay generally emphasizes strategy, planning ahead, and sometimes a bit of bluffing.
    """

    # Initialize the game board with 12 pots (6 per player), each starting with 4 seeds.
    pots = [
        {"owner": "player1", "name": f"pot{i+1}", "seeds": 4} for i in range(6)
    ] + [
        {"owner": "player2", "name": f"pot{i+1}", "seeds": 4} for i in range(6)
    ]


    # Initialize the first player
    player = 1

    # Creating a variable to track the number of seeds to distribute for a player round
    pick_seeds_to_distribute = 0  

    # Dictionary to keep track of the number of seeds captured by each player
    player_seed_count = {"player1": 0, "player2": 0}

    # Sum all seeds from each pot on the board
    total_seed_on_board = sum(pot["seeds"] for pot in pots)


    while total_seed_on_board > 0:
        # Display board  
        display_board(pots)
        pot_names = [pot["name"] for pot in pots if pot["owner"] == f"player{player}"]
        

        while True:
            pot_selection = input(f"\nPlayer {player}, choose a pot to sow seeds from (pot1 to pot6): ").lower()

            if pot_selection in pot_names:
                # Find the index of the selected pot
                pot_index = next(i for i, pot in enumerate(pots) if pot["owner"] == f"player{player}" and pot["name"] == pot_selection)

                if pots[pot_index]["seeds"] == 0:
                    print(f"{pot_selection} is empty. Please choose a pot with seeds.")
                    continue
                else:
                    break

            else:
                print("Invalid pot name. Try again.")
                pot_selection = ""
                continue
                
        # Proceed to sow/distribute seeds from selected pot
        pick_seeds_to_distribute = pots[pot_index]["seeds"] #pick up seeds
        pots[pot_index]["seeds"] = 0    # selected pot is now empty
        pot_index = (pot_index + 1) % len(pots)  # Move to next pot

        print(f"\nSowing the seeds of {pot_selection}...")

        # Main game logic: distribute seeds and handle any captures before switching players
        distribute_seeds_across_pots(pots, pot_index, pick_seeds_to_distribute, player, player_seed_count)

        # Go through the current player's pots, find any with exactly 4 seeds, and capture them.
        clear_fours_in_players_pots(pots, player, pot_index, player_seed_count)

        # Update the sum all seeds from each pot on the board
        total_seed_on_board = sum(pot["seeds"] for pot in pots)

        if total_seed_on_board >= 8:
            # Switch to next player
            player = 2 if player == 1 else 1 

            # Now the new player sweeps their own pots
            clear_fours_in_players_pots(pots, player, pot_index, player_seed_count)

        else: #if there are only four seeds
            player_seed_count[f"player{player}"] += 4
            total_seed_on_board = 0



        print(f"Player 1 points: {player_seed_count['player1']} | Player 2 points: {player_seed_count['player2']}")

           
    if player_seed_count['player1'] > player_seed_count['player2']:
        print("Player 1 wins 🏆")
    elif player_seed_count['player2'] > player_seed_count['player1']:
        print("Player 2 wins 🏆")
    else:
        print("It's a tie")
    
        
       
    
def distribute_seeds_across_pots(pots, start_index, seeds_to_distribute, player, player_seed_count):
    """
    Distributes seeds one by one into pots starting from start_index.
    If the final seed lands in a pot with 0 or 3 seeds, perform capture and exit early.
    
    Returns the final pot index after distribution.
    """
    while seeds_to_distribute > 0:
        # start_index = (start_index + 1) % len(pots)  # move to next pot

        # If only 1 seed remains and pot is empty or has 3 seeds, place it in pot and handle capture 
        if seeds_to_distribute == 1 and pots[start_index]["seeds"] in (0, 3):
            pots[start_index]["seeds"] += 1
            seeds_to_distribute -= 1
            handle_capture(pots, player, start_index, player_seed_count)
            break

        elif seeds_to_distribute == 1:
            # Drop the last seed, pick up all seeds in this pot, and continue
            pots[start_index]["seeds"] += 1
            seeds_to_distribute = pots[start_index]["seeds"]
            pots[start_index]["seeds"] = 0
            start_index = (start_index + 1) % len(pots)

        else:
            # Otherwise, normal distribution: drop a seed and move on
            pots[start_index]["seeds"] += 1
            seeds_to_distribute -= 1

            if pots[start_index]["seeds"] == 4:
                handle_capture(pots, player, start_index, player_seed_count)

            start_index = (start_index + 1) % len(pots)
        
    return start_index
      

   
def display_board(pots):
    """
    Prints the current state of the board, showing how many seeds are in each player's pots.
    """
    print("\nPlayer 1 pots:")
    for pot in pots:
        if pot["owner"] == "player1":
            print(f'{pot["name"]}: {pot["seeds"]}')

    print("Player 2 pots:")
    for pot in pots:
        if pot["owner"] == "player2":
            print(f'{pot["name"]}: {pot["seeds"]}')



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



def clear_fours_in_players_pots(pots, player, pot_index, player_seed_count):
    """
    Checks all of the player’s other pots and captures any that have exactly 4 seeds.
    """
    for i, pot in enumerate(pots):
        if i != pot_index and pot["owner"] == f"player{player}" and pot["seeds"] == 4:
            pot["seeds"] = 0
            player_seed_count[f"player{player}"] += 4

    

if __name__ == "__main__":
    main()