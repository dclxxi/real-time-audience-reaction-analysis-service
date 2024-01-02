const chartData = {
    times: [],
    concentrations: [],
    reactions: [],
    feedbacks: [],
};

document.addEventListener('DOMContentLoaded', function () {
    processReactionsData(reactions);
});

function processReactionsData(reactions) {
    reactions.forEach(function (reaction) {
        chartData.times.push(reaction.time);
        chartData.concentrations.push(reaction.concentration);
        chartData.reactions.push({
            positive: reaction.positive,
            neutral: reaction.neutral,
            negative: reaction.negative
        });
        chartData.feedbacks.push(reaction.feedback);
    });

    initLineChart();
    initBarChart();
}

function initLineChart() {
    const ctx = document.getElementById('chart-left').getContext('2d');
    const timeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.times,
            datasets: [{
                label: '시간대 별 청중 반응 차트',
                data: chartData.concentrations,
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
            },
            onHover: function (event, elements) {
                if (elements.length > 0) {
                    const index = elements[0].index;
                    const reaction = chartData.reactions[index];
                    const feedback = chartData.feedbacks[index];

                    updateBarChart(reaction.positive, reaction.neutral, reaction.negative);
                    document.getElementById('feedback-display').innerHTML = feedback.replace(/\\n/g, '<br>');
                }
            },
        }
    });
}

function updateBarChart(positive, neutral, negative) {
    myHorizontalChart.data.datasets[0].data = [positive, neutral, negative];
    myHorizontalChart.update();
}

let myHorizontalChart;

function initBarChart() {
    const ctx = document.getElementById('chart-right').getContext('2d');
    myHorizontalChart = new Chart(ctx, {
        type: 'bar', // 차트 타입을 수평 바로 설정
        data: {
            labels: ["긍정", "중립", "부정"],
            datasets: [{
                label: '시간대 별 청중 반응 차트',
                data: [0, 0, 0],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)'
                ],
                borderWidth: 1,
                barThickness: 3
            }]
        },
        options: {
            legend: {
                display: false
            },
            indexAxis: 'y',
            maintainAspectRatio: false,
            aspectRatio: 1,
            scales: {
                x: {
                    display: false,
                    grid: {
                        display: false // x축 그리드 라인 숨기기
                    },
                    beginAtZero: true,
                    max: 100,
                },
                y: {
                    grid: {
                        display: false
                    },
                }
            }
        }
    });
}