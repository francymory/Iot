import csv
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from login_app import Presenza, db, app

# Assicurati di aver definito il tuo oggetto app e il db SQLAlchemy

# Funzione per estrarre i dati dal database e creare il file CSV
def create_csv_from_database():
    # Query per estrarre i dati dal database
    data_from_db = Presenza.query.all()

    # Definizione del nome del file CSV
    csv_file_name = 'parks_data.csv'

    # Definizione dei campi del file CSV
    fieldnames = ['ds', 'y', 'zona']

    # Apertura del file CSV e scrittura dei dati
    with open(csv_file_name, mode='w+', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        # Dizionario per tenere traccia del numero di persone per zona e orario
        data_dict = {}

        # Iterazione sui dati estratti dal database
        for data in data_from_db:
            # Ottieni la chiave composta da zona e orario
            key = (data.zona, data.orario)

            # Aggiorna il numero di persone per la zona e l'orario corrente
            if key in data_dict:
                data_dict[key] += 1
            else:
                data_dict[key] = 1

        # Scrivi i dati nel file CSV
        for (zona, orario), num_persone in data_dict.items():
            writer.writerow({'ds': orario.strftime("%Y-%m-%d %H:%M:%S"), 'y': num_persone, 'zona': zona})

    print(f"File CSV '{csv_file_name}' creato con successo.")

# Eseguire la funzione di creazione del file CSV al momento del caricamento dello script
if __name__ == "_main_":
    create_csv_from_database()