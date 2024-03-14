import csv
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from login_app import Presenza, db, app, Predizione
import pandas as pd
import prophet 
from matplotlib import pyplot as plt

def make_prediction():
    path='parchi.csv'
    df = pd.read_csv(path, header=0)
    frames = []
    for parco_valore in df['zona'].unique():
        frame = df[df['zona'] == parco_valore].copy()
        frame = frame.rename(columns={'ds': 'ds', 'y': 'y'})
        frames.append(frame)

    # Creare e allenare i modelli di Prophet per ciascuna sequenza
    modelli = []
    for frame in frames:
        model = prophet.Prophet()
        model.fit(frame)
        modelli.append(model)


    # Creare un dataframe futuro per ciascuna sequenza
    futures = [model.make_future_dataframe(periods=60) for model in modelli]

    # Fare le previsioni per ciascuna sequenza
    previsioni = [model.predict(future) for model, future in zip(modelli, futures)]

    counter=0
    # Visualizzare le previsioni per ciascuna sequenza
    for parco_valore, previsione in zip(df['zona'].unique(), previsioni):
        for y,ds in zip(previsione['yhat'],previsione['ds']):
            predizione=Predizione(n_persone=int(y),orario=ds,zona=parco_valore)
            db.session.add(predizione)
            db.session.commit()
            counter+=1
    print("ho scritto ", counter, " righe nel db")

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
    make_prediction()