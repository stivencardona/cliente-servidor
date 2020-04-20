# Task worker
# Connects PULL socket to tcp://localhost:5557
# Collects workloads from ventilator via that socket
# Connects PUSH socket to tcp://localhost:5558
# Sends results to sink via that socket
#
# Author: Lev Givon <lev(at)columbia(dot)edu>

import sys
import time
import zmq
import json
import linecache

context = zmq.Context()

# Socket to receive messages on
receiver = context.socket(zmq.PULL)
receiver.connect("tcp://localhost:5557")

# Socket to send messages to
sender = context.socket(zmq.PUSH)
sender.connect("tcp://localhost:5558")

def distance(pointA,pointB):
	return sum([ (x[0] - x[1])**2 for x in zip(pointA, pointB) ])

def getPoint(line):
	return [float(x) for x in line.split(",")]

def calculateDistance(id, centroids, nameFile):
	return [distance(centroid, getPoint(linecache.getline(nameFile, id + 1))) for centroid in centroids] 

def emptyList(dimension):
	return [0 for i in range(dimension)]

# Process tasks forever
while True:
	nameFile = "./iris-data-set/normalized.csv"
	
	tasks = json.loads(receiver.recv())
	
	data = {"tags":[], "sums":[ emptyList(len(tasks["centroids"][0])) for i in range(len(tasks["centroids"]))]}


	for id in range(tasks["range"][0], tasks["range"][1]):
		distances = calculateDistance(id, tasks["centroids"],nameFile)
		data["tags"].append([id, distances[0], 0])
		
		for i,value in enumerate(distances):
			if value < data["tags"][len(data["tags"]) - 1][1]:
				data["tags"][len(data["tags"]) - 1] = [id,value,i]
		
		currentPoint = getPoint(linecache.getline(nameFile, id + 1))
		
		for i in range(len(tasks["centroids"][0])):
			data["sums"][data["tags"][len(data["tags"]) - 1][2]][i] += currentPoint[i]
	
	sender.send_string(json.dumps(data))

