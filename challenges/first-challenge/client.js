// Hello World client
// Connects REQ socket to tcp://localhost:5555
// Sends "Hello" to server.

let zmq = require("zeromq");

// socket to talk to server
console.log("Connecting to hello world server…");
let requester = zmq.socket("req");

requester.on("message", function(reply) {
	console.log("Received reply : [", reply.toString(), "]");
	requester.close();
	process.exit(0);
});

requester.connect("tcp://localhost:5555");

console.log("Sending request…");
requester.send(
	JSON.stringify({
		left: parseInt(process.env.LEFT) || 0,
		oper: process.env.OPER || "+",
		right: parseInt(process.env.RIGHT) || 0
	})
);

process.on("SIGINT", function() {
	requester.close();
});
