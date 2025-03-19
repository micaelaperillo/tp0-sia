from src.pokemon import Pokemon, StatusEffect, PokemonFactory
from src.catching import attempt_catch
import json
import numpy as np
import matplotlib
import os

matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

colors = {
    "pokeball": 'r',
    "fastball": 'g',
    "ultraball": 'b',
    "heavyball": 'y',
}

EXPERIMENTS = 100
ATTEMPTS = 100

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



def main():

    factory = PokemonFactory("pokemon.json")

    with open("pokemon.json", "r") as f:
        pokemon_names = json.load(f)

    with open('pokeball.json', "r") as c:
        pokeballs = json.load(c).keys()

    analyze_level_and_capture(factory, pokeballs, pokemon_names)

    analyze_level_and_capture_with_capture_rate(factory, pokeballs, pokemon_names)

    analyze_hp_and_capture_with_capture_rate(factory, pokeballs, pokemon_names)

    analyze_status_and_capture_with_capture_rate(factory, pokeballs, pokemon_names)

    

if __name__ == "__main__":
    main()
