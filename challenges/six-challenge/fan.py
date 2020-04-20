import zmq
import random
import time
import json
import random
import math

try:
    raw_input
except NameError:
    # Python 3
    raw_input = input

context = zmq.Context()

# Socket to send messages on
sender = context.socket(zmq.PUSH)
sender.bind("tcp://*:5557")

# Socket with direct access to the sink: used to synchronize start of batch
sink = context.socket(zmq.PUSH)
sink.connect("tcp://localhost:5558")

sinkRep = context.socket(zmq.REP)
sinkRep.bind("tcp://*:5559")

print("Input the number of centroids  when the workers are ready: ")
k = raw_input()
print("Sending tasks to workers…")

numberPoints = 150
segment = 3
dimensions = 4

# The first message is "0" and signals start of batch
sink.send_string(json.dumps([k,dimensions, numberPoints]))


def generateCentroid(start, end, size):
	return [random.uniform(start, end) for i in range(size)]

def readFile(nameFile):
	with open(nameFile) as file:
		for i,line in enumerate(file):
			print([float(x) for x in line.split(",")])

def mapper(value, maximum, lenRange):
	return [value, min(maximum, value + lenRange)]

def work(sizeData, numberIntervals, centroids):
	lenRange = math.ceil(sizeData / numberIntervals)
	rangeWork = [mapper(x,sizeData,lenRange) for x in range(0,sizeData,lenRange)]
	for work in rangeWork:
		task = { "centroids": centroids, "range": work}
		sender.send_string(json.dumps(task))

work(numberPoints,12, [ generateCentroid(-3 , 3, dimensions) for i in range(int(k))])


numberIterations = 0

while numberIterations < 5:
	request = sinkRep.recv()
	centroids = json.loads(request)
	numberIterations += 1
	sinkRep.send_string('ok')
	work(numberPoints,12,centroids)