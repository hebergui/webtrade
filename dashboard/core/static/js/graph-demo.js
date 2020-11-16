var graphCtx = document.getElementById("graphChart").getContext('2d');
if (graphCtx != null) {
    var graphChart = new Chart(graphCtx, {
        type: 'candlestick',
        data: {
            datasets: [{
                label: 'Label', //msgChart.graph_label,
                data: getRandomData('01 Apr 2017 00:00 Z', 60), //msgChart.graph_data,
            }]
        },
    });
}

var getRandomInt = function(max) {
	return Math.floor(Math.random() * Math.floor(max));
};

function randomNumber(min, max) {
	return Math.random() * (max - min) + min;
}

function randomBar(date, lastClose) {
	var open = randomNumber(lastClose * 0.95, lastClose * 1.05).toFixed(2);
	var close = randomNumber(open * 0.95, open * 1.05).toFixed(2);
	var high = randomNumber(Math.max(open, close), Math.max(open, close) * 1.1).toFixed(2);
	var low = randomNumber(Math.min(open, close) * 0.9, Math.min(open, close)).toFixed(2);
	return {
		t: date.valueOf(),
		o: open,
		h: high,
		l: low,
		c: close
	};
}

function getRandomData(dateStr, count) {
	var date = luxon.DateTime.fromRFC2822(dateStr);
	var data = [randomBar(date, 30)];
	while (data.length < count) {
		date = date.plus({days: 1});
		if (date.weekday <= 5) {
			data.push(randomBar(date, data[data.length - 1].c));
		}
	}
	return data;
}