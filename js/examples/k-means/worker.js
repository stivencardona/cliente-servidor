// Task worker in node.js
// Connects PULL socket to tcp://localhost:5557
// Collects workloads from ventilator via that socket
// Connects PUSH socket to tcp://localhost:5558
// Sends results to sink via that socket

var zmq = require("zeromq"),
	receiver = zmq.socket("pull"),
	sender = zmq.socket("push");

receiver.on("message", (data) => {
	const values = JSON.parse(data);
	console.log(values);
	sender.send("yes");
});

receiver.connect("tcp://localhost:5557");
sender.connect("tcp://localhost:5558");

process.on("SIGINT", function () {
	receiver.close();
	sender.close();
	process.exit();
});
