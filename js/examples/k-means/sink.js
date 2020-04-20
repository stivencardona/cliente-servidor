// Task sink in node.js
// Binds PULL socket to tcp://localhost:5558
// Collects results from workers via that socket.

const zmq = require("zeromq");
const receiver = zmq.socket("pull");
let state = false;
let matrix;

receiver.on("message", (push) => {
	console.log(push);
});

process.stdin.on("data", (data) => {
	const inputs = data.toString().trim().split(" ");
	if (inputs[0] == "exit") process.exit();
});

receiver.bindSync("tcp://*:5558");
