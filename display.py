#!/usr/bin/python

import Adafruit_BBIO.GPIO as GPIO
import time,sys,string,json,urllib2

#Set segment pin
#[[e,d,c,g,b,f,a],[1,2,3,4](from left to right)], display1 is 4-digit for showing bus route while display2 is 2-digit indicating the time (in mins) for the next bus.
display1 = [[ "P8_11","P8_12","P8_13","P8_14","P8_15","P8_16","P8_17" ],[ "P8_10","P8_9","P8_8","P8_7" ]]
display2 = [[ "P9_11","P9_12","P9_13","P9_14","P9_15","P9_16","P9_23" ],[ "P9_22","P9_21" ]]
#Set up all pins
for pinGroup in display1 + display2:
	for pin in pinGroup:	
		GPIO.setup(pin,GPIO.OUT)
#define legal character set
charSet = {}
charSet['A'] = [1,0,1,1,1,1,1]
charSet['C'] = [1,1,0,0,0,1,1]
charSet['E'] = [1,1,0,1,0,1,1]
charSet['F'] = [1,0,0,1,0,1,1]
charSet['H'] = [1,0,1,1,1,1,0]
charSet['L'] = [1,1,0,0,0,1,0]
charSet['P'] = [1,0,0,1,1,1,1]
charSet['U'] = [1,1,1,0,1,1,0]
charSet['ERR'] = [0,0,0,1,0,0,0]
charSet['NULL'] = [0,0,0,0,0,0,0]
charSet['0'] = [1,1,1,0,1,1,1]
charSet['1'] = [0,0,1,0,1,0,0]
charSet['2'] = [1,1,0,1,1,0,1]
charSet['3'] = [0,1,1,1,1,0,1]
charSet['4'] = [0,0,1,1,1,1,0]
charSet['5'] = [0,1,1,1,0,1,1]
charSet['6'] = [1,1,1,1,0,1,1]
charSet['7'] = [0,0,1,0,1,0,1]
charSet['8'] = [1,1,1,1,1,1,1]
charSet['9'] = [0,1,1,1,1,1,1]

#Set refresh time for each digit interval for the display
refreshInterval=0
#Set the time interval for updating the  data
updateInterval=60
#Set tcp connection timeout
tcpTimeout=10

def displayDigit(segmentArr,display):
	for i in range(0,len(segmentArr)):
		pinId=display[0][i]
		if segmentArr[i] == 1:
			GPIO.output(pinId, GPIO.HIGH)
		else:
			GPIO.output(pinId, GPIO.LOW)

def selectDigit(digitArr,display):
	for i in range(0,len(digitArr)):
		comPinId = display[1][i]
		if digitArr[i] == 1:
			GPIO.output(comPinId, GPIO.LOW)
		else:
			GPIO.output(comPinId, GPIO.HIGH)
def display(content,numMode):
	if numMode == 1: #Show number on display2(2 digit number at most) 
		display = display2
	else: #Show String on display1(4 digit at most)
		display = display1
	size = len(display[1])
        digitArr = [[ 0 for i in range(size)] for j in range(size)] #initialize all digit by zeros(display nothing)
        for i in range(len(content)):
                if numMode == 1: #To display number from right to left
                        key = size - i - 1
                else: #To display characters from left to right
                        key = i
                digitArr[key][key] = 1 #set digit to display

	contentArr = [[ 0 for i in range(len(display[0]))] for j in range(size)]#initialize all segments by zeros(display nothing)
	if numMode == 1:
		if content.isdigit() and len(content) <= 2:
			for i in range(len(content),0,-1):
				contentArr[i-1] = charSet[content[i-1]]
			if len(content) < size:
				contentArr.reverse()
		else:
			# display '99' on the two digit display if the number >= 100 
			contentArr=[charSet['9'], charSet['9']]
	else: #numMode = 0, show string on display1
		for i in range(len(content)):
			if charSet.has_key(content[i]):
				contentArr[i] = charSet[content[i]]
			else:
				#All other characters can not be shown properlly on the display, so display a '-' 
				contentArr[i] = charSet['ERR']
	
	#Now we get digitArr and contentArr ready for displaying	
	for i in range(size):
		selectDigit(digitArr[i],display)
		displayDigit(contentArr[i],display)
		time.sleep(refreshInterval)
		displayDigit(charSet['NULL'],display)
		
def getData():
	# this should be the <input name='vote[email]'> in the page
	result = []
	stopId=sys.argv[1]
	url = 'http://realtime.adelaidemetro.com.au/SiriWebServiceSAVM/SiriStopMonitoring.svc/json/SM?MonitoringRef='+stopId+'&LineRef=&PreviewInterval=30&StartTime=&DirectionRef=&StopMonitoringDetailLevel=normal&MaximumStopVisits=20&Item=1'
	req = urllib2.urlopen(url,timeout=tcpTimeout)
	data=req.read()
	decoded_data=json.loads(data)
	nextLines = decoded_data["StopMonitoringDelivery"][0]["MonitoredStopVisit"]
	timeNow=int(time.time()*1000) 
	for i in range(len(nextLines)):
		busNumber = nextLines[i]["MonitoredVehicleJourney"]["LineRef"]["Value"]
		expectedTimeString=nextLines[i]["MonitoredVehicleJourney"]["MonitoredCall"]["LatestExpectedArrivalTime"]
		destinationName=nextLines[i]["MonitoredVehicleJourney"]["DestinationName"][0]["Value"]
		expectedTime = int(expectedTimeString.replace("+0930)/","").replace("/Date(",""))
		expectedArrivalMin = int((expectedTime-timeNow)/1000/60)
		#print busNumber,expectedArrivalMin,destinationName
		result.append([busNumber,expectedArrivalMin])

	return result

	#return [['196F',12],['H20',50],['286',812],['200E',4],['300B',5],['12',6],['1234',7],['130B',8],['286H',9],['1234',10]]

def showOne(record,interval):
	now = time.time()
	while (time.time() - now) < interval :
		display(str(record[0]),numMode=0)
		display(str(record[1]),numMode=1)

def mainLoop(): 	
	log = open("display.log",'w+')
	while 1:
		try:
			resultArr = getData()
		except:
			print "Error : No results returned, sleep 60"
			log.write("%s: No results returned, sleep 60\n" % str(time.time()))
			log.flush()
			time.sleep(60)
			continue
		interval = updateInterval / len(resultArr)
		print resultArr
		log.write("%s:\t%s\n" % (str(time.time()),str(resultArr)))
		log.flush()
		for record in resultArr:
			showOne(record,interval)

if __name__ == "__main__":
	mainLoop()
	GPIO.cleanup()
