from src.pokemon import Pokemon, StatusEffect, PokemonFactory
from src.catching import attempt_catch
import json
import numpy as np
import matplotlib

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

    for name in pokemon_names:
        plt.figure()
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

            plt.errorbar(levels, avg_prob_by_level, yerr=std_prob_by_level, color=colors[ball], label=ball, marker='o',capsize=5, capthick=1)


        plt.title(f"Probability of catching Pokemon %s " % name)
        plt.xlabel("Level")
        plt.ylabel("Probability")
        plt.grid(True)
        plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
        plt.show()

def analyze_level_and_capture_with_catch_rate(factory, pokeballs, pokemon_names):
    
    for name in pokemon_names:
        plt.figure()
        for ball in pokeballs:
            prob = []
            levels = []

            for level in [1] + list(range(10, 101, 5)):
                pokemon = factory.create(name, level, StatusEffect.NONE, 0.5)
                success, catch_prob = attempt_catch(pokemon, ball)
                prob.append(catch_prob)
                levels.append(level)

            plt.plot(levels, prob, color=colors[ball], label=ball, marker='o')

        plt.title(f"Probability of catching Pokemon %s " % name)
        plt.xlabel("Level")
        plt.ylabel("Probability")
        plt.grid(True)
        plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
        plt.show()


###    Variating HP    ###

def analyze_hp_and_capture_with_catch_rate(factory, pokeballs, pokemon_names):
    for name in pokemon_names:
        plt.figure()
        for ball in pokeballs:
            prob = []
            hps = []

            for hp in range(0, 101, 1):
                pokemon = factory.create(name, 100, StatusEffect.NONE, hp / 100)
                success, catch_prob = attempt_catch(pokemon, ball)
                prob.append(catch_prob)
                hps.append(hp)

            plt.plot(hps, prob, color=colors[ball], label=ball, marker='o')

        plt.title(f"Probability of catching Pokemon %s " % name)
        plt.xlabel("HP %")
        plt.ylabel("Probability")
        plt.grid(True)
        plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
        plt.show()

###    Variating Status    ###

def analyze_status_and_capture_with_catch_rate(factory, pokeballs, pokemon_names):
    for name in pokemon_names:
        plt.figure()
        for ball in pokeballs:
            prob = []
            statuses = []

            for status in StatusEffect:
                pokemon = factory.create(name, 100, status, 0.5)
                success, catch_prob = attempt_catch(pokemon, ball)
                prob.append(catch_prob)
                statuses.append(status.name)

            plt.plot(statuses, prob, color=colors[ball], label=ball, marker='o')
        
        plt.title(f"Probability of catching Pokemon %s " % name)
        plt.xlabel("Status")
        plt.ylabel("Probability")
        plt.grid(True)
        plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
        plt.show()

def main():

    factory = PokemonFactory("pokemon.json")
    pokeballs = ["pokeball", "fastball", "ultraball", "heavyball"]

    with open("pokemon.json", "r") as f:
        pokemon_names = json.load(f)

    #analyze_level_and_capture(factory, pokeballs, pokemon_names)
    analyze_level_and_capture_with_catch_rate(factory, pokeballs, pokemon_names)
    

if __name__ == "__main__":
    main()
