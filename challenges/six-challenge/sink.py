# Task sink
# Binds PULL socket to tcp://localhost:5558
# Collects results from workers via that socket
#
# Author: Lev Givon <lev(at)columbia(dot)edu>

import sys
import time
import zmq
import json

context = zmq.Context()

# Socket to receive messages on
receiver = context.socket(zmq.PULL)
receiver.bind("tcp://*:5558")

# Socket request to fan
request = context.socket(zmq.REQ)
request.connect("tcp://localhost:5559")

# Wait for start of batch
response = json.loads(receiver.recv())
numberCentroids, dimensions, numberPoints = [int(x) for x in response]
groupsSizes = [ 0 for i in range(numberCentroids)]
numberPoint = 0

def generatePoint(size):
	return [0 for i in range(size)]

numberIterations = 0

# Process 10 confirmations
while numberIterations < 5:
	with open("prediction.csv", "r") as file:
		data = file.readlines()
		newCentroids = [generatePoint(dimensions) for i in range(numberCentroids)]
		while numberPoint < numberPoints:
			response = json.loads(receiver.recv())
			numberPoint += len(response["tags"])
			for tag in response["tags"]:
				data[tag[0]] = data[tag[0]].split("\n")[0] + str(tag[2]) + "\n"
				groupsSizes[tag[2]] += 1
			for i,value in enumerate(response["sums"]):
				for j,comp in enumerate(value):
					newCentroids[i][j] += comp 
		with open("prediction.csv", "w") as file:
			file.writelines(data)
		for i, centroid in enumerate(newCentroids):
			for j, comp in enumerate(centroid):
				newCentroids[i][j] = comp / groupsSizes[i] if groupsSizes[i] else 0
		request.send_string(json.dumps(newCentroids))
		request.recv()
		print("hi")
	numberIterations += 1


