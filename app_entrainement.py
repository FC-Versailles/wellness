import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import squarify

# Constants for Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
TOKEN_FILE = 'token.pickle'  # Replace with your credentials file path
SPREADSHEET_ID = '15n4XkQHrUpSPAW61vmR_Rk1kibd5zcmVqgHA40szlPg'  # Replace with your actual Spreadsheet ID
RANGE_NAME = 'Feuille 1'  # Replace with your range name


# Function to get Google Sheets credentials
def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    return creds


# Function to fetch data from Google Sheet
def fetch_google_sheet(spreadsheet_id, range_name):
    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])
    if not values:
        st.error("No data found in the specified range.")
        return pd.DataFrame()
    header = values[0]
    data = values[1:]
    max_columns = len(header)
    adjusted_data = [
        row + [None] * (max_columns - len(row)) if len(row) < max_columns else row[:max_columns]
        for row in data
    ]
    return pd.DataFrame(adjusted_data, columns=header)


# Streamlit cache for loading data
@st.cache_data(ttl=60)
def load_data():
    return fetch_google_sheet(SPREADSHEET_ID, RANGE_NAME)





# Streamlit App
def main():
    

    
    st.title("FC Versailles - Entrainement")
    
    # Add a button to redirect to a URL
    url = "https://tally.so/r/3X1vz4"  # Replace with your desired URL
    if st.button("Collecter la donnée"):
        js = f"window.open('{url}')"
        html = f'<script>{js}</script>'
        st.markdown(html, unsafe_allow_html=True)


    # Load data from Google Sheets
    data = load_data()

    # Check if the data is not empty
    if not data.empty:
        # Remove the first three columns from the DataFrame
        data_trimmed = data.iloc[:, 3:]
        
        
# Display the dataset as a table
        st.write("### Aperçu des données")
        st.dataframe(data_trimmed, use_container_width=True)
        
        # Treemap Visualization
        st.write("### Répartition des activités")
        activity_columns = [f"Temps {i}" for i in range(6) if f"Temps {i}" in data_trimmed.columns]
        if activity_columns:
            activity_data = data_trimmed.melt(
                id_vars=[], 
                value_vars=activity_columns, 
                var_name='Temps', 
                value_name='Activité'
            ).dropna()
            activity_counts = activity_data['Activité'].value_counts()
        
            # Create the labels with updated activity names
           # Create the labels with updated activity names
            labels = [
                f"{label.replace('Situation technique sans opposition', 'Tech sans oppo').replace('Situation technique avec oppostion', 'Tech avec oppo')}\n{count}" 
                for label, count in zip(activity_counts.index, activity_counts.values)
            ]
        
            # Generate the treemap
            fig, ax = plt.subplots(figsize=(12, 8))
            squarify.plot(
                sizes=activity_counts.values, 
                label=labels, 
                alpha=0.8, 
                color=plt.cm.Set3(range(len(activity_counts))),
                text_kwargs={'fontsize': 10}
            )
            plt.title("")
            plt.axis('off')  # Remove axes for a clean look
            plt.tight_layout()
        
            # Display the treemap
            st.pyplot(fig)
            
        else:
            st.warning("No activity columns (Temps 0 to Temps 5) found in the dataset.")

        # Grouped stacked bar plot visualization
        st.write("### Répartition des procédés par type d'entraînement")
        activity_columns = [col for col in data_trimmed.columns if col.startswith('Temps')]
        if activity_columns:
            # Melt data and count occurrences by exercise and type
            melted_data = data.melt(id_vars=["Type"], value_vars=activity_columns, 
                                    var_name="Temps", value_name="Activité").dropna()
            activity_type_counts = melted_data.pivot_table(index="Activité", columns="Type", aggfunc="size", fill_value=0)

            # Create the grouped stacked bar plot
            fig, ax = plt.subplots(figsize=(12, 7))
            activity_type_counts.plot(kind="bar", stacked=True, ax=ax, color=plt.cm.Set3(range(len(activity_type_counts.columns))))

            # Style the plot
            ax.set_ylabel("Nombre d'apparitions")
            ax.set_xticks(range(len(activity_type_counts.index)))
            ax.set_xticklabels(activity_type_counts.index, rotation=45, ha='right')
            ax.legend(title="Type", bbox_to_anchor=(1.05, 1), loc='upper left')
            
            # Remove top and right axes
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            # Adjust layout
            plt.tight_layout()

            # Display the grouped stacked bar plot in Streamlit
            st.pyplot(fig)
        else:
            st.warning("No activity columns found in the dataset.") 

        st.write("### Répartition des procédés par type d'entraînement")
        
        # Ensure 'Type' is preserved during the melting process
        activity_columns = [col for col in data.columns if col.startswith("Temps")]
        activity_data = data.melt(
            id_vars=["Type"], value_vars=activity_columns, var_name="Temps", value_name="Activité"
        ).dropna()
        
        # Remove "Prévention" and "RAS" from the data
        activity_data = activity_data[~activity_data["Activité"].isin(["Prévention", "RAS"])]
        
        # Group data by "Type" and "Activité" to calculate counts
        activity_by_type = activity_data.groupby(['Type', 'Activité']).size().unstack(fill_value=0)
        
        # Generate colors for each activity
        colors = [plt.cm.Set3(i / (len(activity_by_type.columns) - 1)) for i in range(len(activity_by_type.columns))]
        
        # Create the horizontal stacked bar plot
        fig, ax = plt.subplots(figsize=(12, 8))
        activity_by_type.plot(kind='barh', stacked=True, ax=ax, color=colors)
        
        # Style the plot
        ax.set_xlabel("Nombre d'apparitions")

        ax.legend( bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Remove top and right axes
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        
        # Adjust layout
        plt.tight_layout()
        
        # Display the plot in Streamlit
        st.pyplot(fig)

        st.write("### Répartition des procédés par temps d'entraînement")
        if activity_columns:
            # Count occurrences by activity type and time
            activity_type_counts = activity_data.pivot_table(index="Activité", columns="Temps", aggfunc="size", fill_value=0)
        
            # Generate colors for each "Temps" category (columns)
            colors = [plt.cm.Set3(i / (len(activity_type_counts.T.columns) - 1)) for i in range(len(activity_type_counts.T.columns))]
            
            # Create the stacked bar plot
            fig, ax = plt.subplots(figsize=(12, 7))
            activity_type_counts.T.plot(kind="bar", stacked=True, ax=ax, color=colors)
        
            # Style the plot

            ax.set_ylabel("Nombre d'apparitions")

            ax.set_xticks(range(len(activity_type_counts.T.index)))
            ax.set_xticklabels(activity_type_counts.T.index, rotation=45, ha="right")
            ax.legend(title="Temps", bbox_to_anchor=(1.05, 1), loc="upper left")
            
            # Remove top and right axes
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            
            # Adjust layout
            plt.tight_layout()
        
            # Display the bar plot
            st.pyplot(fig)

        
    else:
        st.error("No data loaded from the Google Sheet. Please check your Spreadsheet ID or Range Name.")


if __name__ == "__main__":
    main()
