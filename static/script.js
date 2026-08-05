fetch("/api/scrape-entries")
    .then(response => response.json())
    .then(data => {  
        const ctx = document.getElementById("scarpeChart1").getContext("2d");
        
        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, "rgba(55, 138, 221, 0.4)"); 
        gradient.addColorStop(1, "rgba(55, 138, 221, 0)");

        new Chart(ctx, {
            type: "line",
            data: {
                labels: data.labels,
                datasets: [{
                    label: "Entries per scrapes",
                    data: data.values,
                    borderColor: "#4ca3a9",
                    backgroundColor: gradient,
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0
                }]
            },
            options: {
                color: "#9E9E9E",
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: "#9E9E9E"
                        },
                        ticks: {
                            color: "#9E9E9E"
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }).catch(error => console.error("Error fetching chart data:", error));

fetch("/api/scrape-urls")
    .then(response => response.json())
    .then(data => {
        const ctx = document.getElementById("scarpeChart2").getContext("2d");

        const drawValues = {
            id: "drawValues",
            afterDraw(chart) {
                const { ctx } = chart;
                chart.data.datasets.forEach((dataset, i) => {
                    const meta = chart.getDatasetMeta(i);
                    meta.data.forEach((slice, index) => {
                        const value = dataset.data[index];
                        const pos = slice.tooltipPosition();
                        ctx.save();
                        ctx.fillStyle = "#FFF";
                        ctx.font = "bold 12px sans-serif";
                        ctx.textAlign = "center";
                        ctx.textBaseline = "middle";
                        ctx.fillText(value, pos.x, pos.y);
                        ctx.restore();
                    });
                });
            }
        };

        new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values
                }]
            },
            plugins: [drawValues],
            options: {
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { color: "#9E9E9E" }
                    }
                }
            }
        });
    }).catch(error => console.error("Error fetching chart data:", error));