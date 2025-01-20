#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 10:36:04 2025

@author: fcvmathieu
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


# Load the dataset
file_path = 'df.csv'  # Ensure this file is in the same directory or provide the correct path
data = pd.read_csv(file_path)

# Convert the "Date" column to datetime format for easier filtering
data['Date'] = pd.to_datetime(data['Date'], errors='coerce')

# Retain the "Date" column temporarily for filtering
data_filtered = data[['Date'] + list(data.columns[4:])]

# Streamlit app
st.title("Wellness - FC Versailles")

# Sidebar for navigation
st.sidebar.title("Choisir")
page = st.sidebar.radio("", ["Equipe", "Joueurs","Medical"])

if page == "Equipe":
    st.header("État de l'équipe")
    
    # Define the full list of players
    all_players = [
        "Hend", "Raux-Yao", "Moussadek", "Guirassy","Odzoumo", 
        "Mbemba", "Ben Brahim", "Santini", "Kodjia", "Mendes", "M'bone", 
        "Mbala", "Chadet", "Diakhaby", "Altikulac", "Duku", "Mahop", 
        "Calvet", "Basque", "Tchato", "Baghdadi", "Renot", "Renaud", 
        "Raux", "Traoré"
    ]

    # Date selection
    date_min = data['Date'].min()
    date_max = data['Date'].max()
    selected_date = st.sidebar.date_input(
        "Choisir la date:", 
        min_value=date_min, 
        max_value=date_max
    )

    # Filter data by the selected date
    filtered_data = data[data['Date'] == pd.Timestamp(selected_date)]

    # Get the list of players who filled the questionnaire
    players_filled = filtered_data['Nom'].dropna().unique()
    players_not_filled = list(set(all_players) - set(players_filled))

    # Drop unnecessary columns for display
    columns_to_display = ['Nom', 'Sommeil', 'Fatigue', 'Courbature', 'Humeur']
    filtered_data_display = filtered_data[columns_to_display]

    # Display the filtered data
    if not filtered_data_display.empty:
        st.write(f"{selected_date}")
        st.dataframe(filtered_data_display)

        # Calculate averages for the selected date
        averages = filtered_data.groupby('Nom')[['Sommeil', 'Fatigue', 'Courbature', 'Humeur']].mean()
        averages.reset_index(inplace=True)

        st.write("### Moyenne des scores")
        st.dataframe(averages)

        # List players with scores above 5 in specific columns
        high_scores = filtered_data[(filtered_data['Sommeil'] > 5) | 
                                     (filtered_data['Fatigue'] > 5) | 
                                     (filtered_data['Courbature'] > 5) | 
                                     (filtered_data['Humeur'] > 5)]
        if not high_scores.empty:
            st.write("Joueurs avec des scores supérieurs à 5:")
            for index, row in high_scores.iterrows():
                st.write(f"- {row['Nom']}: Sommeil {row['Sommeil']} - Fatigue {row['Fatigue']} - Courbature {row['Courbature']} - Humeur {row['Humeur']}")
        else:
            st.write("Aucun joueur avec des scores élevés pour aujourd'hui.")
    else:
        st.write(f"Aucune donnée disponible pour le {selected_date}.")

    # Display players who did not fill the questionnaire
    st.write(f"Joueurs n'ayant pas rempli le questionnaire le {selected_date}:")
    if players_not_filled:
        for player in sorted(players_not_filled):
            st.write(f"- {player}")
    else:
        st.write("Tous les joueurs ont rempli le questionnaire.")



