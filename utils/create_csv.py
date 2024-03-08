import math
import csv
from datetime import datetime, timedelta
from numpy import random

# Nome del file CSV
csv_file_name = 'parchi.csv'

# Apertura del file CSV e scrittura dei dati
with open(csv_file_name, mode='w', newline='') as file:
    writer = csv.writer(file)

    # Scrivi l'intestazione
    writer.writerow(['ds', 'y','zona'])
    
    start_date = datetime(2024, 1, 1, 0, 0)
    date_sequence = [[1,0.3,1,1,5],[],[]]
    a=math.pi/(7*12)    # periodicità settimanale
    b=math.pi/12        # periodicità giornaliera
    s=[1,5,3]           # coefficiente per la periodicità settimanale
    g=[1,4,2]           # coefficiente per la periodicità giornaliera
    o=[5,2,0]           # offset
    park_sequence=["parcoFerrari","parcoAmendola","parcoResistenza"]   
    # parco ferrari ha più gente, parco resistenza è più vuoto    
    # Calcola la funzione per valori di x da 1 a 365
    for idx,park in enumerate(park_sequence):
        for x in range(500):
            media = int(-s[idx]*math.cos(a*x) + g[idx]*math.cos(b*x) + o[idx])  # funz trig per comportamento prevedibile
            risultato=int(random.normal(loc=media,scale=1,size=1))              # faccio sampling per introdurre noise hehe
            if risultato<0:
                risultato=0                                                     # non posso avere popolaz negativa
            current_date = start_date + timedelta(hours=x)
            formatted_date = current_date.strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([formatted_date,risultato,park])


