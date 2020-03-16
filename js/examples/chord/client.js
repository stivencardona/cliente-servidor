const zmq = require("zeromq");
const fs = require("fs");
const req = zmq.socket("req");
const crypto = require("crypto");
const { formatRequest } = require("./utils");

class File {
	constructor(fileName, path) {
		this.path = path;
		this.chunkReadSize = 1024 * 1024 * 2;
		this.fileName = fileName;
		this.stats = fs.statSync(this.getPath());
		this.position = 0;
	}

	getPath() {
		return `./${this.path}/${this.fileName}`;
	}
}

class Client {
	constructor(id = 0) {
		this.request = zmq.socket("req");
		this.path = `client-${id}`;
		this.pointConnect = "localhost:5555";
		this.connect();
	}

	connect() {
		this.request.connect(`tcp://${this.pointConnect}`);
		this.request.on("message", reply => {
			const data = JSON.parse(reply);
			console.log(data);
		});

		this.request.on("end", () => {
			console.log("good bye");
		});
	}

	upload(filename) {
		const file = new File(filename, this.path);

		let chord = { name: filename, hashs: [] };

		const readStream = fs.createReadStream(file.getPath(), {
			highWaterMark: file.chunkReadSize
		});

		readStream.on("data", buffer => {
			const hash = crypto
				.createHash("sha1")
				.update(buffer)
				.digest("hex");
			const request = formatRequest("upload", {
				hash: hash,
				buffer: buffer.toJSON()
			});
			chord.hashs.push(hash);
			this.request.send(request);
		});

		readStream.on("end", () => {
			console.log(`${filename} send`);
			const data = JSON.stringify(chord);
			const hash = crypto
				.createHash("sha1")
				.update(data)
				.digest("hex");
			const request = formatRequest("uploadjson", {
				content: data,
				hash: hash
			});
			this.request.send(request);
		});
	}
	download() {}
}

const client = new Client();

console.log("Escribe el nombre del archivo");
let stdin = process.openStdin();

stdin.addListener("data", data => {
	const filename = data.toString().trim();
	client.upload(filename);
});

process.on("SIGINT", _ => req.close());
