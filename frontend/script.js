let map = L.map('map').setView([41.0, -77.0], 7);
let markersLayer = L.layerGroup().addTo(map);
let activeMarker = null;


L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19
}).addTo(map);


function condColor(c) {
    if (c >= 7) return "green";
    if (c >= 5) return "orange";
    if (c >= 0) return "red";
    return "gray";
}


async function reloadMap() {
    markersLayer.clearLayers();

    const year = document.getElementById("yearSelect").value;
    const cond = document.getElementById("condSelect").value;

    let url = `http://127.0.0.1:8000/api/bridges/year/${year}`;
    const resp = await fetch(url);
    const data = await resp.json();

    let condCounts = {};

    data.forEach(b => {
        if (!b.LAT_016 || !b.LONG_017) return;

        let c = parseInt(b.DECK_COND_058);
        condCounts[c] = (condCounts[c] || 0) + 1;

        if (cond === "good" && c < 7) return;
        if (cond === "fair" && (c < 5 || c > 6)) return;
        if (cond === "poor" && c > 4) return;

        let marker = L.circleMarker(
            [b.LAT_016, b.LONG_017],
            {
                radius: 5,
                color: condColor(c),
                weight: 1.5,
                fillOpacity: 0.9
            }
        );

        marker.bridgeId = b.STRUCTURE_NUMBER_008;
        marker.originalColor = condColor(c);

        marker.on("click", () => onMarkerClick(marker));

        marker.addTo(markersLayer);
    });

    let selectedYear = document.getElementById("yearSelect").value;
    updateChart(condCounts, selectedYear);
}


async function onMarkerClick(marker) {

    if (activeMarker) {
        activeMarker.setStyle({
            radius: 5,
            weight: 1.5,
            color: activeMarker.originalColor
        });
    }

    marker.setStyle({
        radius: 10,
        color: "yellow",
        weight: 4
    });

    activeMarker = marker;

    const year = document.getElementById("yearSelect").value;

    const resp = await fetch(
        `http://127.0.0.1:8000/api/bridge/${marker.bridgeId}?year=${year}`
    );

    const b = await resp.json();

    updateDetailTable(b);
}


function updateDetailTable(b) {
    const table = document.getElementById("detailTable");
    table.innerHTML = "";

    const highlightFields = ["STRUCTURE_NUMBER_008", "DECK_COND_058", "ADT_029", "YEAR_BUILT_027", "DATA_YEAR"];

    for (let key in b) {
        let highlight = highlightFields.includes(key) ? "highlight" : "";
        table.innerHTML += `
            <tr class="${highlight}">
                <td><b>${key}</b></td>
                <td>${b[key]}</td>
            </tr>
        `;
    }
}


async function searchBridge() {
    let id = document.getElementById("searchId").value.trim();
    if (!id) return;

    const year = document.getElementById("yearSelect").value;
    let url = `http://127.0.0.1:8000/api/bridge/${id}?year=${year}`;


    const resp = await fetch(url);

    if (!resp.ok) {
        alert("Bridge not found!");
        return;
    }

    const b = await resp.json();
    map.setView([b.LAT_016, b.LONG_017], 14);

    updateDetailTable(b);
}

// Chart.js 
let chart = null;
function drawChart(counts) {

    if (chart) chart.destroy();

    chart = new Chart(
        document.getElementById("condChart"),
        {
            type: "bar",
            data: {
                labels: Object.keys(counts),
                datasets: [{
                    label: "Count",
                    data: Object.values(counts),
                    backgroundColor: "steelblue"
                }]
            },
            options: { responsive: true }
        }
    );
}

// update chart
function updateChart(counts, selectedYear) {
    if (window.conditionChart) {
        window.conditionChart.destroy();
    }

    let ctx = document.getElementById("condChart").getContext("2d");
    // Update external chart title
    try {
        const titleEl = document.getElementById('chartTitle');
        if (titleEl) titleEl.textContent = `Bridge Condition Chart (Year: ${selectedYear})`;
    } catch (e) {
        console.error("Error updating chart title:", e);
    }

    window.conditionChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: Object.keys(counts),
            datasets: [{
                label: "Count",
                data: Object.values(counts),
                backgroundColor: "rgba(30,144,255,0.7)"
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: false
                },
                legend: { display: true }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}




// 
reloadMap();
