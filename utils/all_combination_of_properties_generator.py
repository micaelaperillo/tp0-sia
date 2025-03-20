import os
import json
import sys
import subprocess
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from src.catching import attempt_catch
from src.pokemon import PokemonFactory, StatusEffect
#we test two pokemons passed as parameters under different conditions

if __name__ == "__main__":
     # Check if we have the correct number of arguments
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <pokemon> <second_pokemon>")
        print("Example: python3 run_pokemon_script.py snorlax caterpie")
        sys.exit(1)
    
    first_pokemon = sys.argv[1]
    second_pokemon = sys.argv[2]
    print(f"First pokemon: {first_pokemon}, Second pokemon: {second_pokemon}")
    
    pokeball_types = ["pokeball", "ultraball", "fastball", "heavyball"]
    status_types = [StatusEffect.NONE, StatusEffect.BURN, StatusEffect.FREEZE, StatusEffect.POISON, StatusEffect.PARALYSIS, StatusEffect.SLEEP]
    status_names = {StatusEffect.NONE: "None", StatusEffect.BURN: "Burn", StatusEffect.FREEZE: "Freeze", StatusEffect.POISON: "Poison", StatusEffect.PARALYSIS: "Paralysis", StatusEffect.SLEEP: "Sleep"}
    
    factory = PokemonFactory("pokemon.json")

    # the output of the test is a file with the following format:
    # Pokemon: string with the name of the pokemon
    # Level: integer value between 1 and 100
    # Status: string with one of the following states: ["poison", "burn", "paralysis", "sleep", "freeze", "none"]
    # HP: integer value between 1 and 100

    for pokemon in [first_pokemon, second_pokemon]:
        with open(f'{pokemon}_conditions_combination.txt', 'w') as file:
            for ball in pokeball_types:
                for status in status_types:
                    for level in range (1, 101):
                        for health in range(1, 101):
                            lines = []
                            lines.append(f"Pokemon: {pokemon}\n")
                            lines.append(f"Pokeball: {ball}\n")
                            lines.append(f"Level: {level}\n")
                            lines.append(f"Status: {status_names[status]}\n")
                            lines.append(f"HP: {health}\n")
                            # we create the pokemon
                            pokemonCreated = factory.create(pokemon, level, status, health / 100)
                            # now we test catching it  
                            attempt_success, capture_rate = attempt_catch(pokemonCreated, ball)
                            lines.append(f"CaptureRate: {capture_rate}\n")
                            lines.append("------------------------------------------------------\n")
                            file.writelines(lines)
