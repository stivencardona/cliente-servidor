"use strict";

let zmq = require("zeromq");
process.stdin.resume();
process.stdin.setRawMode(true);

let sender = zmq.socket("push");
sender.bind("tcp://*:5557");

let sink = zmq.socket("push");
sink.bind("tcp://localhost:5558");

let rep = zmq.socket("rep");
rep.bind("tcp://localhost:5559");

let data = [
	{ x: 0, y: 0 },
	{ x: 2, y: 0 },
	{ x: 1, y: 0 },
	{ x: 3, y: 0 },
	{ x: 4, y: 0 },
	{ x: 0, y: 5 },
	{ x: 0, y: 2 },
	{ x: 0, y: 1 },
	{ x: 1, y: 3 },
	{ x: 2, y: 1 },
	{ x: 3, y: 2 },
	{ x: 4, y: 4 },
];

let u = [
	{ x: 1, y: 1 },
	{ x: 2, y: 0 },
];

function formatMessage(points) {
	let obj = {
		centroids: u,
		points: points,
	};
	return JSON.stringify(obj);
}

function work() {
	let start = 0,
		end = 0;
	while (start < data.lenght) {
		end = Math.min(data.lenght, end + sz);
		let msg = formatMessage(data.slice(start, end));
		sender.send(msg);
		start = end;
	}
}

rep.on("message", (data) => {
	let sz = 4;
	let request = JSON.parse(data);
	if (request.type == "next") {
		work();
	}
	if (request.type == "finish") {
		console.log("yeah :)");
	}
});

console.log("Press enter when the workers are ready…");
process.stdin.on("data", function () {
	process.stdin.pause();
	work();
});
