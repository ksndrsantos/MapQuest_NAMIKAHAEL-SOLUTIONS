const form = document.getElementById("route-form");
const results = document.getElementById("route-results");

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const start = document.getElementById("origin").value.trim();
    const destination = document.getElementById("destination").value.trim();
    const unit = document.getElementById("unit").value;

    results.innerHTML = "";

    if (!start || !destination) {
        results.innerHTML = `
            <div class="error-message">
                Please enter both a starting location and a destination.
            </div>
        `;
        return;
    }

    results.innerHTML = `
        <div class="summary-card">
            <p>Finding route...</p>
        </div>
    `;

    try {
        const response = await fetch("/api/route", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                start: start,
                destination: destination,
                unit: unit
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "Unable to get route information."
            );
        }

        displayRoute(data);

    } catch (error) {
        results.innerHTML = `
            <div class="error-message">
                ${error.message}
            </div>
        `;
    }
});


function displayRoute(data) {
    let directionsHTML = "";

    if (data.directions && data.directions.length > 0) {
        directionsHTML = data.directions.map(function (direction) {
            return `
                <li>
                    ${direction.instruction}
                </li>
            `;
        }).join("");
    } else {
        directionsHTML = `
            <li>Turn-by-turn directions are unavailable.</li>
        `;
    }

    results.innerHTML = `
        <div class="summary-card">
            <h2>Route Summary</h2>

            <p class="summary-item">
                <strong>From:</strong>
                ${data.start}
            </p>

            <p class="summary-item">
                <strong>To:</strong>
                ${data.destination}
            </p>

            <p class="summary-item">
                <strong>Distance:</strong>
                ${data.distance} ${data.unit}
            </p>

            <p class="summary-item">
                <strong>Estimated Travel Time:</strong>
                ${data.time}
            </p>
        </div>

        <div class="directions-card">
            <h2>Turn-by-Turn Directions</h2>

            <ol class="directions-list">
                ${directionsHTML}
            </ol>
        </div>
    `;
}
