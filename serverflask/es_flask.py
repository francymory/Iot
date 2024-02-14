from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

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

#gestisco l'arrivo di dati da parte di un braccialetto
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
    return "200"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(host='192.168.1.72')