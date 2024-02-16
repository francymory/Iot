from flask import Flask, request, jsonify, Response
import json
from flask_sqlalchemy import SQLAlchemy
import string, random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///braccialetti.db'
db = SQLAlchemy(app)

# Creo la tabella e le colonne per i braccialetti
class Braccialetto(db.Model):
    identifier = db.Column(db.String(200), primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    caduta = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"Braccialetto: {self.identifier}, {self.latitude}, {self.longitude}, {self.caduta}"
    
# Creo la tabella per il login 
class Utente(db.Model):
    id = db.Column(db.String(15), primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(15), nullable=False)


# Metto i dati da parte di un braccialetto, spediti con una POST nel bridge, nel DB 
@app.route('/data', methods=['POST'])
def ricevi_richiesta():
    dati_richiesta = request.get_json()
    identifier = dati_richiesta.get('id', '')
    latitude = float(dati_richiesta.get('latitude', '0.0'))
    longitude = float(dati_richiesta.get('longitude', '0.0'))
    caduta = bool(dati_richiesta.get("caduta", False))

    print(f'stampa prova: ho ricevuto da identifier={identifier}, latitude={latitude}, longitude={longitude}, caduta={caduta}')

    # Cerco il braccialetto nel database
    braccialetto_esistente = Braccialetto.query.filter_by(identifier=identifier).first()

    if braccialetto_esistente:
        # Se esiste già aggiorni i dati del braccialetto esistente
        braccialetto_esistente.latitude = latitude
        braccialetto_esistente.longitude = longitude
        braccialetto_esistente.caduta = caduta
        db.session.commit()
    else:
        # Altrimenti aggiung il braccialetto e i suoi dati nel database
        braccialetto = Braccialetto(identifier=identifier, latitude=latitude, longitude=longitude, caduta=caduta)
        db.session.add(braccialetto)
        db.session.commit()
    return "Info aggiunte al DB, 200"
    

# per generare stringhe
def genera_stringa_casuale ():
    lunghezza=10
    caratteri = string.ascii_letters + string.digits
    stringa_casuale = ''.join(random.choice(caratteri) for _ in range(lunghezza))
    return stringa_casuale


# procedura di login
@app.route('/login',methods=['POST'])
def login():
    richiesta = request.get_json()
    username=richiesta.get('username')
    password=richiesta.get('password')
    
    utente = Utente.query.filter_by(username=username,password=password).first()

    if utente:
        j_data=json.dumps({"id":utente.id})
        return Response(j_data,status=200, mimetype='application/json')        # utente valido
    else:
        j_data=json.dumps({"id":0})             # utente o password sbagliata / non esistente
        return Response(j_data,status=400, mimetype='application/json')


# procedura di sign up
@app.route('/signup',methods=['POST'])
def signup():
    richiesta = request.get_json()
    username=richiesta.get('username')
    
    utente = Utente.query.filter_by(username=username).first()

    if utente:
        data=json.dumps({"id":0})  
        return Response(data,status=400, mimetype='application/json')  # username già usato, 400 ERRORE
    
    password=richiesta.get('password')
    id=genera_stringa_casuale()       # genera identificativo
    nuovo_utente = Utente(id=id, username=username, password=password)  # creazione utente
    db.session.add(nuovo_utente)
    db.session.commit()

    data=json.dumps({"id":id})
    return Response(data,status=200, mimetype='application/json')        # utente valido


# Verifico se un braccialetto è isolato, gestisco le GET del bridge
@app.route('/others/<string:braccialetto_id>', methods=['GET'])

def check_isolato(braccialetto_id):

    braccialetto = Braccialetto.query.filter_by(identifier=braccialetto_id).first()
    if braccialetto is None:
        return jsonify({"isolato": 2}), 400

    # Verifica se il braccialetto è isolato o meno
    altri_braccialetti = Braccialetto.query.filter(Braccialetto.identifier != braccialetto_id).all()
    
    cad = 0
    lat = 0
    long = 0
    vicini = False  # Variabile booleana per tenere traccia se almeno un altro braccialetto è nel raggio d'azione

    for altro_braccialetto in altri_braccialetti:
        distanza = calcola_distanza(braccialetto.latitude, braccialetto.longitude,
                                     altro_braccialetto.latitude, altro_braccialetto.longitude)
        print(f"distanza={distanza}")
    
        if distanza <= 1000:
            vicini = True
            if altro_braccialetto.caduta == 1:
                cad = 1
                lat = altro_braccialetto.latitude
                long = altro_braccialetto.longitude
    # Prepariamo il dizionario dei parametri
    response_data = {
        "isolato": 0 if vicini else 1,
        "caduto": cad,
        "latitude": lat,
        "longitude": long
    }
    print("invio a ", braccialetto_id, response_data)
    return jsonify(response_data), 200


# Funzione per calcolare la distanza in metri tra due coordinate GPS
def calcola_distanza(lat1, lon1, lat2, lon2):
    # fanculo la distanza geodesica!!! beccati questa distanza euclidea 0 neuroni usati
    return ((lat1-lat2)**2+(lon1-lon2)**2)**(0.5)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(host='192.168.1.52')