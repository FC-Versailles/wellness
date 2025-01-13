#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 10:36:04 2025

@author: fcvmathieu
"""

import streamlit as st
import pandas as pd

# Load the dataset
file_path = 'df.csv'  # Ensure this file is in the same directory or provide the correct path
data = pd.read_csv(file_path)

# Convert the "Date" column to datetime format for easier filtering
data['Date'] = pd.to_datetime(data['Date'], errors='coerce')

# Retain the "Date" column temporarily for filtering
data_filtered = data[['Date'] + list(data.columns[4:])]

# Streamlit app
st.title("Wellness - FC Versailles")

# Date selection
selected_date = st.date_input(
    "Choose a date to filter the table:", 
    min_value=data['Date'].min(), 
    max_value=data['Date'].max()
)

# Filter data by the selected date
filtered_data = data_filtered[data_filtered['Date'] == pd.Timestamp(selected_date)]

# Drop the "Date" column for display if you want
filtered_data = filtered_data.drop(columns=['Date'])

# Display the filtered data
if not filtered_data.empty:
    st.write(f"Data for {selected_date}:")
    st.dataframe(filtered_data)
else:
    st.write(f"No data available for {selected_date}.")
