// Task worker in node.js
// Connects PULL socket to tcp://localhost:5557
// Collects workloads from ventilator via that socket
// Connects PUSH socket to tcp://localhost:5558
// Sends results to sink via that socket

var zmq = require("zeromq"),
	receiver = zmq.socket("pull"),
	sender = zmq.socket("push");

function dot(row, column) {
	const result = row.map((element, indx) => {
		return element * column[indx];
	});
	return result.reduce((prev, curr) => {
		return prev + curr;
	});
}

receiver.on("message", data => {
	const values = JSON.parse(data);
	const result = dot(values.row, values.column);
	const message = { i: values.i, j: values.j, dot: result };
	console.log(JSON.parse(data));
	sender.send(JSON.stringify(message));
});

receiver.connect("tcp://localhost:5557");
sender.connect("tcp://localhost:5558");

process.on("SIGINT", function() {
	receiver.close();
	sender.close();
	process.exit();
});
