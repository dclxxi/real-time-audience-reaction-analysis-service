const chartData = {
    times: [],
    concentrations: [],
    reactions: [],
    feedbacks: [],
    strengths: [],
    weaknesses: [],
    improvements: [],
};


function initDoughnutChart() {
    const ctx = document.getElementById('emotionDoughnutChart').getContext('2d');
    const doughnutChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['긍정', '중립', '부정'],
            datasets: [{
                label: '감정 비율',
                data: [averages.positive, averages.neutral, averages.negative],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(75, 192, 192, 0.7)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(75, 192, 192, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            aspectRatio: 1,
            cutout: '70%',
        },
        plugins: [{
            id: 'textInsideDoughnut',
            beforeDraw: function (chart) {
                const ctx = chart.ctx;
                ctx.save();

                ctx.font = '20px Arial';
                ctx.fillStyle = 'black';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';

                const centerX = (chart.chartArea.left + chart.chartArea.right) / 2;
                const centerY = (chart.chartArea.top + chart.chartArea.bottom) / 2;
                const text = "평균 집중도: " + Math.round(averages.concentration) + "%";

                ctx.fillText(text, centerX, centerY);
                ctx.restore();
            }
        }]
    });
}

document.addEventListener('DOMContentLoaded', function () {
    initDoughnutChart();
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
        chartData.strengths.push(reaction.feedback_strength);
        chartData.weaknesses.push(reaction.feedback_weakness);
        chartData.improvements.push(reaction.feedback_improvement);
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
                label: '시간대 별 청중 집중도',
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
                    min: 0,
                    max: 100,
                    title: {
                        display: true,
                        text: '집중도'
                    },
                    ticks: {
                        stepSize: 20,
                        beginAtZero: true,
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
                    const strength = chartData.strengths[index];
                    const weakness = chartData.weaknesses[index];
                    const improvement = chartData.improvements[index];
                    const tmp = document.createElement("div")
                    let strength_txt = ''
                    let weakness_txt = ''
                    let improvement_txt = ''
                    for (var x of strength){
                        strength_txt += '- ' + x + '\n\n';
                    }
                    for (var x of weakness){
                        weakness_txt += '- ' + x + '\n\n';
                    }
                    for (var x of improvement){
                        improvement_txt += '- ' + x + '\n\n';
                    }
                    // document.querySelector(".take1").append(tmp);
                    updateBarChart(reaction.positive, reaction.neutral, reaction.negative);
                    // document.getElementById('feedback-display').innerHTML = feedback.replace(/\\n/g, '<br>');
                    document.querySelector(".take1").innerHTML = strength_txt.replace(/\\n/g, '<br>');
                    document.querySelector(".take2").innerHTML = weakness_txt.replace(/\\n/g, '<br>');
                    document.querySelector(".take3").innerHTML = improvement_txt.replace(/\\n/g, '<br>');
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
                label: '시간대 별 청중 반응',
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