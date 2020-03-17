const zmq = require("zeromq");
const fs = require("fs");
const crypto = require("crypto");
const { formatRequest } = require("./utils");
const { exec } = require("child_process");

class File {
	constructor(fileName, path) {
		this.path = path;
		this.chunkReadSize = 1024 * 1024 * 20;
		this.fileName = fileName;
		this.stats = fs.statSync(this.getPath());
	}

	getPath() {
		return `./${this.path}/${this.fileName}`;
	}
}

class Client {
	constructor(id = 0, ip = "localhost", port = 5555) {
		this.request = zmq.socket("req");
		this.path = `client-${id}`;
		this.pointConnect = `${ip}:${port}`;
		this.listHash;
		this.connect();
	}

	connect() {
		this.request.connect(`tcp://${this.pointConnect}`);
		this.request.on("message", reply => {
			const data = JSON.parse(reply);
			if (data.type == "download") {
				if (data.message.status) {
					this.storeFile(data.message.hash, data.message.content);
				} else {
					this.pointConnect = data.message.content;
					this.request.connect(`tcp://${this.pointConnect}`);
					this.request.send(
						formatRequest("download", {
							filename: data.message.filename,
							hash: data.message.hash
						})
					);
				}
			}
			if (data.type == "downloadlist") {
				if (data.message.status) {
					this.currentFile = JSON.parse(data.message.content);
					this.currentFile["filename"] = data.message.hash;
					this.initDownload(
						JSON.parse(data.message.content),
						data.message.hash
					);
				} else {
					this.request.disconnect(`tcp://${this.pointConnect}`);
					this.pointConnect = data.message.content;
					this.request.connect(`tcp://${this.pointConnect}`);
					this.request.send(
						formatRequest("downloadlist", { filename: data.message.filename })
					);
				}
			}
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
		let cnt = 1;
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
			console.log(`${cnt++} part sends of file`);
		});

		readStream.on("end", () => {
			const data = JSON.stringify(chord);
			const hash = crypto
				.createHash("sha1")
				.update(data)
				.digest("hex");
			const request = formatRequest("uploadjson", {
				content: data,
				hash: hash
			});
			console.log(`Share your hash file ${hash}`);
			this.request.send(request);
		});
	}

	initDownload(data, hash) {
		this.currentHash = 1;
		data.hashs.forEach(filename => {
			this.request.send(
				formatRequest("download", { filename: filename, hash: hash })
			);
		});
	}

	download(filename) {
		this.request.send(formatRequest("downloadlist", { filename: filename }));
	}

	storeFile(filename, data) {
		console.log(`${this.currentHash} segment download`);
		const buffer = Buffer.from(data);
		const writeStream = fs.createWriteStream(`${this.path}/${filename}`);
		writeStream.write(buffer, err => {
			this.currentHash += 1;
		});
		writeStream.end();
		writeStream.on("ready", () => {
			if (this.currentHash == this.currentFile.hashs.length) {
				const directories = this.currentFile.hashs.map(
					filename => `${this.path}/${filename}`
				);
				const command = directories.join(" ");
				exec(
					`cat ${command} > ${this.path}/${this.currentFile.filename}`,
					(error, stdout, stderr) => {
						if (error) {
							console.log(`error: ${error.message}`);
							return;
						}
						if (stderr) {
							console.log(`stderr: ${stderr}`);
							return;
						}
						exec(`rm ${command}`, (error, stdout, stderr) => {
							if (error) {
								console.log(`error: ${error.message}`);
								return;
							}
							if (stderr) {
								console.log(`stderr: ${stderr}`);
								return;
							}
							console.log("Download complete");
						});
					}
				);
			}
		});
	}
}

const client = new Client(
	process.env.ID || 0,
	process.env.IP || "localhost",
	process.env.PORT || 5555
);
console.log("Type command");
let stdin = process.openStdin();

stdin.addListener("data", data => {
	const inputs = data
		.toString()
		.trim()
		.split(" ");
	const command = inputs[0];
	if (command == "upload") {
		if (inputs.length > 1) {
			const filename = inputs[1];
			client.upload(filename);
		} else {
			console.log("format error, type again");
		}
	} else if (command == "download") {
		if (inputs.length > 1) {
			const filename = inputs[1];
			client.download(filename);
		} else {
			console.log("format error, type again");
		}
	} else if (command == "exit") {
		process.exit(1);
	} else {
		console.log("Command not found, type again");
	}
});

process.on("SIGINT", _ => client.request.close());
