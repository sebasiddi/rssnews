from flask import Flask, jsonify, render_template
import feedparser
from datetime import datetime, timedelta
from dateutil import parser
import os

app = Flask(__name__)

RSS_FEEDS = {
    # Perfil
    "perfil_ultimo": "https://www.perfil.com/feed",
    "perfil_politica": "https://www.perfil.com/feed/politica",
    "perfil_economia": "https://www.perfil.com/feed/economia",
    "perfil_deportes": "https://www.perfil.com/feed/deportes",
    "perfil_sociedad": "https://www.perfil.com/feed/sociedad",
    "perfil_cultura": "https://www.perfil.com/feed/cultura",

    # Clarín
    "clarin_ultimo": "https://www.clarin.com/rss/lo-ultimo/",
    "clarin_politica": "https://www.clarin.com/rss/politica/",
    "clarin_economia": "https://www.clarin.com/rss/economia/",
    "clarin_deportes": "https://www.clarin.com/rss/deportes/",
    "clarin_sociedad": "https://www.clarin.com/rss/sociedad/",
    "clarin_policiales": "https://www.clarin.com/rss/policiales/",
    "clarin_cultura": "https://www.clarin.com/rss/cultura/",

    # La Nación
    "lanacion_ultimo": "https://www.lanacion.com.ar/rss",
    "lanacion_politica": "https://www.lanacion.com.ar/rss/politica",
    "lanacion_economia": "https://www.lanacion.com.ar/rss/economia",
    "lanacion_deportes": "https://www.lanacion.com.ar/rss/deportes",
    "lanacion_sociedad": "https://www.lanacion.com.ar/rss/sociedad",
    "lanacion_policiales": "https://www.lanacion.com.ar/rss/policiales",
    "lanacion_cultura": "https://www.lanacion.com.ar/rss/cultura"
}

CATEGORY_COLORS = {
    "ultimo": "#db6363",       # Rojo claro
    "politica": "#ffcccc",     # Rosa claro
    "economia": "#ccffcc",     # Verde claro
    "deportes": "#ccccff",    # Azul claro
    "sociedad": "#ffcc99",    # Naranja claro
    "policiales": "#c2c2f0",  # Lila claro
    "cultura": "#ffb3ff"      # Rosa fuerte
}


def convert_to_gmt_minus3(published):
    try:
        # Usar dateutil.parser para manejar múltiples formatos de fecha
        parsed_time = parser.parse(published)
        local_time = parsed_time - timedelta(hours=3)
        return local_time
    except Exception as e:
        print(f"Error al convertir fecha: {e}")
        return None


def get_news():
    news_list = []
    for source, url in RSS_FEEDS.items():
        try:
            category = source.split("_")[-1]  # Extraer la categoría
            feed = feedparser.parse(url)
            if feed.entries:
                for entry in feed.entries[:50]:  # Obtener solo las 50 últimas noticias de cada fuente
                    published_time = convert_to_gmt_minus3(entry.get("published", ""))
                    if published_time:  # Solo agregar si hay fecha válida
                        news_list.append({
                            "title": entry.title,
                            "link": entry.link,
                            "published": published_time.strftime("%d/%m/%Y %H:%M:%S"),
                            "source": source.split("_")[0],  # Extraer el nombre de la fuente
                            "category": category,
                            "color": CATEGORY_COLORS.get(category, "#ffffff"),
                            "timestamp": published_time  # Guardar timestamp para ordenar
                        })
            else:
                print(f"No se encontraron entradas para {source} ({url})")
        except Exception as e:
            print(f"Error al procesar {source} ({url}): {e}")

    # Filtrar noticias sin fecha válida
    news_list = [news for news in news_list if news["timestamp"]]

    # Ordenar las noticias por timestamp en orden descendente (más recientes primero)
    news_list.sort(key=lambda x: x["timestamp"], reverse=True)
    return news_list


@app.route("/news", methods=["GET"])
def news():
    return jsonify(get_news())


@app.route("/")
def home():
    return render_template("index.html")

""" 
if __name__ == "__main__":
    app.run(debug=True)
 """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Usa el puerto de Railway o 5000 por defecto
    app.run(host="0.0.0.0", port=port)