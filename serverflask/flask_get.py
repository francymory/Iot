from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from math import radians, sin, cos, sqrt, atan2 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///braccialetti.db'
db = SQLAlchemy(app)

# Creo la tabella e le colonne e la loro rapppresentazione stampabile
class Braccialetto(db.Model):
    identifier = db.Column(db.String(200), primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    caduta = db.Column(db.Boolean, nullable=False)
    ip = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"Braccialetto: {self.identifier}, {self.latitude}, {self.longitude}, {self.caduta}, {self.ip}"

# Metto i dati da parte di un braccialetto, spediti con una POST nel bridge, nel DB 
@app.route('/', methods=['POST'])
def ricevi_richiesta():
    dati_richiesta = request.get_json()
    identifier = dati_richiesta.get('id', '')
    latitude = float(dati_richiesta.get('latitude', '0.0'))
    longitude = float(dati_richiesta.get('longitude', '0.0'))
    caduta = bool(dati_richiesta.get("caduta", False))
    ip = request.remote_addr

    print(f'stampa prova: ho ricevuto da identifier={identifier}, latitude={latitude}, longitude={longitude}, caduta={caduta}, ip={ip}')

    # Cerco il braccialetto nel database
    braccialetto_esistente = Braccialetto.query.filter_by(identifier=identifier).first()

    if braccialetto_esistente:
        # Se esiste già aggiorni i dati del braccialetto esistente
        braccialetto_esistente.latitude = latitude
        braccialetto_esistente.longitude = longitude
        braccialetto_esistente.caduta = caduta
        braccialetto_esistente.ip = ip
        db.session.commit()
    else:
        # Altrimenti aggiung il braccialetto e i suoi dati nel database
        braccialetto = Braccialetto(identifier=identifier, latitude=latitude, longitude=longitude, caduta=caduta, ip=ip)
        db.session.add(braccialetto)
        db.session.commit()
    return "Info aggiunte al DB, 200"

# Verifico se un braccialetto è isolato, gestisco le GET del bridge
@app.route('/<string:braccialetto_id>', methods=['GET'])
def check_isolato(braccialetto_id):
    

    braccialetto = Braccialetto.query.filter_by(identifier=braccialetto_id).first()
    if braccialetto is None:
        return jsonify({"isolato": 2}), 200

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

    return jsonify(response_data), 200


# Funzione per calcolare la distanza in metri tra due coordinate GPS
def calcola_distanza(lat1, lon1, lat2, lon2):
    # Raggio della Terra in metri
    R = 6371000
    # Converti le coordinate in radianti
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    # Differenze tra le coordinate
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    # Calcola la distanza utilizzando la formula di Haversine
    a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distanza = R * c
    return distanza


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(host='192.168.1.185')