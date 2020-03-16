const fs = require("fs");

exports.formatRequest = function(type, params = {}) {
	return JSON.stringify({
		description: "request",
		type: type,
		params: params
	});
};

exports.formatReply = function(type, message = {}) {
	return JSON.stringify({
		description: "reply",
		type: type,
		message: message
	});
};
