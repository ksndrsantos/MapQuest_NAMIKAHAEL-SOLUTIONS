import urllib.parse
import requests

main_api = "https://www.mapquestapi.com/directions/v2/route?"
key = "EGVIJZBu6OlzjazQolRueK1VFVfoi30D"  

while True:
    orig = input("Starting Location: ")
    if orig == "quit" or orig == "q":
        break
    dest = input("Destination: ")
    if dest == "quit" or dest == "q":
        break

    url = main_api + urllib.parse.urlencode({"key": key, "from": orig, "to": dest})

    # Fetch API data once
    json_data = requests.get(url).json()

    print("URL: " + (url))

    json_status = json_data["info"]["statuscode"]

    if json_status == 0:
        print("API Status: " + str(json_status) + " = A successful route call.\n")
        print("Directions from " + (orig) + " to " + (dest))
        print("Trip Duration:   " + (json_data["route"]["formattedTime"]))
        print("Miles:           " + str(json_data["route"]["distance"]))
        print("Kilometers:      " + str("{:.2f}".format((json_data["route"]["distance"]) * 1.61)))

        for each in json_data["route"]["legs"][0]["maneuvers"]:
            print((each["narrative"]) + " (" + str("{:.2f}".format((each["distance"]) * 1.61) + " km)"))

    elif json_status == 402:
        print("Status Code: " + str(json_status) + "; Invalid user inputs for one or both locations.")
    elif json_status == 611:
        print("Status Code: " + str(json_status) + "; Missing an entry for one or both locations.")
    else:
        print("For Status Code: " + str(json_status) + "; Refer to:")
        print("https://developer.mapquest.com/documentation/directions-api/status-codes")
