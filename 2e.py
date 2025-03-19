from src.pokemon import StatusEffect, PokemonFactory
from src.catching import attempt_catch
import json
import matplotlib
import os
import sys

matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

colors = {
    "pokeball": 'r',
    "fastball": 'g',
    "ultraball": 'b',
    "heavyball": 'y',
}

def analyze_effectiveness(factory,pokemon_name, status_list, hp_min, hp_max, pokeballs):

    for status in status_list:
        fig, ax = plt.subplots(figsize=(10, 6))
        for ball in pokeballs:
            prob = []
            levels = []

            for level in [1] + list(range(10, 101, 5)):
                pokemon = factory.create(pokemon_name, level, status, hp_min + hp_max / 2) # Como tengo el rango de %HP, tomo el valor medio del intervalo #
                success, catch_prob = attempt_catch(pokemon, ball)
                prob.append(catch_prob)
                levels.append(level)

            ax.plot(levels, prob, color=colors[ball], label=ball, marker='o')

        ax.set_title(f"Probabilidad de captura de {pokemon_name}  ({status.name})")
        ax.set_xlabel("Nivel")
        ax.set_ylabel("Probabilidad de captura")
        ax.grid(True)
        ax.legend(loc="upper left", bbox_to_anchor=(1, 1))

        output_dir = "graphs"
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, f"effectiveness_{pokemon_name}_{status.name}.png")
        fig.savefig(output_path, bbox_inches="tight")
        plt.close(fig)  


def main():

    factory = PokemonFactory("pokemon.json")

    with open(f"{sys.argv[1]}", "r") as f:
        config = json.load(f)

    with open('pokeball.json', "r") as c:
        pokeballs = json.load(c).keys()

    status_list = [StatusEffect[status] for status in config["status"]] 

    analyze_effectiveness(factory,config["pokemon"],status_list,config["hp_min"],config["hp_max"],pokeballs)



if __name__ == "__main__":
    main()
