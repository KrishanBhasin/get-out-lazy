import googlemaps
from datetime import datetime, timedelta
import math
import requests
import json
import iso8601
from googlemaps import directions as directions_client


NCTX_BASE_URL = "https://api.nctx.co.uk/api/v1/"

with open("../config/configuration.json") as json_data_file:
    configuration = json.load(json_data_file)
    GMAPS_API_KEY = configuration["credentials"]["googleMapsApiKey"]
    options = configuration["options"]
    HOME_POSTCODE = options["homePostcode"]
    BUS_STOP_POSTCODE = options["destinationPostcode"]
    BUS_STOP_CODE = options["busStopCode"]
    BUS_NUMBER = options["busNumber"]
    TRAVEL_MODE = options["travelModeToBus"]


def get_walking_time(travel_from, travel_to, travel_mode):
    gmaps = googlemaps.Client(GMAPS_API_KEY)
    directions = directions_client.directions(
        origin=travel_from,
        destination=travel_to,
        client=gmaps,
        mode=travel_mode
    )
    return math.ceil(directions[0]["legs"][0]["distance"]["value"] / 60)


def get_next_bus_time(bus_number, bus_stop_code, travel_time):
    r = requests.get(NCTX_BASE_URL + "departures/" + bus_stop_code + "/realtime")

    bus_time_json = json.loads(r.content.decode("utf-8"))

    for entry in bus_time_json:
        if entry["busService"] == bus_number and entry["time"]:
            departure_time = iso8601.parse_date(entry["time"]).replace(tzinfo=None)
            if datetime.now() + timedelta(minutes=travel_time) > departure_time:
                continue
            return departure_time

    raise Exception("No bus found")


def main():
    walking_time_minutes = get_walking_time(HOME_POSTCODE, BUS_STOP_POSTCODE, TRAVEL_MODE)
    print("Time to bus stop: " + str(walking_time_minutes))
    next_bus_time = get_next_bus_time(BUS_NUMBER, BUS_STOP_CODE, walking_time_minutes)
    print("Next bus time is: " + str(next_bus_time))
    time_to_leave = next_bus_time - timedelta(minutes=walking_time_minutes)
    print("The time to leave is: " + str(time_to_leave))

    time_until_time_to_leave = time_to_leave - datetime.now()

    print("You need to leave in " + str(math.floor(time_until_time_to_leave.seconds/60)) + " minutes.")


if __name__ == "__main__":
    main()
