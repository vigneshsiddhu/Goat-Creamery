document.addEventListener("DOMContentLoaded", function () {
    const chartsEl = document.getElementById("report-charts");
    if (!chartsEl || typeof Chart === "undefined") {
        initMap();
        return;
    }
    const charts = JSON.parse(chartsEl.textContent);
    const purple = "#6F63D9";
    const green = "#16a34a";
    const red = "#dc2626";
    const orange = "#ea580c";
    const palette = ["#6F63D9", "#16a34a", "#ea580c", "#0ea5e9", "#db2777", "#ca8a04", "#7c3aed"];

    function makeChart(id, config) {
        const canvas = document.getElementById(id);
        if (!canvas) return;
        new Chart(canvas, config);
    }

    if (charts.daily) {
        makeChart("chart-daily", {
            type: "line",
            data: {
                labels: charts.daily.labels,
                datasets: [{
                    label: charts.daily.label,
                    data: charts.daily.values,
                    borderColor: purple,
                    backgroundColor: "rgba(111, 99, 217, 0.15)",
                    fill: true,
                    tension: 0.35,
                    pointRadius: 2,
                }],
            },
            options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } },
        });
    }

    if (charts.weekday) {
        makeChart("chart-weekday", {
            type: "bar",
            data: {
                labels: charts.weekday.labels,
                datasets: [{
                    label: charts.weekday.label,
                    data: charts.weekday.values,
                    backgroundColor: charts.weekday.labels.map(function (label) {
                        return ["Fri", "Sat", "Sun"].indexOf(label) >= 0 ? orange : purple;
                    }),
                    borderRadius: 6,
                }],
            },
            options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } },
        });
    }

    if (charts.flavour) {
        makeChart("chart-flavour", {
            type: "doughnut",
            data: {
                labels: charts.flavour.labels,
                datasets: [{ data: charts.flavour.values, backgroundColor: palette }],
            },
            options: { plugins: { legend: { position: "bottom" } } },
        });
    }

    if (charts.payment) {
        makeChart("chart-payment", {
            type: "doughnut",
            data: {
                labels: charts.payment.labels,
                datasets: [{ data: charts.payment.values, backgroundColor: palette }],
            },
            options: { plugins: { legend: { position: "bottom" } } },
        });
    }

    if (charts.city) {
        makeChart("chart-city", {
            type: "bar",
            data: {
                labels: charts.city.labels,
                datasets: [{
                    label: "Revenue ₹",
                    data: charts.city.values,
                    backgroundColor: ["#6F63D9", "#16a34a"],
                    borderRadius: 6,
                }],
            },
            options: { indexAxis: "y", plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true } } },
        });
    }

    if (charts.session) {
        makeChart("chart-session", {
            type: "bar",
            data: {
                labels: charts.session.labels,
                datasets: [
                    { label: "Morning", data: charts.session.morning, backgroundColor: "#93c5fd", stack: "milk" },
                    { label: "Evening", data: charts.session.evening, backgroundColor: "#6366f1", stack: "milk" },
                ],
            },
            options: { scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true } } },
        });
    }

    if (charts.goats) {
        makeChart("chart-goats", {
            type: "bar",
            data: {
                labels: charts.goats.labels,
                datasets: [{ label: "Litres", data: charts.goats.values, backgroundColor: purple, borderRadius: 6 }],
            },
            options: { indexAxis: "y", plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true } } },
        });
    }

    if (charts.movers) {
        makeChart("chart-movers", {
            type: "bar",
            data: {
                labels: charts.movers.labels,
                datasets: [{
                    label: "Change kg",
                    data: charts.movers.values,
                    backgroundColor: charts.movers.values.map(function (value) {
                        return value >= 0 ? green : red;
                    }),
                    borderRadius: 6,
                }],
            },
            options: { plugins: { legend: { display: false } } },
        });
    }

    if (charts.current) {
        makeChart("chart-current", {
            type: "bar",
            data: {
                labels: charts.current.labels,
                datasets: [{ label: "kg", data: charts.current.values, backgroundColor: "#a78bfa", borderRadius: 6 }],
            },
            options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: false } } },
        });
    }

    if (charts.mix) {
        makeChart("chart-mix", {
            type: "line",
            data: {
                labels: charts.mix.labels,
                datasets: [
                    {
                        label: "Milk L",
                        data: charts.mix.milk,
                        borderColor: "#4338ca",
                        backgroundColor: "rgba(67, 56, 202, 0.12)",
                        fill: true,
                        tension: 0.35,
                        yAxisID: "y",
                        pointRadius: 2,
                    },
                    {
                        label: "Sales ₹",
                        data: charts.mix.sales,
                        borderColor: "#ea580c",
                        backgroundColor: "rgba(234, 88, 12, 0.08)",
                        fill: true,
                        tension: 0.35,
                        yAxisID: "y1",
                        pointRadius: 2,
                    },
                ],
            },
            options: {
                scales: {
                    y: { beginAtZero: true, position: "left", title: { display: true, text: "Litres" } },
                    y1: { beginAtZero: true, position: "right", grid: { drawOnChartArea: false }, title: { display: true, text: "₹" } },
                },
            },
        });
    }

    initMap();
});

function initMap() {
    const mapEl = document.getElementById("report-map");
    const dataEl = document.getElementById("report-map-data");
    if (!mapEl || !dataEl || typeof L === "undefined") return;
    const mapData = JSON.parse(dataEl.textContent);
    const map = L.map(mapEl).setView(mapData.center || [11.48, 78.38], mapData.zoom || 8);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 18,
        attribution: "&copy; OpenStreetMap",
    }).addTo(map);
    const points = mapData.points || [];
    const maxAmount = Math.max.apply(null, points.map(function (p) { return p.amount; }).concat([1]));
    points.forEach(function (point) {
        const radius = 8 + (point.amount / maxAmount) * 16;
        L.circleMarker([point.lat, point.lng], {
            radius: radius,
            color: "#c2410c",
            fillColor: "#ea580c",
            fillOpacity: 0.55,
            weight: 1,
        }).bindPopup(
            "<strong>" + point.label + "</strong><br>" +
            point.city + " · " + point.date + "<br>₹" + Math.round(point.amount)
        ).addTo(map);
    });
    if (points.length) {
        map.fitBounds(points.map(function (p) { return [p.lat, p.lng]; }), { padding: [28, 28], maxZoom: 11 });
    }
}
