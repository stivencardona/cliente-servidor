// Hello World server
// Binds REP socket to tcp://*:5555
// Expects "Hello" from client, replies with "world"

let zmq = require("zeromq");

// socket to talk to clients
let responder = zmq.socket("rep");

responder.on("message", function(request) {
	let data = JSON.parse(request.toString());
	console.log(data);
	if (data.oper == "+") responder.send(data.left + data.right);
	if (data.oper == "-") responder.send(data.left - data.right);
	if (data.oper == "*") responder.send(data.left * data.right);
	if (data.oper == "/") responder.send(data.left / data.right);
});

responder.bind("tcp://*:5555", function(err) {
	if (err) {
		console.log(err);
	} else {
		console.log("Listening on 5555…");
	}
});

process.on("SIGINT", function() {
	responder.close();
});
