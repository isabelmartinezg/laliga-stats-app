from playwright.sync_api import sync_playwright
import json
from datetime import datetime, timedelta

def extract_half_stats(stats_data):
    resultados = []

    claves = {
        "Total shots": "remates",
        "Shots on target": "remates_a_puerta",
        "Corner kicks": "corners",
        "Yellow cards": "amarillas",
        "Red cards": "rojas"
    }

    for bloque in stats_data.get("statistics", []):
        periodo = bloque.get("period")

        if periodo in ("FIRST_HALF", "1ST"):
            parte = 1
        elif periodo in ("SECOND_HALF", "2ND"):
            parte = 2
        else:
            continue

        datos = {
            "parte": parte,
            "remates_home": 0,
            "remates_away": 0,
            "remates_a_puerta_home": 0,
            "remates_a_puerta_away": 0,
            "corners_home": 0,
            "corners_away": 0,
            "amarillas_home": 0,
            "amarillas_away": 0,
            "rojas_home": 0,
            "rojas_away": 0
        }

        for grupo in bloque.get("groups", []):
            for item in grupo.get("statisticsItems", []):
                nombre = item.get("name")
                if nombre in claves:
                    clave = claves[nombre]
                    datos[f"{clave}_home"] = int(item.get("home", 0) or 0)
                    datos[f"{clave}_away"] = int(item.get("away", 0) or 0)

        resultados.append(datos)

    return resultados


resultados_finales = []
procesados = set()  # 🔥 Para evitar duplicados

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    inicio = datetime(2025, 8, 15)
    fin = datetime.now()

    fecha_actual = inicio

    while fecha_actual <= fin:
        fecha_str = fecha_actual.strftime("%Y-%m-%d")
        print(f"\n=== Buscando partidos del {fecha_str} ===")

        url = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{fecha_str}"
        response = page.request.get(url)
        data = response.json()

        eventos = data.get("events", [])

        laliga = [
            e for e in eventos
            if e["tournament"]["name"] == "LaLiga"
        ]

        for partido in laliga:
            event_id = partido["id"]
            home = partido["homeTeam"]["name"]
            away = partido["awayTeam"]["name"]

            # 🔥 Evitar duplicados
            if event_id in procesados:
                print(f"   (ya procesado, se salta {home} vs {away})")
                continue

            procesados.add(event_id)

            print(f"\n==============================")
            print(f"{home} vs {away} (ID: {event_id})")
            print("==============================")

            stats_url = f"https://api.sofascore.com/api/v1/event/{event_id}/statistics?detail=1"
            stats_response = page.request.get(stats_url)
            stats_data = stats_response.json()

            partes = extract_half_stats(stats_data)

            # 🔥 Añadir cada parte al JSON
            for p in partes:
                registro = {
                    "fecha": fecha_str,
                    "home": home,
                    "away": away,
                    "parte": p["parte"],
                    "remates_home": p["remates_home"],
                    "remates_away": p["remates_away"],
                    "remates_a_puerta_home": p["remates_a_puerta_home"],
                    "remates_a_puerta_away": p["remates_a_puerta_away"],
                    "corners_home": p["corners_home"],
                    "corners_away": p["corners_away"],
                    "amarillas_home": p["amarillas_home"],
                    "amarillas_away": p["amarillas_away"],
                    "rojas_home": p["rojas_home"],
                    "rojas_away": p["rojas_away"]
                }

                resultados_finales.append(registro)

            # 🔥 Crear parte TOTAL sumando todas las partes
            if partes:
                total = {
                    "fecha": fecha_str,
                    "home": home,
                    "away": away,
                    "parte": "total",
                    "remates_home": 0,
                    "remates_away": 0,
                    "remates_a_puerta_home": 0,
                    "remates_a_puerta_away": 0,
                    "corners_home": 0,
                    "corners_away": 0,
                    "amarillas_home": 0,
                    "amarillas_away": 0,
                    "rojas_home": 0,
                    "rojas_away": 0
                }

                for p in partes:
                    total["remates_home"] += int(p["remates_home"])
                    total["remates_away"] += int(p["remates_away"])
                    total["remates_a_puerta_home"] += int(p["remates_a_puerta_home"])
                    total["remates_a_puerta_away"] += int(p["remates_a_puerta_away"])
                    total["corners_home"] += int(p["corners_home"])
                    total["corners_away"] += int(p["corners_away"])
                    total["amarillas_home"] += int(p["amarillas_home"])
                    total["amarillas_away"] += int(p["amarillas_away"])
                    total["rojas_home"] += int(p["rojas_home"])
                    total["rojas_away"] += int(p["rojas_away"])

                resultados_finales.append(total)

        fecha_actual += timedelta(days=1)

    browser.close()

# 🔥 Guardar JSON final
with open("laliga.json", "w", encoding="utf-8") as f:
    json.dump(resultados_finales, f, ensure_ascii=False, indent=4)

print("\nJSON generado correctamente: laliga.json")
