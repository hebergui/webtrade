google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawStocksChart);

function drawStocksChart() {
    // Create and populate the data table.
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'Date'); //0
    data.addColumn('number', 'Low'); //1
    data.addColumn('number', 'Open'); //2
    data.addColumn('number', 'High'); //3
    data.addColumn('number', 'Close'); //4
    data.addColumn('number', 'MM30'); //5
    data.addColumn('number', 'Phase'); //6
    data.addColumn('number', 'Force'); //7
    data.addRows(data4stocks);

    var options = {
        legend: {
            position: 'top'
        },
        candlestick: {
            fallingColor: { strokeWidth: 0, fill: '#a52714' }, // red
            risingColor: { strokeWidth: 0, fill: '#0f9d58' }   // green
        },
        vAxes: {
            1: {
                ticks: [0, 1, 2, 3, 4]
            }
        },
        seriesType: "candlesticks",
        series: {
            0: {
                color: "black",
                visibleInLegend: false,
                targetAxisIndex: 0
            },
            1: {
                type: "line",
                targetAxisIndex: 0
            },
            2: {
                color: '#dfe5f0', //grey
                type: "bars",
                targetAxisIndex: 1,
            },
            3: {
                color: '#f5d0c4', //orange
                type: "line",
                targetAxisIndex: 1,
            }
        }
    };

    // Create and draw the visualization.
    var chartCtx = document.getElementById('chart_stocks_div');
    if (chartCtx != null) {
        var chart = new google.visualization.ComboChart(chartCtx);
        chart.draw(data, options);
    }
}

$(document).ready(function() {
    $('#edit-type-timeline select').change(function() {
            if ($(this).val() == "block") {
                url = '/graph/company/' + $('#company_selector select').val()
                event.preventDefault();
                location.href = url
            }
    });
});