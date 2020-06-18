'''
	UART communcation, client side
	measure connection speed
	speed calculated every chunk_size bytes
'''

import argparse
import serial
import sys
from time import time
from datetime import datetime
import numpy as np

timeout = 2
dev = "/dev/ttyS0"
log_dir = "logs_chunks/"

par = argparse.ArgumentParser(description="Measure speed of UART")
par.add_argument("-n", dest="N", type=int, default=512, help="number of bytes after which speed is calculated")
par.add_argument("-b", dest="baudrate", type=int, default=9600, help="baudrate used in communication")
par.add_argument("-o", dest="log_file", type=str, default="temp", help="log output file, append mode")
args = par.parse_args()

print("\tchunk_size={}, baudrate={}, log file={}".format(args.N, args.baudrate, args.log_file))
print()


# connect on safe baudrate, send chunk size and get total number of bytes
ser = serial.Serial(dev, 9600, timeout=10)
ser.write("OK\n".encode("utf-8"))
ser.write((str(args.N)+'\n').encode('utf-8'))

# wait for input
while (not ser.inWaiting()):
	pass

total_bytes_to_receive = int((ser.read_until()).decode('utf-8'))
# send baudrate to test
ser.write((str(args.baudrate)+'\n').encode('utf-8')) 
ser.close()

print("\tTotal bytes to receive = {}, Baudrate = {}".format(total_bytes_to_receive, args.baudrate))

ser = serial.Serial(dev, args.baudrate, timeout=10)

# wait for input
while (not ser.inWaiting()):
	pass

# measure
buffer = [''] * args.N
bytes_in_interval = []
intervals = []
start_time = time()
while ((time() - start_time) < timeout):
	if not ser.inWaiting():
		continue
	reading_start = time()
	buffer = ser.read_until(size = args.N)
	reading_end = time()
    
	bytes_in_interval.append(len(buffer))
	intervals.append(reading_end - reading_start)

	start_time = time()

ser.close()

# calculate
bytes_lost = total_bytes_to_receive - sum(bytes_in_interval)
loss = bytes_lost/total_bytes_to_receive
speeds = np.array(bytes_in_interval)/np.array(intervals)
print("\t Bytes lost = {0:9.3f}%".format(loss*100))

# log results
now = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
f = open(log_dir+args.log_file, "a")
f.write("\n--- {} --- \tBaudrate = {}, expected {} bytes, received {}, loss = {}%".format(now, args.baudrate, total_bytes_to_receive, sum(bytes_in_interval), loss*100))
f.write("\nSpeed measured in intervals of {} bytes, average speed = {} bytes per second".format(args.N, sum(speeds)/len(speeds)))
f.write("\n\t<bytes> \t<time> \t<speed> \n")
for i in range(len(intervals)):
	f.write("\t{}\t{}\t{}\n".format(bytes_in_interval[i], intervals[i], speeds[i]))
f.write('\n')
f.close()
