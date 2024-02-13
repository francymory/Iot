from flask import Flask, request, jsonify

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


# Dizionario per memorizzare gli identificatori dei braccialetti e i loro dati associati
braccialetti = {}

@app.route('/', methods=['POST'])
def ricevi_richiesta():
    dati_richiesta = request.get_json()
    identificatore = dati_richiesta.get('id','')
    latitude=dati_richiesta.get('latitude','')
    longitude=dati_richiesta.get('longitude','')
    caduta=dati_richiesta.get("caduta")
    ip=request.remote_addr

    
    # Memorizza i dati del braccialetto utilizzando l'identificatore come chiave nel dizionario
    braccialetti[identificatore] = dati_richiesta
    print(f"ho ricevuto da {identificatore} con ip {ip}\n{braccialetti[identificatore]}")

    #dati = {"vicini": 0, "allarme": caduta}
    #print(f"ho ricevuto da {ip}\n{latitude}\t{longitude}\t{caduta}")
    return "200"

if __name__ == '__main__':

    app.run(host='192.168.1.185') 