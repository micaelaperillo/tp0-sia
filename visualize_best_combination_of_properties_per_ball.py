import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch
import matplotlib.colors as mcolors


def parse_pokemon_file(file_path):
    data = []
    with open(file_path, 'r') as file:
        entry = {}
        for line in file:
            line = line.strip()
            
            if line.startswith("Pokemon:"):
                entry["Pokemon"] = line.split("Pokemon:")[1].strip()
            elif line.startswith("Pokeball:"):
                entry["Pokeball"] = line.split("Pokeball:")[1].strip()
            elif line.startswith("Level:"):
                entry["Level"] = int(line.split("Level:")[1].strip())
            elif line.startswith("Status:"):
                entry["Status"] = line.split("Status:")[1].strip().lower()
            elif line.startswith("HP:"):
                entry["HP"] = float(line.split("HP:")[1].strip()) / 100  # Convert to proportion
            elif line.startswith("CaptureRate:"):
                entry["CaptureRate"] = float(line.split("CaptureRate:")[1].strip())
            elif line.startswith("---------"):
                if entry:  # Only append if entry is not empty
                    data.append(entry.copy())
                    entry = {}
    
    # Adds the last entry if file doesn't end with dashes
    if entry:
        data.append(entry)
    
    return pd.DataFrame(data)

def create_capture_rate_heatmaps(df1, df2, pokemon1, pokemon2, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    pokeball_types = ["pokeball", "ultraball", "fastball", "heavyball"]
    status_names = ["none", "burn", "freeze", "poison", "paralysis", "sleep"]
    
    fixed_level = 50
    
    def create_heatmap_for_pokemon(df, pokemon_name, pokeball, cmap):
        filtered_df = df[(df['Pokeball'] == pokeball) & (df['Level'] == fixed_level)]
        
        if filtered_df.empty:
            print(f"No data available for {pokemon_name} with {pokeball} at level {fixed_level}")
            return
        
        hp_values = sorted(filtered_df['HP'].unique())
        
        # If there are too many HP values, bin them for better visualization
        if len(hp_values) > 20:
            hp_bins = np.linspace(min(hp_values), max(hp_values), 20)
            hp_labels = [f"{hp_bins[i]:.2f}-{hp_bins[i+1]:.2f}" for i in range(len(hp_bins)-1)]
            filtered_df['HP_binned'] = pd.cut(filtered_df['HP'], bins=hp_bins, labels=hp_labels)
            hp_column = 'HP_binned'
        else:
            # If there aren't too many HP values, use them directly
            hp_column = 'HP'
        
        # Create a pivot table: status vs HP with capture rate as values
        pivot = filtered_df.pivot_table(
            index='Status', 
            columns=hp_column, 
            values='CaptureRate',
            aggfunc='mean'
        )
        
        # Reorder the index to match the status_names order
        pivot = pivot.reindex(status_names)
        
        # Create the heatmap
        plt.figure(figsize=(14, 8))
        ax = sns.heatmap(
            pivot, 
            cmap= cmap, 
            annot=True,  
            fmt=".3f",   
            linewidths=0.5,
            cbar_kws={'label': 'Precisión de captura'}
        )
        
        plt.title(f'Precisión de captura para {pokemon_name}\nNivel: {fixed_level}, Pokeball: {pokeball.capitalize()}', fontsize=16)
        plt.xlabel('HP %', fontsize=14)
        plt.ylabel('Estado', fontsize=14)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        filename = f"{output_dir}/{pokemon_name.lower()}_nivel_{fixed_level}_{pokeball}_capture_rate_heatmap.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
    
    # Generate heatmaps for all pokeball types for both Pokemon
    for pokeball in pokeball_types:
        create_heatmap_for_pokemon(df1, pokemon1, pokeball, "YlGnBu")
        create_heatmap_for_pokemon(df2, pokemon2, pokeball, "YlOrBr")

def create_bar_plot_for_pokemon_prices(output_directory):
    prices = {
        'pokeball': 200,
        'ultraball': 1200,
        'heavyball': 500,
        'fastball': 500
    }

    base_price = prices['pokeball']
    equivalent_pokeballs = {k: v / base_price for k, v in prices.items()}

    labels = list(equivalent_pokeballs.keys())
    values = list(equivalent_pokeballs.values())

    plt.figure(figsize=(8, 6))
    bars = plt.bar(labels, values, color=['red', 'orange', 'blue', 'green'])

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 0.1,
                 f'{height:.1f}', ha='center', va='bottom')

    plt.title('Relación de precio de pokeballs especiales respecto de la pokeball básica')
    plt.ylabel('Cantidad de pokeballs básicas equivalentes')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    os.makedirs(output_directory, exist_ok=True)

    output_path = os.path.join(output_directory, 'precios_relativos_de_pokeballs.png')
    plt.savefig(output_path)
    plt.close()

