const zmq = require("zeromq");
const fs = require("fs");
const crypto = require("crypto");
const network = require("network");
const { formatRequest, formatReply } = require("./utils");

class File {
	constructor(filename, path) {
		this.path = path;
		this.chunkReadSize = 1024;
		this.filename = filename;
		this.stats = fs.statSync(this.getPath());
		this.buffer = Buffer.alloc(this.stats.size);
	}

	getPath() {
		return `./${this.path}/${this.filename}`;
	}
}

class Peer {
	constructor(port, ipConnection, portConnection) {
		this.reply = zmq.socket("rep");
		this.request = zmq.socket("req");
		this.props = {
			port: port,
			start: 0,
			end: 0,
			hash: 0,
			path: null,
			ip: "localhost",
			previous: null
		};
		network.get_active_interface((err, stats) => {
			this.props.ip = stats.ip_address;
			this.props.previous = `${this.props.ip}:${this.props.port}`;
			this.props.path = `peer-${this.props.port}`;
			const hash = crypto
				.createHash("sha1")
				.update(`${stats.mac_address}${this.props.ip}:${this.props.port}`)
				.digest("hex");
			this.setHashProps(hash);
			console.log(this.props);
			if (ipConnection != "" && portConnection != "")
				this.join(ipConnection, portConnection);
		});
	}

	getHash() {
		return this.props.hash;
	}

	check(hash) {
		const id = parseInt(hash, 16);
		if (this.props.start < this.props.end) {
			return id > this.props.start && id <= this.props.end;
		} else {
			return id > this.props.start || id <= this.props.end;
		}
	}

	join(ip, port) {
		this.setPrevious({ port: port, ip: ip });
		this.request.connect(`tcp://${this.props.previous}`);
		let request = formatRequest("check", { hash: this.props.hash });
		this.request.send(request);
		this.request.on("message", reply => {
			const data = JSON.parse(reply);
			// console.log(data);
			if (data.type == "check") {
				if (data.message.status == true) {
					request = formatRequest("interval", {
						hash: this.props.hash,
						port: this.props.port,
						ip: this.props.ip
					});
					this.request.send(request);
				} else {
					request = formatRequest("prev");
					this.request.send(request);
				}
			}
			if (data.type == "interval") {
				this.request.disconnect(`tcp://${this.props.previous}`);
				this.props.previous = data.message.prev;
				this.request.connect(`tcp://${this.props.previous}`);
				this.request.send(formatRequest("hash"));
				console.log(this.props);
			}
			if (data.type == "hash") {
				this.props.start = parseInt(data.message.hash, 16);
				this.request.disconnect(`tcp://${this.props.previous}`);
				console.log(this.props);
			}
			if (data.type == "prev") {
				this.request.disconnect(`tcp://${this.props.previous}`);
				this.props.previous = data.message.prev;
				this.request.connect(`tcp://${this.props.previous}`);
				request = formatRequest("check", { hash: this.props.hash });
				this.request.send(request);
			}
		});
	}

	bind() {
		this.reply.bind(`tcp://*:${this.props.port}`, err => {
			if (err) console.log(err);
			else console.log("Peer up");
		});

		this.reply.on("message", request => {
			const data = JSON.parse(request);
			// console.log(data);
			if (data.type == "setprev") {
				this.setPrevious(data.params.props);
				this.reply.send(JSON.stringify({ status: true, message: "setprop" }));
			}

			if (data.type == "interval") {
				const previous = this.getPrevious();
				this.setInterval(data.params);
				console.log(this.props);
				this.reply.send(
					formatReply("interval", { update: true, prev: previous })
				);
			}

			if (data.type == "prev") {
				const previous = this.getPrevious();
				this.reply.send(
					formatReply("prev", { prev: previous, hash: data.params.hash })
				);
			}

			if (data.type == "props") {
				const reply = this.getProps();
				this.reply.send(JSON.stringify({ status: true, message: reply }));
			}

			if (data.type == "upload") {
				const stats = data.params;
				const check = this.check(stats.hash);
				if (check) {
					this.storeFile(stats.hash, stats.buffer);
				} else {
					this.request.connect(`tcp://${this.props.previous}`);
					const request = formatRequest("upload", data.params);
					this.request.send(request);
				}
				this.reply.send(
					formatReply("upload", { status: true, message: "uploaded" })
				);
			}

			if (data.type == "check") {
				const reply = this.check(data.params.hash);
				this.reply.send(formatReply("check", { status: reply }));
			}

			if (data.type == "uploadjson") {
				const content = data.params.content;
				const hash = data.params.hash;
				const check = this.check(hash);
				console.log(hash);
				if (check) {
					console.log(hash, content);
					this.storeFileString(hash, content);
				} else {
					this.request.connect(`tcp://${this.props.previous}`);
					const request = formatRequest("uploadjson", data.params);
					this.request.send(request);
				}
				this.reply.send(formatReply("uploadjson", { status: true }));
			}

			if (data.type == "hash") {
				const reply = this.getHash();
				this.reply.send(formatReply("hash", { hash: reply }));
			}

			if (data.type == "download") {
				const filename = data.params.filename;
				this.getFile(filename);
			}
		});
	}

	setHashProps(hash) {
		this.props.hash = hash;
		this.props.end = parseInt(hash, 16);
		this.props.start = parseInt(hash, 16);
	}

	setInterval(data) {
		this.props.start = parseInt(data.hash, 16);
		this.props.previous = `${data.ip}:${data.port}`;
	}

	getProps() {
		return this.props;
	}

	storeFile(filename, data) {
		const writeStream = fs.createWriteStream(`${this.props.path}/${filename}`);
		const buffer = Buffer.from(data);
		writeStream.write(buffer);
	}

	storeFileString(filename, data) {
		fs.writeFile(`${this.props.path}/${filename}`, data, err => {
			if (err) console.log(err);
		});
	}

	getFile(filename) {
		const file = new File(filename, this.props.path);

		const readStream = fs.createReadStream(file.getPath(), {
			highWaterMark: file.chunkReadSize
		});

		readStream.on("data", buffer => {
			const hash = crypto
				.createHash("sha1")
				.update(buffer)
				.digest("hex");
			const message = {
				hash: hash,
				buffer: buffer.toJSON()
			};
			this.reply.send(JSON.stringify({ status: true, message: message }));
		});

		readStream.on("end", () => {
			console.log(`${filename} send`);
		});
	}

	setPrevious(props) {
		this.props.previous = `${props.ip}:${props.port}`;
	}

	getPrevious() {
		return this.props.previous;
	}
}
const server = new Peer(
	process.env.PORT,
	process.env.IPCONNECT,
	process.env.PORTCONNECT
);
server.bind();
process.on("SIGINT", _ => {
	server.reply.close();
});
