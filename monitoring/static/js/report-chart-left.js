var ctx = document.getElementById('chart-left').getContext('2d');
var timeChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ["0분", "3분", "5분", "10분", "15분", "20분", "25분", "30분"],
        datasets: [{
            label: '시간대 별 청중 반응 차트',
            data: [12, 29, 30, 23, 23, 29, 25,30],
            fill: false,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
        }]
    },
    options: {
        maintainAspectRatio: false,
        aspectRatio: 1,
        scales: {
            y: {
                beginAtZero: false,
                title: {
                    display: true,
                    text: '인원'
                },
                ticks: {
                    stepSize: 10,
                    beginAtZero: true,
                    max: 30
                }
            },
            x: {
                title: {
                    display: true,
                    text: '시간 (분)'
                }
            }
        }
    }
});