def group_hp_by_capture_rate(df, num_groups=10):
    pokeball_prices = {
        "pokeball": 200,
        "ultraball": 1200,
        "fastball": 500,
        "heavyball": 500
    }
    
    df_copy = df.copy()
    df_copy['Efficiency'] = df_copy.apply(lambda row: row['CaptureRate'] / pokeball_prices[row['Pokeball']], axis=1)
    
    hp_values = sorted(df_copy['HP'].unique())
    
    # If there are few HP values, return them as is
    if len(hp_values) <= num_groups:
        return {hp: f"{hp:.2f}" for hp in hp_values}
    
    hp_bins = np.linspace(min(hp_values), max(hp_values), num_groups + 1)
    hp_groups = {}
    
    for hp in hp_values:
        # Find which bin this HP value belongs to
        for i in range(len(hp_bins) - 1):
            if hp_bins[i] <= hp <= hp_bins[i+1]:
                group_label = f"{hp_bins[i]:.2f}-{hp_bins[i+1]:.2f}"
                hp_groups[hp] = group_label
                break
    
    return hp_groups

def create_efficiency_heatmaps(df1, df2, pokemon1, pokemon2, output_dir):
    def create_efficiency_heatmap(df, pokemon_name, output_dir, fixed_level=50, num_hp_groups=10):
        os.makedirs(output_dir, exist_ok=True)

        pokeball_prices = {
            "pokeball": 200,
            "ultraball": 1200,
            "fastball": 500,
            "heavyball": 500
        }

        pokeball_colors = {
            "pokeball": "red",
            "ultraball": "orange",
            "fastball": "green",
            "heavyball": "blue"
        }

        status_names = ["sleep", "paralysis", "poison", "freeze", "burn", "none"]

        filtered_df = df[df['Level'] == fixed_level]

        if filtered_df.empty:
            print(f"No data available for {pokemon_name} at level {fixed_level}")
            return

        hp_groups = group_hp_by_capture_rate(filtered_df, num_hp_groups)
        filtered_df['HP_Group'] = filtered_df['HP'].map(hp_groups)

        hp_group_labels = sorted(set(hp_groups.values()), 
                                key=lambda x: float(x.split('-')[0]) if '-' in x else float(x))

        best_pokeball_data = []

        for status in status_names:
            for hp_group in hp_group_labels:
                combo_df = filtered_df[(filtered_df['HP_Group'] == hp_group) & (filtered_df['Status'] == status)]

                if combo_df.empty:
                    continue

                best_efficiency_by_ball = {}

                # Find the most cost-effective ball for each pokeball type
                for pokeball in pokeball_prices.keys():
                    ball_df = combo_df[combo_df['Pokeball'] == pokeball]
                    if not ball_df.empty:
                        avg_capture_rate = ball_df['CaptureRate'].mean()
                        efficiency = avg_capture_rate / pokeball_prices[pokeball]
                        best_efficiency_by_ball[pokeball] = {
                            'efficiency': efficiency,
                            'capture_rate': avg_capture_rate
                        }

                if best_efficiency_by_ball:
                    # Find the ball with the highest efficiency
                    best_ball = max(best_efficiency_by_ball.items(), 
                                    key=lambda x: x[1]['efficiency'])

                    best_pokeball_data.append({
                        'Status': status,
                        'HP_Group': hp_group,
                        'BestPokeball': best_ball[0],
                        'Efficiency': best_ball[1]['efficiency'],
                        'CaptureRate': best_ball[1]['capture_rate']
                    })

        best_df = pd.DataFrame(best_pokeball_data)

        pokeball_pivot = best_df.pivot_table(
            index='Status',
            columns='HP_Group',
            values='BestPokeball',
            aggfunc=lambda x: x.iloc[0] if len(x) > 0 else None
        )

        efficiency_pivot = best_df.pivot_table(
            index='Status',
            columns='HP_Group',
            values='Efficiency',
            aggfunc='first'
        )

        pokeball_pivot = pokeball_pivot.reindex(status_names)
        efficiency_pivot = efficiency_pivot.reindex(status_names)

        pokeball_pivot = pokeball_pivot.reindex(columns=hp_group_labels)
        efficiency_pivot = efficiency_pivot.reindex(columns=hp_group_labels)

        pokeball_cmap = {}
        for pokeball, color in pokeball_colors.items():
            pokeball_cmap[pokeball] = color

        # Create a 2D array of colors based on the best pokeball
        cell_colors = np.zeros((len(pokeball_pivot), len(pokeball_pivot.columns), 3))
        for i, status in enumerate(pokeball_pivot.index):
            for j, hp_group in enumerate(pokeball_pivot.columns):
                if pd.isna(pokeball_pivot.iloc[i, j]):
                    cell_colors[i, j] = mcolors.to_rgb('lightgray')
                else:
                    base_color = mcolors.to_rgb(pokeball_cmap[pokeball_pivot.iloc[i, j]])
                    efficiency = efficiency_pivot.iloc[i, j]

                    # Scale the efficiency to get color intensity
                    # Normalize the efficiency for better visualization
                    max_efficiency = efficiency_pivot.max().max()
                    intensity = min(1.0, efficiency / (max_efficiency * 0.7))

                    # Blend with white based on intensity
                    white = mcolors.to_rgb('white')
                    blended_color = tuple(base * intensity + white[i] * (1 - intensity) for i, base in enumerate(base_color))
                    cell_colors[i, j] = blended_color

        fig, ax = plt.subplots(figsize=(14, 8))

        # Calculate max efficiency for normalization
        max_efficiency = efficiency_pivot.max().max()

        # Draw each cell manually
        for i in range(len(pokeball_pivot.index)):
            for j in range(len(pokeball_pivot.columns)):
                if not pd.isna(pokeball_pivot.iloc[i, j]):
                    ball_type = pokeball_pivot.iloc[i, j]
                    base_color = mcolors.to_rgb(pokeball_colors[ball_type])

                    efficiency = efficiency_pivot.iloc[i, j]
                    intensity = min(1.0, efficiency / (max_efficiency * 0.7))

                    # Blend with white based on intensity
                    white = mcolors.to_rgb('white')
                    color = tuple(base * intensity + white[i] * (1 - intensity) for i, base in enumerate(base_color))

                    # Draw rectangle with white edgecolor (border)
                    rect = plt.Rectangle((j, i), 1, 1, facecolor=color, edgecolor='white', linewidth=1)
                    ax.add_patch(rect)

                    # Add text for efficiency value
                    efficiency_value = efficiency_pivot.iloc[i, j] * 100
                    ax.text(j + 0.5, i + 0.5, f"{efficiency_value:.3f}", 
                           ha="center", va="center", fontweight='bold')

        # Set limits and labels
        ax.set_xlim(0, len(pokeball_pivot.columns))
        ax.set_ylim(0, len(pokeball_pivot.index))

        ax.set_xticks(np.arange(len(pokeball_pivot.columns)) + 0.5)
        ax.set_yticks(np.arange(len(pokeball_pivot.index)) + 0.5)

        ax.set_xticklabels(pokeball_pivot.columns)
        ax.set_yticklabels(pokeball_pivot.index)

        plt.xticks(rotation=45, ha='right')

        plt.title(f'Pokebola más eficiente para capturar a {pokemon_name} (Nivel {fixed_level})', fontsize=16)
        plt.xlabel('HP %', fontsize=14)
        plt.ylabel('Estado', fontsize=14)

        # Create legend for pokeball types
        legend_elements = []
        for pokeball, color in pokeball_colors.items():
            legend_elements.append(Patch(facecolor=color, edgecolor='k', 
                                  label=f"{pokeball.capitalize()} (₽{pokeball_prices[pokeball]})"))

        plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left', 
                  title="Tipos de pokeball")

        plt.tight_layout()

        filename = f"{output_dir}/mejor_pokebola_para_{pokemon_name.lower()}_heatmap.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

    create_efficiency_heatmap(df1, pokemon1, output_dir, num_hp_groups=19)
    create_efficiency_heatmap(df2, pokemon2, output_dir, num_hp_groups=19)

