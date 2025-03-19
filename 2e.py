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

import os
import numpy as np
import matplotlib.pyplot as plt

def analyze_effectiveness(factory, pokemon_name, status_list, hp_min, hp_max, pokeballs):

    hp_values = np.linspace(hp_min, hp_max, 5)

    for status in status_list:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for ball in pokeballs:
            levels = [1] + list(range(10, 101, 5))
            mean_probs = []
            std_devs = []

            for level in levels:
                catch_probs = []

                for hp in hp_values:
                    pokemon = factory.create(pokemon_name, level, status, hp)  
                    success, catch_prob = attempt_catch(pokemon, ball)
                    catch_probs.append(catch_prob)

                mean_prob = np.mean(catch_probs)  # Promedio de las probabilidades
                std_dev = np.std(catch_probs)  # Desviación estándar

                mean_probs.append(mean_prob)
                std_devs.append(std_dev)
                print(f"Nivel {level} - {ball}: std_dev = {std_dev}")


            # Graficar con barras de error
            ax.errorbar(levels, mean_probs, yerr=np.array(std_devs), fmt='-o', color=colors[ball], label=ball, capsize=5)

        ax.set_title(f"Probabilidad de captura de {pokemon_name} ({status.name})")
        ax.set_xlabel("Nivel")
        ax.set_ylabel("Probabilidad de captura")
        ax.grid(True)
        ax.legend(loc="upper left", bbox_to_anchor=(1, 1))

        output_dir = "graphs"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"effectiveness_{pokemon_name}_{status.name}.png")
        fig.savefig(output_path, bbox_inches="tight")
        plt.show()
        plt.close(fig)
  


def main():

    factory = PokemonFactory("pokemon.json")

# Recibe como argumento el archivo de configuración
    with open(f"{sys.argv[1]}", "r") as f:
        config = json.load(f)

    with open('pokeball.json', "r") as c:
        pokeballs = json.load(c).keys()

    status_list = [StatusEffect[status] for status in config["status"]] 

    analyze_effectiveness(factory,config["pokemon"],status_list,config["hp_min"],config["hp_max"],pokeballs)



if __name__ == "__main__":
    main()
