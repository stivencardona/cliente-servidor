// Task sink in node.js
// Binds PULL socket to tcp://localhost:5558
// Collects results from workers via that socket.

const zmq = require("zeromq");
const receiver = zmq.socket("pull");
let state = false;
let matrix;

receiver.on("message", push => {
	const data = JSON.parse(push);
	if (!state) {
		matrix = [...Array(data.rows)].map(x => Array(data.columns).fill(0));
		state = true;
	} else {
		matrix[data.i][data.j] = data.dot;
		console.log(matrix);
	}
});

process.stdin.on("data", data => {
	const inputs = data
		.toString()
		.trim()
		.split(" ");
	if (inputs[0] == "exit") process.exit();
});

receiver.bindSync("tcp://*:5558");