def create_std_dev_heatmaps(df1, df2, pokemon1, pokemon2, output_dir):
    def create_std_dev_heatmap(df, pokemon_name, output_dir, num_hp_groups=19, cmap="YlGrBu"):
        os.makedirs(output_dir, exist_ok=True)
 
        pokeball_colors = {
            "pokeball": "red",
            "ultraball": "yellow",
            "fastball": "green",
            "heavyball": "blue"
        }
 
        status_names = ["none", "burn", "freeze", "poison", "paralysis", "sleep"]
 
        filtered_df = df[(df['Level'] >= 1) & (df['Level'] <= 100)]
 
        if filtered_df.empty:
            print(f"No data available for {pokemon_name} at levels 1-50")
            return
 
        filtered_df = filtered_df.copy()
 
        hp_groups = group_hp_by_capture_rate(filtered_df, num_hp_groups)
        filtered_df['HP_Group'] = filtered_df['HP'].map(hp_groups)
 
        hp_group_labels = sorted(set(hp_groups.values()), 
                                key=lambda x: float(x.split('-')[0]) if '-' in x else float(x))
 
        std_dev_data = []
 
        for pokeball in pokeball_colors.keys():
            for status in status_names:
                for hp_group in hp_group_labels:
                    combo_df = filtered_df[(filtered_df['HP_Group'] == hp_group) & 
                                          (filtered_df['Status'] == status) &
                                          (filtered_df['Pokeball'] == pokeball)]
 
                    if not combo_df.empty and len(combo_df) > 1:  # Need at least 2 points for std dev
                        mean = combo_df['CaptureRate'].mean()
                        std_dev = combo_df['CaptureRate'].std()
 
                        std_dev_data.append({
                            'Pokeball': pokeball,
                            'Status': status,
                            'HP_Group': hp_group,
                            'StdDev': std_dev,
                            'Mean' : mean
                        })
 
        std_dev_df = pd.DataFrame(std_dev_data)
 
        # Create separate heatmaps for each pokeball type
        for pokeball in pokeball_colors.keys():
            pokeball_data = std_dev_df[std_dev_df['Pokeball'] == pokeball]
 
            if pokeball_data.empty:
                print(f"No data available for {pokeball}")
                continue
            
            std_dev_pivot = pokeball_data.pivot_table(
                index='Status',
                columns='HP_Group',
                values='StdDev',
                aggfunc='first'
            )
 
            std_dev_pivot = std_dev_pivot.reindex(status_names)
            std_dev_pivot = std_dev_pivot.reindex(columns=hp_group_labels)
 
            plt.figure(figsize=(14, 8))
 
            # Create a mask for missing values
            mask = pd.isna(std_dev_pivot)
 
            ax = sns.heatmap(
                std_dev_pivot,
                cmap=cmap,
                annot=True,
                fmt=".4f",
                mask=mask,
                cbar=True,
                cbar_kws={'label': 'Desviación estándar de la precisión de captura'},
                linewidths=1,
                linecolor='white',
            )
 
            plt.xticks(rotation=45, ha='right')
 
            plt.title(f'Desviación estándar de la precisión de captura para {pokemon_name}\n  {pokeball.capitalize()} - Niveles: 1-100', fontsize=16)
            plt.xlabel('HP %', fontsize=14)
            plt.ylabel('Estado', fontsize=14)
 
            plt.tight_layout()
 
            filename = f"{output_dir}/{pokemon_name.lower()}_{pokeball}_std_dev_heatmap.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
 
    create_std_dev_heatmap(df1, pokemon1, output_dir, 19, "YlGnBu")
    create_std_dev_heatmap(df2, pokemon2, output_dir, 19, "YlOrBr")

