// Task ventilator in node.js
// Binds PUSH socket to tcp://localhost:5557
// Sends batch of tasks to workers via that socket.

var zmq = require("zeromq");
process.stdin.resume();
process.stdin.setRawMode(true);

// Socket to send messages on
var sender = zmq.socket("push");
sender.bindSync("tcp://*:5557");

var sink = zmq.socket("push");
sink.connect("tcp://localhost:5558");

var i = 0,
	total_msec = 0;

function work() {
	console.log("Sending tasks to workers…");

	// The first message is "0" and signals start of batch
	const A = [
		[1, 2, 3],
		[1, 2, 3],
		[1, 2, 3],
		[1, 2, 3],
		[1, 2, 3]
	];

	const B = [
		[1, 2, 3, 4],
		[1, 2, 3, 4],
		[1, 2, 3, 4]
	];

	const stats = {
		rows: A.length,
		columns: B[0].length
	};

	console.log(stats);

	const BT = B[0].map((col, i) => B.map(row => row[i]));
	console.log(BT);

	sink.send(JSON.stringify(stats));
	A.forEach((row, i) => {
		BT.forEach((column, j) => {
			const message = {
				i: i,
				j: j,
				row: row,
				column: column
			};
			sender.send(JSON.stringify(message));
		});
	});
	sink.close();
	sender.close();
	process.exit();
}

console.log("Press enter when the workers are ready…");
process.stdin.on("data", function() {
	if (i === 0) {
		work();
	}
	process.stdin.pause();
});
