"""Traveling salesman simulation (pure logic, no CLI, no printing)."""

import json
import os
import random
import time

import geopy
import geopy.distance
import pandas as pd

CACHE_FILE = "city_coords_cache.json"

DEFAULT_CITIES = [
    "New York",
    "Knoxville",
    "Birmingham",
    "Baltimore",
    "Bangor",
    "Cleveland",
    "Chicago",
    "Denver",
    "Los Angeles",
    "San Francisco",
    "Raleigh",
    "Seattle",
    "Boston",
    "Houston",
    "Dallas",
    "Miami",
    "Atlanta",
    "Fort Worth",
    "Phoenix",
    "San Diego",
]


def my_cities(*args):
    """Build a list of cities from input."""
    return list(args)


def create_cities_dataframe(cities=None):
    """Create a DataFrame of cities and their latitudes/longitudes.

    Coordinates are cached in ``CACHE_FILE`` so repeated runs do not hit
    Nominatim, which requires clients to cache results and rate-limit
    themselves to at most one request per second.
    """
    if cities is None:
        cities = DEFAULT_CITIES

    cache = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, encoding="utf-8") as fh:
            cache = json.load(fh)

    latitudes = []
    longitudes = []
    for city in cities:
        if city not in cache:
            geolocator = geopy.geocoders.Nominatim(user_agent="tsp_pandas")
            location = geolocator.geocode(city, timeout=10)
            cache[city] = [location.latitude, location.longitude]
            time.sleep(1.1)
        latitudes.append(cache[city][0])
        longitudes.append(cache[city][1])

    with open(CACHE_FILE, "w", encoding="utf-8") as fh:
        json.dump(cache, fh, indent=2)

    return pd.DataFrame(
        {
            "city": cities,
            "latitude": latitudes,
            "longitude": longitudes,
        }
    )


def _coord(df, city):
    """Return (lat, lon) for ``city`` from ``df``."""
    row = df[df["city"] == city].iloc[0]
    return row["latitude"], row["longitude"]


def tsp(cities_df):
    """Sample one random tour, return (total_distance_miles, route)."""
    city_list = cities_df["city"].to_list()
    random.shuffle(city_list)

    distance_list = []
    n = len(city_list)
    for i, city in enumerate(city_list):
        next_city = city_list[(i + 1) % n]
        distance = geopy.distance.distance(
            _coord(cities_df, city), _coord(cities_df, next_city)
        ).miles
        distance_list.append(distance)

    return sum(distance_list), city_list


def run_simulations(count, df=None):
    """Run ``count`` simulations, return (best_distance, best_route, all_distances)."""
    if df is None:
        df = create_cities_dataframe()

    all_runs = []
    for _ in range(count):
        distance, route = tsp(df)
        all_runs.append((distance, route))

    best_distance, best_route = min(all_runs, key=lambda r: r[0])
    return best_distance, best_route, [d for d, _ in all_runs]