def create_mean_std_dev_heatmaps(df1, df2, pokemon1, pokemon2, output_dir, first_level=1, last_level=100):
    # Function to create and return both the heatmap and the calculated data
    def create_std_dev_heatmap(df, pokemon_name, output_dir, num_hp_groups=19, cmap="YlGrBu"):
        os.makedirs(output_dir, exist_ok=True)
        pokeball_colors = {
            "pokeball": "red",
            "ultraball": "yellow",
            "fastball": "green",
            "heavyball": "blue"
        }
        status_names = ["none", "burn", "freeze", "poison", "paralysis", "sleep"]
        
        filtered_df = df[(df['Level'] >= first_level) & (df['Level'] <= last_level)]
        if filtered_df.empty:
            print(f"No data available for {pokemon_name} at levels 1-50")
            return None
        
        filtered_df = filtered_df.copy()
        hp_groups = group_hp_by_capture_rate(filtered_df, num_hp_groups)
        filtered_df['HP_Group'] = filtered_df['HP'].map(hp_groups)
        hp_group_labels = sorted(set(hp_groups.values()), key=lambda x: float(x.split('-')[0]) if '-' in x else float(x))
        
        std_dev_data = []
        for pokeball in pokeball_colors.keys():
            for status in status_names:
                for hp_group in hp_group_labels:
                    combo_df = filtered_df[(filtered_df['HP_Group'] == hp_group) & 
                                         (filtered_df['Status'] == status) & 
                                         (filtered_df['Pokeball'] == pokeball)]
                    if not combo_df.empty and len(combo_df) > 1:  # Need at least 2 points for std dev
                        mean = combo_df['CaptureRate'].mean()
                        std_dev = combo_df['CaptureRate'].std()
                        std_dev_data.append({
                            'Pokeball': pokeball,
                            'Status': status,
                            'HP_Group': hp_group,
                            'StdDev': std_dev,
                            'Mean': mean
                        })
        
        std_dev_df = pd.DataFrame(std_dev_data)
        
        # Create separate heatmaps for each pokeball type
        for pokeball in pokeball_colors.keys():
            pokeball_data = std_dev_df[std_dev_df['Pokeball'] == pokeball]
            if pokeball_data.empty:
                print(f"No data available for {pokeball}")
                continue
                
            mean_pivot = pokeball_data.pivot_table(
                index='Status', 
                columns='HP_Group', 
                values='Mean', 
                aggfunc='first'
            )
            mean_pivot = mean_pivot.reindex(status_names)
            mean_pivot = mean_pivot.reindex(columns=hp_group_labels)
            
            std_dev_pivot = pokeball_data.pivot_table(
                index='Status', 
                columns='HP_Group', 
                values='StdDev', 
                aggfunc='first'
            )
            std_dev_pivot = std_dev_pivot.reindex(status_names)
            std_dev_pivot = std_dev_pivot.reindex(columns=hp_group_labels)
            
            # Combine mean and std dev in the format "mean\n±\nstd_dev"
            combined_pivot = pd.DataFrame(index=mean_pivot.index, columns=mean_pivot.columns)
            for idx in mean_pivot.index:
                for col in mean_pivot.columns:
                    if not pd.isna(mean_pivot.loc[idx, col]) and not pd.isna(std_dev_pivot.loc[idx, col]):
                        combined_pivot.loc[idx, col] = f"{mean_pivot.loc[idx, col]:.4f}\n±\n{std_dev_pivot.loc[idx, col]:.4f}"
            
            plt.figure(figsize=(18, 10))  
            
            mask = combined_pivot.isna()
            
            def annotate_heatmap(data, color_data, **kws):
                yd, xd = np.meshgrid(np.arange(data.shape[0]) + 0.5, np.arange(data.shape[1]) + 0.5)
                for y, x, val, color_val in zip(xd.flatten(), yd.flatten(), data.values.flatten(), color_data.values.flatten()):
                    if not pd.isna(val):
                        kws['color'] = 'white' if color_val < mean_pivot.values.flatten().max() / 2 else 'black'
                        plt.text(y, x, val, ha="center", va="center", **kws)
            
            # Use standard heatmap with std_dev values for color but without annotations
            ax = sns.heatmap(
                mean_pivot,
                cmap=cmap,
                annot=False,
                mask=mask,
                cbar=True,
                cbar_kws={'label': 'Media de la precisión de captura'},
                linewidths=1,
                linecolor='white',
            )
            
            # Add custom annotations with both mean and std_dev in multiline format
            annotate_heatmap(combined_pivot, mean_pivot, fontsize=8)
            
            plt.xticks(rotation=45, ha='right')
            plt.title(f'Precisión de captura (media ± desv. estándar) para {pokemon_name}\n {pokeball.capitalize()} - Niveles: {first_level}-{last_level}', fontsize=16)
            plt.xlabel('HP %', fontsize=14)
            plt.ylabel('Estado', fontsize=14)
            plt.tight_layout()
            
            filename = f"{output_dir}/{pokemon_name.lower()}_{pokeball}_niveles_{first_level}-{last_level}_heatmap.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
        
        # Return the DataFrame with the calculated values to use for efficiency calculations
        return std_dev_df
    
    data_df1 = create_std_dev_heatmap(df1, pokemon1, output_dir, 19, "YlGnBu")
    data_df2 = create_std_dev_heatmap(df2, pokemon2, output_dir, 19, "YlOrBr")
    return data_df1, data_df2

