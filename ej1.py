import json
import matplotlib.pyplot as plt
import numpy as np 
import pandas as pd


from src.pokemon import PokemonFactory, StatusEffect, Pokemon
from src.catching import attempt_catch

def a() -> None:

    with open("pokemon.json", "r") as file1, open("pokeball.json", "r") as file2:
        pokemons = json.load(file1)
        pokeballs = json.load(file2)
        factory = PokemonFactory("pokemon.json")

        capture_data = {} # Almacena los datos de captura para cada pokébola
    
        for pokeball in pokeballs.keys():
            print(f"Probabilidad de captura por Pokémon con {pokeball}")
            catched_counts = []  # Lista para almacenar los porcentajes por Pokémon
            for pokemon in pokemons.keys():
                pokemon_created = factory.create(pokemon, 100, StatusEffect.NONE, 1)
                probability = getProbabilityOfCapture(pokemon_created, pokeball, 100)
                catched_counts.append(probability)
                print(f"{pokemon_created.name}: {probability}%")
            capture_data[pokeball] = catched_counts
            print(f"Probabilidad de captura de {pokeball}: {sum(catched_counts) / len(catched_counts)}%\n")

        plt.figure(figsize=(8, 6))
        plt.boxplot(capture_data.values(), labels=capture_data.keys(), patch_artist=True)
        plt.ylabel("Probabilidad de captura (%)")
        plt.title("Distribución de probabilidad de captura por Pokebola")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.savefig("./graphs/boxplot.png")

        plt.figure(figsize=(8, 6))
        avg_catch_rates = {pokeball: sum(catched_counts) / len(catched_counts) for pokeball, catched_counts in capture_data.items()}
        std_errors = {pokeball: np.std(catched_counts, ddof=1) for pokeball, catched_counts in capture_data.items()}
        plt.bar(avg_catch_rates.keys(), avg_catch_rates.values(), yerr=std_errors.values(), capsize=5, color="skyblue", edgecolor="black")
        plt.ylim(0, 100)
        plt.ylabel("Probabilidad promedio de captura (%)")
        plt.xlabel("Tipo de Pokébola")
        plt.title("Probabilidad promedio de captura por Pokébola")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.savefig("./graphs/bar_chart.png")



def b() -> None:
    
    with open("pokemon.json", "r") as file1, open("pokeball.json", "r") as file2:
        pokemons = json.load(file1)
        pokeballs = json.load(file2)
        factory = PokemonFactory("pokemon.json")

        effectiveness = {}

        for pokemon in pokemons.keys():
            pokemon_created = factory.create(pokemon, 100, StatusEffect.NONE, 1)
            effectiveness[pokemon] = {}
            for pokeball in pokeballs.keys():
                probability = getProbabilityOfCapture(pokemon_created, pokeball, 10000)
                if(pokeball == "pokeball"):
                    effectiveness[pokemon][pokeball] = round(probability,1)
                    print(f"\n{pokemon_created.name} con POKEBOLA BASICA: {probability}%")
                else:
                    if effectiveness[pokemon]["pokeball"] != 0:
                        effectiveness[pokemon][pokeball] = round(probability / effectiveness[pokemon]["pokeball"],2)
                        print(f"{pokemon_created.name} con {pokeball}: {probability}%")
                    else: effectiveness[pokemon][pokeball] = "infinito"
                    print(f"Efectividad: {effectiveness[pokemon][pokeball]}")
        
        df = pd.DataFrame.from_dict(effectiveness, orient="index")
        df.replace("infinito", "∞", inplace=True)
        first_column = df.columns[0]
        df[first_column] = df[first_column].map(lambda x: f"{x}%" if isinstance(x, (int, float)) else x)

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.axis("tight")
        ax.axis("off")

        cell_colours = [
            ['lightblue' if j == 0 else 'lightgreen' if j != 0 else 'white' for j in range(df.shape[1])]
            for i in range(df.shape[0])
        ]

        ax.table(cellText=df.values, colLabels=df.columns, rowLabels=df.index, cellLoc="center", loc="center", cellColours=cell_colours)
        plt.savefig("./graphs/tabla_efectividad.png", bbox_inches="tight", dpi=300)    



def getProbabilityOfCapture(pokemon: Pokemon, ball: str, iterations: int) -> float:
    catched = 0
    for i in range(iterations):
        is_catched,_ = attempt_catch(pokemon, ball)
        if is_catched:
            catched += 1
    return catched * 100 / iterations