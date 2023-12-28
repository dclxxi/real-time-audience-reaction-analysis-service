var ctx = document.getElementById('chart-right').getContext('2d');
var myHorizontalChart = new Chart(ctx, {
    type: 'bar', // 차트 타입을 수평 바로 설정
    data: {
        labels: ["긍정", "중립", "부정"],
        datasets: [{
            label: '시간대 별 청중 반응 차트',
            data: [70, 20, 10], // y축 데이터
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
            y : {
                grid: {
                    display: false
                },
        }
        }
    }
});