elif page == "Joueurs":
    st.header("Joueur")
    
    # Sort names alphabetically
    sorted_names = sorted(data['Nom'].dropna().unique())
    selected_name = st.sidebar.selectbox("Choisir un nom:", options=sorted_names, index=0)

    # Filter data for the selected player
    data_filtered_by_name = data[data['Nom'] == selected_name]

    # Ensure the Date column is sorted and retains datetime format
    data_filtered_by_name = data_filtered_by_name.sort_values(by='Date')
    data_filtered_by_name['Date'] = pd.to_datetime(data_filtered_by_name['Date'], errors='coerce')

    # Calculate metrics
    if not data_filtered_by_name.empty:
        # Value of the most recent date
        latest_date = data_filtered_by_name['Date'].max()
        latest_values = data_filtered_by_name[data_filtered_by_name['Date'] == latest_date]

        # Mean of all available data
        mean_values = data_filtered_by_name[['Sommeil', 'Fatigue', 'Courbature', 'Humeur']].mean()

        # Mean of the last 3 days
        last_three_days = data_filtered_by_name.tail(3)
        last_three_mean = last_three_days[['Sommeil', 'Fatigue', 'Courbature', 'Humeur']].mean()

        # Create a summary table
        summary_table = pd.DataFrame({
            'Metric': ['Valeur du jour', 'Moyenne', 'Moyenne des 3 derniers jours'],
            'Sommeil': [
                latest_values['Sommeil'].values[0] if not latest_values.empty else "N/A",
                mean_values['Sommeil'],
                last_three_mean['Sommeil']
            ],
            'Fatigue': [
                latest_values['Fatigue'].values[0] if not latest_values.empty else "N/A",
                mean_values['Fatigue'],
                last_three_mean['Fatigue']
            ],
            'Courbature': [
                latest_values['Courbature'].values[0] if not latest_values.empty else "N/A",
                mean_values['Courbature'],
                last_three_mean['Courbature']
            ],
            'Humeur': [
                latest_values['Humeur'].values[0] if not latest_values.empty else "N/A",
                mean_values['Humeur'],
                last_three_mean['Humeur']
            ]
        })

        # Display the summary table
        st.write(f"### Résumé pour {selected_name}")
        st.table(summary_table)

        # Graphique interactif
        st.write("### Métriques de Santé")
        variable = st.selectbox("Choisir la variable:", ["Sommeil", "Fatigue", "Courbature", "Humeur"])

        fig, ax = plt.subplots()
        ax.plot(data_filtered_by_name['Date'], data_filtered_by_name[variable], marker='o', linestyle='-')
        ax.set_title(f"{variable}")
        ax.set_xlabel("Date")
        ax.set_ylabel(variable)
        ax.grid(True)
        # Supprimer les axes supérieurs et droits
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        # Définir la plage de l'axe Y
        ax.set_ylim(1, 7)
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.write(f"Aucune donnée disponible pour {selected_name}.")
        
        
        
if page == "Medical":
    st.header("Analyse des Douleurs")

    # Date selection
    date_min = data['Date'].min()
    date_max = data['Date'].max()
    selected_date = st.sidebar.date_input(
        "Choisir une date:", 
        min_value=date_min, 
        max_value=date_max
    )

    # Filter data by the selected date
    filtered_data = data[data['Date'] == pd.Timestamp(selected_date)]

    # Further filter for players who reported "Oui" for "Douleurs"
    players_with_pain = filtered_data[filtered_data['Douleurs'] == "Oui"]

    # Display an overview
    if not players_with_pain.empty:
        st.write(f"### Joueurs ayant signalé des douleurs le {selected_date.strftime('%d-%m-%Y')}")
        
        # Display a table of players and details
        columns_to_display = [
            'Nom', 'Identifie l\'emplacement de la douleur', 'Intensité de la douleur'
        ]
        st.dataframe(players_with_pain[columns_to_display])

        # Display pain intensity distribution
        st.write("### Distribution de l'intensité des douleurs")
        fig, ax = plt.subplots()
        ax.hist(players_with_pain['Intensité de la douleur'].dropna(), bins=range(1, 11), edgecolor='black')
        ax.set_title("Distribution de l'intensité des douleurs")
        ax.set_xlabel("Intensité de la douleur")
        ax.set_ylabel("Nombre de joueurs")
        ax.grid(True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        st.pyplot(fig)
    else:
        st.write(f"Aucun joueur n'a signalé de douleurs le {selected_date.strftime('%d-%m-%Y')}.")

