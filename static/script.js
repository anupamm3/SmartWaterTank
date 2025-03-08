async function fetchWaterLevel() {
    try {
        const response = await fetch('/get_data');  // Fetch from the Flask server
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();

        if (data.error) {
            console.error(data.error);
        } else {
            updateWaterLevel(data.water_level, data.anomaly);
        }
    } catch (error) {
        console.error('Error fetching water level:', error);
    }
}

function updateWaterLevel(waterLevel, anomaly) {
    const waterDiv = document.getElementById('water');
    const waterLevelDiv = document.getElementById('waterLevel');
    const anomalyAlert = document.getElementById('anomalyAlert');

    // Update the water level display
    waterDiv.style.height = waterLevel + '%';
    waterLevelDiv.textContent = waterLevel + '%';

    // Show anomaly alert if necessary
    anomalyAlert.style.display = anomaly ? 'block' : 'none';
    anomalyAlert.textContent = anomaly ? 'Anomaly detected! Please check the tank.' : '';
}

function startFetching() {
    fetchWaterLevel();  // Initial fetch
    setInterval(fetchWaterLevel, 15000);  // Fetch every 15 seconds
}

async function addEmail() {
const email = document.getElementById('emailInput').value;
const response = await fetch('/add_email', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'  // Ensure JSON content type
    },
    body: JSON.stringify({ email })  // Convert the email to a JSON string
});

const result = await response.json();
const messageDiv = document.getElementById('message');
if (response.ok) {
    messageDiv.textContent = result.message;
    messageDiv.style.color = 'green';
} else {
    messageDiv.textContent = result.error;
    messageDiv.style.color = 'red';
}
document.getElementById('emailInput').value = '';  // Clear the input field
}


window.onload = startFetching;  // Start fetching data when the page loads