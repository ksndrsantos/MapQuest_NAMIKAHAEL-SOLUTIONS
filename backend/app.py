from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import requests

from mapquest_api import get_route, MapQuestError


# Create the Flask application.
#
# The template folder points to the existing frontend
# templates directory.
#
# The static folder points to the existing frontend
# static directory.
app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static",
    static_url_path="/static"
)

# Allow the frontend to communicate with the backend API.
CORS(app)


@app.route("/")
def home():
    """
    Display the main MapQuest webpage.
    """

    return render_template("index.html")


@app.route("/api/health", methods=["GET"])
def health():
    """
    Check if the backend server is running.

    This endpoint is useful for testing the backend
    before connecting the frontend.
    """

    return jsonify({
        "status": "Backend is running"
    })


@app.route("/api/route", methods=["POST"])
def route():
    """
    Receive route information from the frontend,
    request the route from MapQuest, and return
    a simplified JSON response.
    """

    # Get the JSON data sent by the frontend.
    data = request.get_json()

    # Check if the request contains JSON data.
    if not data:
        return jsonify({
            "error": "No data was provided."
        }), 400

    # Get the starting location.
    start = data.get(
        "start",
        ""
    ).strip()

    # Get the destination.
    destination = data.get(
        "destination",
        ""
    ).strip()

    # Get the selected distance unit.
    #
    # "m" = miles
    # "k" = kilometers
    unit = data.get(
        "unit",
        "m"
    )

    # -----------------------------
    # INPUT VALIDATION
    # -----------------------------

    # Make sure the starting location
    # was provided.
    if not start:
        return jsonify({
            "error": "Starting location is required."
        }), 400

    # Make sure the destination
    # was provided.
    if not destination:
        return jsonify({
            "error": "Destination is required."
        }), 400

    # Only allow the units supported
    # by the MapQuest API.
    if unit not in ["m", "k"]:
        return jsonify({
            "error": (
                "Unit must be 'm' for miles "
                "or 'k' for kilometers."
            )
        }), 400

    try:

        # Request route information from
        # the MapQuest API.
        result = get_route(
            start,
            destination,
            unit
        )

        # Get the route section from
        # the MapQuest response.
        route_data = result.get(
            "route",
            {}
        )

        # -----------------------------
        # ROUTE SUMMARY
        # -----------------------------

        # Get the total route distance.
        total_distance = route_data.get(
            "distance",
            0
        )

        # Get the estimated travel time.
        travel_time = route_data.get(
            "formattedTime",
            ""
        )

        # -----------------------------
        # DIRECTIONS
        # -----------------------------

        directions = []

        # MapQuest organizes directions
        # inside legs and maneuvers.
        for leg in route_data.get(
            "legs",
            []
        ):

            for maneuver in leg.get(
                "maneuvers",
                []
            ):

                directions.append({
                    "instruction": maneuver.get(
                        "narrative",
                        ""
                    ),
                    "distance": maneuver.get(
                        "distance",
                        0
                    ),
                    "time": maneuver.get(
                        "formattedTime",
                        ""
                    )
                })

        # -----------------------------
        # RESPONSE TO FRONTEND
        # -----------------------------

        response = {
            "start": start,
            "destination": destination,
            "distance": total_distance,
            "time": travel_time,
            "unit": (
                "miles"
                if unit == "m"
                else "kilometers"
            ),
            "directions": directions
        }

        return jsonify(response)

    # Handle errors specifically raised
    # by the MapQuest API module.
    except MapQuestError as error:

        return jsonify({
            "error": str(error)
        }), 502

    # Handle errors when communicating
    # with the MapQuest server.
    except requests.exceptions.RequestException:

        return jsonify({
            "error": "Unable to connect to MapQuest."
        }), 502

    # Handle unexpected backend errors.
    except Exception as error:
        print("ERROR:", error)

        return jsonify({
            "error": (
                "An unexpected server "
                "error occurred."
            )
        }), 500


# Start the Flask development server
# when this file is executed directly.
if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
