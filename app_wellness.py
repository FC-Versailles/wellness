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
page = st.sidebar.radio("", ["Team", "Joueurs"])

if page == "Team":
    st.header("État de l'équipe")
    
    # Define the full list of players
    all_players = [
        "Agoro", "Hend", "Raux-Yao", "Moussadek", "Guirrassy", 
        "Mbemba", "Ben Brahim", "Santini", "Kodjia", "Mendes", "M'bone", 
        "Mbala", "Chadet", "Diakhaby", "Altikulac", "Duku", "Mahop", 
        "Calvet", "Basque", "Tchato", "Baghdadi", "Renot", "Renaud", 
        "Raux", "Dabana", "Traoré"
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
    columns_to_display = ['Nom', 'Sommeil', 'Fatigue', 'Courbature', 'Humeur', 'Douleurs', 
                           'Identifie l\'emplacement de la douleur', 'Intensité de la douleur']
    filtered_data_display = filtered_data[columns_to_display]

    # Display the filtered data
    if not filtered_data_display.empty:
        st.write(f"Data for {selected_date}:")
        st.dataframe(filtered_data_display)

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
    
    # Dropdown to select "Nom"
    names = data['Nom'].dropna().unique()
    selected_name = st.sidebar.selectbox("Choisir un nom:", options=names, index=0)

    # Filter data by the selected name
    data_filtered_by_name = data[data['Nom'] == selected_name]
    
    # Format the "Date" column as dd-mm-yy for display
    data_filtered_by_name['Date'] = data_filtered_by_name['Date'].dt.strftime('%d-%m-%y')

    # Drop unnecessary columns for display
    columns_to_display = ['Date', 'Sommeil', 'Fatigue', 'Courbature', 'Humeur', 'Douleurs', 
                           'Identifie l\'emplacement de la douleur', 'Intensité de la douleur']
    filtered_data_display = data_filtered_by_name[columns_to_display]

    # Display the filtered data
    if not filtered_data_display.empty:
        st.write(f"{selected_name}:")
        st.dataframe(filtered_data_display)

        # Interactive plot
        st.write("### Métriques de Santé")
        variable = st.selectbox("Choisir la variable:", ["Sommeil", "Fatigue", "Courbature", "Humeur"])

        fig, ax = plt.subplots()
        ax.plot(data_filtered_by_name['Date'], data_filtered_by_name[variable], marker='o', linestyle='-')
        ax.set_title(f"{variable}")
        ax.set_xlabel("Date")
        ax.set_ylabel(variable)
        ax.grid(True)
        # Remove top and right axes
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        # Set y-axis range
        ax.set_ylim(1, 7)
        plt.xticks(rotation=90)
        st.pyplot(fig)
    else:
        st.write(f"No data available for {selected_name}.")
