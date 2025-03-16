from src.pokemon import Pokemon, StatusEffect, PokemonFactory
from src.catching import attempt_catch
import pandas as pd
import json
import numpy as np

import matplotlib
matplotlib.use('Qt5Agg')  # 'Qt5Agg' o 'TkAgg'
import matplotlib.pyplot as plt

colors = {
        "pokeball": 'r',
        "fastball": 'g',
        "ultraball": 'b',
        "heavyball": 'y',
    }  

# 2a)
def analyze_health_and_capture(factory, pokeballs, pokemon_name):
    
    pokemon_df = pd.DataFrame(columns=["pokemon", "pokeball", "status", "mean", "std_dev"])

    experiments = 100 # Number of independent experiments
    attempts = 1000 # Number of attempts per experiment

    for status in StatusEffect:
        # Iterate through all status effects, 100 level (max), 0 hp percentage (min) are constant
        pokemon = factory.create(pokemon_name, 100, status, 0) 
        
        for pokeball in pokeballs:
            capture_attempts = []
            for _ in range(experiments):
                catched = 0
                for _ in range(attempts):
                    attempt_success, capture_rate = attempt_catch(pokemon, pokeball)
                    if attempt_success:
                        catched += 1
                capture_attempts.append(catched / attempts)
            pokemon_df = pd.concat([
                pokemon_df, 
                pd.DataFrame([[pokemon_name, pokeball, status.name, np.mean(capture_attempts), np.std(capture_attempts)]], 
                             columns=["pokemon", "pokeball", "status", "mean", "std_dev"])
            ], ignore_index=True)

    plt.figure(figsize=(10, 6))
    
    for pokeball in pokeballs:
        pokeball_df = pokemon_df[pokemon_df["pokeball"] == pokeball] 
        plt.plot(pokeball_df["status"], pokeball_df["mean"], color=colors[pokeball], label=pokeball, marker='o')
        plt.errorbar(pokeball_df["status"], pokeball_df["mean"], pokeball_df["std_dev"], fmt='none', color=colors[pokeball], capsize=3)

    plt.title(f"Mean vs Status for {pokemon_name}")
    plt.xlabel("Status")
    plt.ylabel("Mean")
    plt.grid(True)
    plt.legend()
    plt.show()

# 2b)
def analyze_hp_and_capture(factory, pokeballs, pokemon_name):
    pokemon_df = pd.DataFrame(columns=["pokemon", "pokeball", "hp", "mean", "std_dev"])

    experiments = 100 # Number of independent experiments
    attempts = 100 # Number of attempts per experiment

    for hp in range(0, 100, 5):
        # Iterate through all hp percentages, 100 level (max), NONE status are constant
        hp = hp / 100
        pokemon = factory.create(pokemon_name, 100, StatusEffect.NONE, hp) 
        
        for pokeball in pokeballs:
            capture_attempts = []
            for _ in range(experiments):
                catched = 0
                for _ in range(attempts):
                    attempt_success, capture_rate = attempt_catch(pokemon, pokeball)
                    if attempt_success:
                        catched += 1
                capture_attempts.append(catched / attempts)
            pokemon_df = pd.concat([
                pokemon_df, 
                pd.DataFrame([[pokemon_name, pokeball, hp, np.mean(capture_attempts), np.std(capture_attempts)]], 
                             columns=["pokemon", "pokeball", "hp", "mean", "std_dev"])
            ], ignore_index=True)

    plt.figure(figsize=(10, 6))
    for pokeball in pokeballs:
        pokeball_df = pokemon_df[pokemon_df["pokeball"] == pokeball]
        plt.plot(pokeball_df["hp"], pokeball_df["mean"], color=colors[pokeball], label=pokeball, marker='o')
        plt.errorbar(pokeball_df["hp"], pokeball_df["mean"], pokeball_df["std_dev"], fmt='none', color=colors[pokeball], capsize=3)

    plt.title(f"Mean vs Health Percentage (HP) for {pokemon_name}")
    plt.xlabel("HP %")
    plt.ylabel("Mean")
    plt.grid(True)
    plt.legend()
    plt.show()



def main():
    with open('pokemon.json', "r") as c:
        pokemon_names = json.load(c)   
    
    factory = PokemonFactory("pokemon.json")
    pokeballs = ["pokeball", "ultraball", "fastball", "heavyball"]

    for pokemon in pokemon_names.keys():
        analyze_health_and_capture(factory, pokeballs, pokemon)
        analyze_hp_and_capture(factory, pokeballs, pokemon)


if __name__ == "__main__":
    main()