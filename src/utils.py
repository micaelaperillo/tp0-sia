import json
import matplotlib.pyplot as plt
import numpy as np 
import pandas as pd
import os


from src.pokemon import PokemonFactory, StatusEffect, Pokemon
from src.catching import attempt_catch

colors = {
        "pokeball": 'r',
        "fastball": 'g',
        "ultraball": 'b',
        "heavyball": 'y',
}  

EXPERIMENTS = 100
ATTEMPTS = 100

# Ex: 1a
def average_probability_of_capture() -> None:

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


# Ex: 1b
def pokeball_effectiveness() -> None:
    
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

# Ex: 2a
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

    plt.title(f"Precisión de captura vs Estado para {pokemon_name}")
    plt.xlabel("Estado")
    plt.ylabel("Precisión de captura (Promedio)")
    plt.grid(True)
    plt.legend()
    plt.savefig(f"./graphs/health_capture_{pokemon_name}.png")
    print(f"Graph saved as health_capture_{pokemon_name}.png")

# Ex: 2b
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

    plt.title(f"Precisión de captura vs Porcentaje de Salud (HP) for {pokemon_name}")
    plt.xlabel("HP %")
    plt.ylabel("Precisión de captura (Promedio)")
    plt.grid(True)
    plt.legend()
    plt.savefig(f"./graphs/hp_capture_{pokemon_name}.png")
    print(f"Graph saved as hp_capture_{pokemon_name}.png")

# Ex: 2c
###     Variating Level    ###
def analyze_level_and_capture(factory, pokeballs, pokemon_names):

    figures = []  # Lista para almacenar las figuras

    for name in pokemon_names:
        fig, ax = plt.subplots(figsize=(10, 6))
        for ball in pokeballs:
            prob = []
            avg_prob_by_level = []
            std_prob_by_level = []
            levels = []

            for level in [1] + list(range(10, 101, 5)):

                for _ in range(ATTEMPTS):
                    captures = 0
                    for _ in range(EXPERIMENTS):
                        pokemon = factory.create(name, level, StatusEffect.NONE, 0.5)
                        success, catch_prob = attempt_catch(pokemon, ball)
                        if success:
                            captures += 1
                    prob.append(captures / EXPERIMENTS)

                levels.append(level)
                avg_prob_by_level.append(np.mean(prob))
                std_prob_by_level.append(np.std(prob))

            ax.errorbar(levels, avg_prob_by_level, yerr=std_prob_by_level, 
                        label=ball, marker='o', capsize=5, capthick=1)

        ax.set_title(f"Probabilidad de captura vs Nivel para {name}")
        ax.set_xlabel("Nivel")
        ax.set_ylabel("Probabilidad de captura")
        ax.grid(True)
        ax.legend(loc="upper left", bbox_to_anchor=(1, 1))

        figures.append((fig, name))  # Guardar figura en memoria

    # Guardar todas las imágenes al final
    output_dir = "graphs"
    os.makedirs(output_dir, exist_ok=True)

    for fig, name in figures:
        output_path = os.path.join(output_dir, f"level_capture_{name}.png")
        fig.savefig(output_path, bbox_inches="tight")
        plt.close(fig)  # Cerrar figura para liberar memoria


def analyze_level_and_capture_with_capture_rate(factory, pokeballs, pokemon_names):
    figures = []  # Lista para almacenar las figuras
    for name in pokemon_names:
        fig, ax = plt.subplots(figsize=(10, 6))
        for ball in pokeballs:
            prob = []
            levels = []

            for level in [1] + list(range(10, 101, 5)):
                pokemon = factory.create(name, level, StatusEffect.NONE, 0.5)
                success, catch_prob = attempt_catch(pokemon, ball)
                prob.append(catch_prob)
                levels.append(level)

            ax.plot(levels, prob, color=colors[ball], label=ball, marker='o')

        ax.set_title(f"Probabilidad de captura vs Nivel para %s " % name)
        ax.set_xlabel("Nivel")
        ax.set_ylabel("Probabilidad de captura")
        ax.grid(True)
        ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
        
        figures.append((fig, name))  # Guardar figura en memoria

    # Guardar todas las imágenes al final
    output_dir = "graphs"
    os.makedirs(output_dir, exist_ok=True)

    for fig, name in figures:
        output_path = os.path.join(output_dir, f"level_capture_{name}_with_capture_rate.png")
        fig.savefig(output_path, bbox_inches="tight")
        plt.close(fig)  # Cerrar figura para liberar memoria


###    Variating HP    ###
def analyze_hp_and_capture_with_capture_rate(factory, pokeballs, pokemon_names):

    figures = []  # Lista para almacenar las figuras

    for name in pokemon_names:
        fig, ax = plt.subplots(figsize=(10, 6))
        for ball in pokeballs:
            prob = []
            hps = []

            for hp in range(0, 101, 5):
                pokemon = factory.create(name, 50, StatusEffect.NONE, hp / 100)
                success, catch_prob = attempt_catch(pokemon, ball)
                prob.append(catch_prob)
                hps.append(hp)

            ax.plot(hps, prob, color=colors[ball], label=ball, marker='o')

        ax.set_title(f"Probabilidad de captura vs Porcentaje de salud (HP) para %s " % name)
        ax.set_xlabel("HP %")
        ax.set_ylabel("Probabilidad de captura")
        ax.grid(True)
        ax.legend(loc="upper left", bbox_to_anchor=(1, 1))

        figures.append((fig, name))  # Guardar figura en memoria

    # Guardar todas las imágenes al final
    output_dir = "graphs"
    os.makedirs(output_dir, exist_ok=True)

    for fig, name in figures:
        output_path = os.path.join(output_dir, f"hp_capture_{name}_with_capture_rate.png")
        fig.savefig(output_path, bbox_inches="tight")
        plt.close(fig)  # Cerrar figura para liberar memoria


###    Variating Status    ###
def analyze_status_and_capture_with_capture_rate(factory, pokeballs, pokemon_names):

    figures = []  # Lista para almacenar las figuras

    for name in pokemon_names:
        fig, ax = plt.subplots(figsize=(10, 6))
        for ball in pokeballs:
            prob = []
            statuses = []

            for status in StatusEffect:
                pokemon = factory.create(name, 50, status, 0.5)
                success, catch_prob = attempt_catch(pokemon, ball)
                prob.append(catch_prob)
                statuses.append(status.name)

            ax.plot(statuses, prob, color=colors[ball], label=ball, marker='o')
        
        ax.set_title(f"Probabilidad de captura vs Estado para %s " % name)
        ax.set_xlabel("Estado")
        ax.set_ylabel("Probabilidad de captura")
        ax.grid(True)
        ax.legend(loc="upper left", bbox_to_anchor=(1, 1))

        figures.append((fig, name))  # Guardar figura en memoria
    
    # Guardar todas las imágenes al final
    output_dir = "graphs"
    os.makedirs(output_dir, exist_ok=True)

    for fig, name in figures:
        output_path = os.path.join(output_dir, f"health_capture_{name}_with_capture_rate.png")
        fig.savefig(output_path, bbox_inches="tight")
        plt.close(fig)  # Cerrar figura para liberar memoria