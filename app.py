from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

# Cargar JSON
with open("laliga.json", "r", encoding="utf-8") as f:
    DATA = json.load(f)

@app.route("/")
def index():
    equipos = sorted(list({p["home"] for p in DATA} | {p["away"] for p in DATA}))
    return render_template("index.html", equipos=equipos)

@app.route("/filtrar")
def filtrar():
    equipo = request.args.get("equipo")
    metrica = request.args.get("metrica")
    parte = request.args.get("parte")
    local = request.args.get("local")
    condicion = request.args.get("condicion")
    valor = int(request.args.get("valor"))

    resultados = []

    for p in DATA:
        # Filtrar equipo
        if equipo and equipo not in (p["home"], p["away"]):
            continue

        # Filtrar parte
        if parte != "total" and str(p["parte"]) != parte:
            continue

        # Filtrar local/visitante
        if local == "local" and p["home"] != equipo:
            continue
        if local == "visitante" and p["away"] != equipo:
            continue

        # Obtener valor de la métrica
        campo = f"{metrica}_{'home' if p['home']==equipo else 'away'}"
        valor_metrica = p[campo]

        # Aplicar condición
        if condicion == "menos":
            cumple = valor_metrica < valor
        elif condicion == "mas":
            cumple = valor_metrica > valor
        else:
            cumple = None # sin filtro

        resultados.append({
            "fecha": p["fecha"],
            "vs": p["away"] if p["home"] == equipo else p["home"],
            "valor": valor_metrica,
            "cumple": cumple
        })

    # Calcular porcentaje
    if condicion:
        porcentaje = round(100 * sum(r["cumple"] for r in resultados) / len(resultados), 2)
    else:
        porcentaje = None

    return jsonify({"resultados": resultados, "porcentaje": porcentaje})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

