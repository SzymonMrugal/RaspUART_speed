'''
	UART communication, server side
	send random bytes in order to measure connection speed at client side
'''

import argparse
import serial
import time
import random
import string

dev = "/dev/ttyS0"

par = argparse.ArgumentParser()
par.add_argument('-n', dest="chunks", type=int, default=10)
args = par.parse_args()


while True:
	# connect on safe baudrate, get chunk size and send total number of bytes
	ser = serial.Serial(dev, 9600)
	if (ser.read_until().decode('utf-8') != "OK\n"):
		break
	chunks_size = int(ser.read_until().decode('utf-8'))
	ser.write((str(args.chunks*chunks_size) + '\n').encode('utf-8'))
	baudrate = int((ser.read_until()).decode('utf-8'))
	ser.close()

	print("\tBaudrate = {}, sending total of {} bytes".format(baudrate, args.chunks*chunks_size))
	print()

	time.sleep(0.1)
	# connect on new baudrate for testing
	ser = serial.Serial(dev, baudrate)

	# generate random bytes to send, size is (args.chunks * chunks_size)
	sampleData = ''.join((random.choice(string.ascii_letters) for i in range(args.chunks*chunks_size - 1)))
	sampleData += '\n'

	ser.write(sampleData.encode('utf-8'))

	ser.close()
