from flask import Flask, render_template, request, jsonify
import requests
import json
from functools import lru_cache

app = Flask(__name__)
apikey = "8c6a419"

# Cache para limitar el consumo de la API OMDB
@lru_cache(maxsize=100)
def searchfilms(search_text):
    url = "https://www.omdbapi.com/?s=" + search_text + "&apikey=" + apikey
    response = requests.get(url)
    print("Response status:", response.status_code)
    print("Response JSON:", response.json())  
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve search results.")
        return None
    
def getmoviedetails(movie):
    url = "https://www.omdbapi.com/?i=" + movie["imdbID"] + "&apikey=" + apikey
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve search results.")
        return None

flags_cache = {}

# Guardar las banderas en memoria para evitar hacer muchas solicitudes para el mismo pais
def get_country_flag(fullname):
    if fullname in flags_cache:
        return flags_cache[fullname]

    url = f"https://restcountries.com/v3.1/name/{fullname}?fullText=true"
    response = requests.get(url)
    if response.status_code == 200:
        country_data = response.json()
        if country_data:
            flag_url = country_data[0].get("flags", {}).get("svg", None)
            flags_cache[fullname] = flag_url  # Guardar en caché
            return flag_url
    print(f"Failed to retrieve flag for country code: {fullname}")
    return None

def merge_data_with_flags(filter):
    filmssearch = searchfilms(filter)
    moviesdetailswithflags = []
    if filmssearch and "Search" in filmssearch:
        for movie in filmssearch["Search"]:
            moviedetails = getmoviedetails(movie)
            countriesNames = moviedetails["Country"].split(",")
            countries = []
            for country in countriesNames:
                countrywithflag = {
                    "name": country.strip(),
                    "flag": get_country_flag(country.strip())
                }
                countries.append(countrywithflag)
            moviewithflags = {
                "title": moviedetails["Title"],
                "year": moviedetails["Year"],
                "countries": countries
            }
            moviesdetailswithflags.append(moviewithflags)
    else:
        print("No se encontraron resultados para esta búsqueda.")
    return moviesdetailswithflags


@app.route("/")
def index():
    filter = request.args.get("filter", "").upper()
    movies = merge_data_with_flags(filter)
    print("Movies:", movies) 
    return render_template("index.html", movies=movies)

@app.route("/api/movies")
def api_movies():
    filter = request.args.get("filter", "")
    return jsonify(merge_data_with_flags(filter))    

if __name__ == "__main__":
    app.run(debug=True)