def create_efficiency_heatmaps_from_std_dev(std_dev_data1, std_dev_data2, pokemon1, pokemon2, output_dir, first_level=1, last_level=100):
    def create_efficiency_heatmap_from_means(std_dev_data, pokemon_name, output_dir, num_hp_groups=19):
        if std_dev_data is None or std_dev_data.empty:
            print(f"No data available for {pokemon_name}")
            return
            
        os.makedirs(output_dir, exist_ok=True)

        pokeball_prices = {
            "pokeball": 200,
            "ultraball": 1200,
            "fastball": 500,
            "heavyball": 500
        }

        pokeball_colors = {
            "pokeball": "red",
            "ultraball": "orange",
            "fastball": "green",
            "heavyball": "blue"
        }

        status_names = ["sleep", "paralysis", "poison", "freeze", "burn", "none"]
        
        std_dev_data['Efficiency'] = std_dev_data.apply(
            lambda row: row['Mean'] / pokeball_prices[row['Pokeball']], axis=1
        )
        
        hp_group_labels = sorted(set(std_dev_data['HP_Group']), 
                            key=lambda x: float(x.split('-')[0]) if '-' in x else float(x))
        
        best_pokeball_data = []

        for status in status_names:
            for hp_group in hp_group_labels:
                combo_df = std_dev_data[(std_dev_data['HP_Group'] == hp_group) & 
                                      (std_dev_data['Status'] == status)]

                if combo_df.empty:
                    continue

                best_efficiency_by_ball = {}

                for pokeball in pokeball_prices.keys():
                    ball_df = combo_df[combo_df['Pokeball'] == pokeball]
                    if not ball_df.empty:
                        avg_capture_rate = ball_df['Mean'].values[0]
                        efficiency = avg_capture_rate / pokeball_prices[pokeball]
                        best_efficiency_by_ball[pokeball] = {
                            'efficiency': efficiency,
                            'capture_rate': avg_capture_rate
                        }

                if best_efficiency_by_ball:
                    # Find the ball with the highest efficiency
                    best_ball = max(best_efficiency_by_ball.items(), 
                                  key=lambda x: x[1]['efficiency'])

                    best_pokeball_data.append({
                        'Status': status,
                        'HP_Group': hp_group,
                        'BestPokeball': best_ball[0],
                        'Efficiency': best_ball[1]['efficiency'],
                        'CaptureRate': best_ball[1]['capture_rate']
                    })

        best_df = pd.DataFrame(best_pokeball_data)

        pokeball_pivot = best_df.pivot_table(
            index='Status',
            columns='HP_Group',
            values='BestPokeball',
            aggfunc=lambda x: x.iloc[0] if len(x) > 0 else None
        )

        efficiency_pivot = best_df.pivot_table(
            index='Status',
            columns='HP_Group',
            values='Efficiency',
            aggfunc='first'
        )

        pokeball_pivot = pokeball_pivot.reindex(status_names)
        efficiency_pivot = efficiency_pivot.reindex(status_names)

        pokeball_pivot = pokeball_pivot.reindex(columns=hp_group_labels)
        efficiency_pivot = efficiency_pivot.reindex(columns=hp_group_labels)

        fig, ax = plt.subplots(figsize=(14, 8))

        max_efficiency = efficiency_pivot.max().max()

        # Draw each cell manually
        for i in range(len(pokeball_pivot.index)):
            for j in range(len(pokeball_pivot.columns)):
                if not pd.isna(pokeball_pivot.iloc[i, j]):
                    ball_type = pokeball_pivot.iloc[i, j]
                    base_color = mcolors.to_rgb(pokeball_colors[ball_type])

                    efficiency = efficiency_pivot.iloc[i, j]
                    intensity = min(1.0, efficiency / (max_efficiency * 0.7))

                    white = mcolors.to_rgb('white')
                    color = tuple(base * intensity + white[i] * (1 - intensity) for i, base in enumerate(base_color))

                    rect = plt.Rectangle((j, i), 1, 1, facecolor=color, edgecolor='white', linewidth=1)
                    ax.add_patch(rect)

                    efficiency_value = efficiency_pivot.iloc[i, j] * 100
                    ax.text(j + 0.5, i + 0.5, f"{efficiency_value:.3f}", 
                           ha="center", va="center", fontweight='bold')

        ax.set_xlim(0, len(pokeball_pivot.columns))
        ax.set_ylim(0, len(pokeball_pivot.index))

        ax.set_xticks(np.arange(len(pokeball_pivot.columns)) + 0.5)
        ax.set_yticks(np.arange(len(pokeball_pivot.index)) + 0.5)

        ax.set_xticklabels(pokeball_pivot.columns)
        ax.set_yticklabels(pokeball_pivot.index)

        plt.xticks(rotation=45, ha='right')

        plt.title(f'Pokebola más eficiente para capturar a {pokemon_name}\n(Basado en media de niveles {first_level}-{last_level})', fontsize=16)
        plt.xlabel('HP %', fontsize=14)
        plt.ylabel('Estado', fontsize=14)

        legend_elements = []
        for pokeball, color in pokeball_colors.items():
            legend_elements.append(Patch(facecolor=color, edgecolor='k', 
                                  label=f"{pokeball.capitalize()} (₽{pokeball_prices[pokeball]})"))

        plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left', 
                  title="Tipos de pokeball")

        plt.tight_layout()

        filename = f"{output_dir}/mejor_pokebola_para_{pokemon_name.lower()}_niveles_{first_level}-{last_level}_heatmap.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

    create_efficiency_heatmap_from_means(std_dev_data1, pokemon1, output_dir, num_hp_groups=19)
    create_efficiency_heatmap_from_means(std_dev_data2, pokemon2, output_dir, num_hp_groups=19)

