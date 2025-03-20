import json
import sys

from src.catching import attempt_catch
from src.pokemon import PokemonFactory, StatusEffect
from src.utils import average_probability_of_capture, pokeball_effectiveness, \
    analyze_health_and_capture, analyze_hp_and_capture, analyze_level_and_capture, \
    analyze_level_and_capture_with_capture_rate, analyze_hp_and_capture_with_capture_rate, \
    analyze_status_and_capture_with_capture_rate

if __name__ == "__main__":

    # Ex: 1a
    average_probability_of_capture()
    
    # Ex: 1b
    pokeball_effectiveness()

    with open('pokemon.json', "r") as c:
        pokemon_names = json.load(c).keys()   

    with open('pokeball.json', "r") as c:
        pokeballs = json.load(c).keys()
    
    factory = PokemonFactory("pokemon.json")

    for pokemon in pokemon_names:
        # Ex: 2a
        analyze_health_and_capture(factory, pokeballs, pokemon)
        # Ex: 2b
        analyze_hp_and_capture(factory, pokeballs, pokemon)

    # Ex: 2c
    analyze_level_and_capture(factory, pokeballs, pokemon_names)
    analyze_level_and_capture_with_capture_rate(factory, pokeballs, pokemon_names)
    analyze_hp_and_capture_with_capture_rate(factory, pokeballs, pokemon_names)
    analyze_status_and_capture_with_capture_rate(factory, pokeballs, pokemon_names)

    # Ex: 2d and 2e are in ./all_combination_of_properties_generator.py and ./visualize_best_combination_of_properties.py

