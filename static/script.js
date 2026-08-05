fetch('/api/scrape-entries')
    .then(response => response.json())
    .then(data => {
        new Chart(document.getElementById('scarpeChart'), {
            type: "line",
            data: {
                labels: data.labels,
                datasets: [{
                    label: "Entries per scrapes",
                    data: data.values,
                    borderWidth: 1
                    // Change the color of the text
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }).catch(error => console.error('Error fetching chart data:', error));
