from flask import Flask, request, jsonify

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route('/', methods=['POST'])
def ricevi_richiesta():
    dati_richiesta = request.get_json()
    latitude=dati_richiesta.get('latitude','')
    longitude=dati_richiesta.get('longitude','')
    caduta=dati_richiesta.get("caduta")
    ip=request.remote_addr

    dati = {"vicini": 0, "allarme": caduta}
    print(f"ho ricevuto da {ip}\n{latitude}\t{longitude}\t{caduta}")
    return dati, 200

if __name__ == '__main__':

    app.run(host='192.168.1.74') 