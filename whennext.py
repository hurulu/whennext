#!/usr/bin/env python
import time,string,json,sys,urllib

def main():
	# this should be the <input name='vote[email]'> in the page
	stopId=sys.argv[1]
	req = urllib.urlopen('http://realtime.adelaidemetro.com.au/SiriWebServiceSAVM/SiriStopMonitoring.svc/json/SM?MonitoringRef='+stopId+'&LineRef=&PreviewInterval=30&StartTime=&DirectionRef=&StopMonitoringDetailLevel=normal&MaximumStopVisits=20&Item=1')
	data=req.read()
	decoded_data=json.loads(data)
	nextLines = decoded_data["StopMonitoringDelivery"][0]["MonitoredStopVisit"]
	timeNow=int(time.time()*1000) 
	for i in range(len(nextLines)):
		busNumber = nextLines[i]["MonitoredVehicleJourney"]["LineRef"]["Value"]
		expectedTimeString=nextLines[i]["MonitoredVehicleJourney"]["MonitoredCall"]["LatestExpectedArrivalTime"]
		expectedTime = int(expectedTimeString.replace("+0930)/","").replace("/Date(",""))
		expectedArrivalMin = int((expectedTime-timeNow)/1000/60)
		print busNumber,expectedArrivalMin

if __name__ == "__main__":
    	main()