# First run ./utils/all_combination_of_properties_generator.py with the same pokemons selected
def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <first_pokemon> <second_pokemon>")
        print("Example: python3 visualize_best_combination_of_properties_per_ball.py snorlax caterpie")
        sys.exit(1)
    
    first_pokemon = sys.argv[1]
    second_pokemon = sys.argv[2]

    file_path1 = f"{first_pokemon}_conditions_combination.txt"
    file_path2 = f"{second_pokemon}_conditions_combination.txt"

    try:
        # Parse the data files
        df1 = parse_pokemon_file(file_path1)
        df2 = parse_pokemon_file(file_path2)

        # Create output directory
        output_dir = "combination_of_properties_graphs"
        os.makedirs(output_dir, exist_ok=True)

        # Create plots
        # 2d
        # in all functions the fixed level is already set
        create_capture_rate_heatmaps(df1,df2,first_pokemon, second_pokemon, output_dir)

        create_bar_plot_for_pokemon_prices(output_dir)
        
        create_efficiency_heatmaps(df1,df2, first_pokemon, second_pokemon, output_dir)

        # 2e
        # fixed for levels 1-100
        create_std_dev_heatmaps(df1, df2, first_pokemon, second_pokemon, output_dir)

        # for the following functions if limits are not passed, the default range is 1-100
        std_dev_data1_low, std_dev_data2_low = create_mean_std_dev_heatmaps(df1, df2, first_pokemon, second_pokemon, output_dir, 1, 50)
        std_dev_data1_high, std_dev_data2_high = create_mean_std_dev_heatmaps(df1, df2, first_pokemon, second_pokemon, output_dir, 51, 100)
        create_efficiency_heatmaps_from_std_dev(std_dev_data1_low, std_dev_data2_low, first_pokemon, second_pokemon, output_dir, 1, 50)
        create_efficiency_heatmaps_from_std_dev(std_dev_data1_high, std_dev_data2_high, first_pokemon, second_pokemon, output_dir, 51, 100)
    
    except Exception as e:
        import traceback
        print(f"Error occurred: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()