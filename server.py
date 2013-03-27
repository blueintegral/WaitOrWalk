#! /usr/bin/env python
import os
from BeautifulSoup import BeautifulSoup, SoupStrainer
from urllib import urlopen
import urllib
import urllib2
import string
import sys
import time
import re
from datetime import datetime
from flask import Flask, render_template, request
import subprocess
import json
from v2methods import *
app= Flask(__name__)

thetime = time.time()
cold = 0
rainy = 0


@app.route('/')
def index():
	return render_template('index.html')	

@app.route('/how')
def how():
	return render_template('how.html')

@app.route('/weather')
def weather():
	#Check current conditions every 5 minutes
	global thetime
	global cold
	global rainy
	if(time.time() - thetime > 300):
		thetime = time.time() #reset timer
		f = urllib2.urlopen('http://api.wunderground.com/api/your-api-key-here/conditions/q/30332.json')
		json_string = f.read()
		parsed_json = json.loads(json_string)
		temperature = parsed_json['current_observation']['temp_f']
		if(temperature < 60):
			cold = 1 #it's cold
		conditions = parsed_json['current_observation']['weather']
		if(conditions == 'Light Drizzle' or conditions == 'Heavy Drizzle' or conditions == 'Light Rain' or conditions == 'Heavy Rain' or conditions == 'Light Hail' or conditions == 'Heavy Hail' or conditions == 'Light Rain Mist' or conditions == 'Heavy Rain Mist' or conditions == 'Light Rain Showers' or conditions == 'Heavy Rain Showers' or conditions == 'Light Hail Showers' or conditions == 'Heavy Hail Showers' or conditions == 'Light Small Hail Showers' or conditions == 'Heavy Small Hail Showers' or conditions == 'Light Thunderstorm' or conditions == 'Heavy Thunderstorm' or conditions == 'Light Thunderstorms and Rain' or conditions == 'Heavy Thunderstorms and Rain' or conditions == 'Light Thunderstorms with Hail' or conditions == 'Heavy Thunderstorms with Hail' or conditions == 'Light Thunderstorms with Small Hail' or conditions == 'Heavy Thunderstorms with Small Hail' or conditions == 'Light Freezing Drizzle' or conditions == 'Heavy Freezing Drizzle' or conditions == 'Light Freezing Rain' or conditions == 'Heavy Freezing Rain' or conditions == 'Small Hail'):
			rainy = 1 #it's raining	
	if(rainy):
		return str(1)
	elif(cold):
		return str(2)
	else:
		return str(0)


@app.route('/shouldwait')
def start_api():
	if (not ('start' in request.args and 'end' in request.args)):
		return
	#the page has passed both a start and end point
	start_tag = request.args['start']
	end_tag = request.args['end']
	start_title = stop_tag_to_stop_title(start_tag)
	end_title = stop_tag_to_stop_title(end_tag)

	(route_tag, direction_tag) = getRoute(start_title, end_title)

	result = shouldWait(start_tag, end_tag, route_tag, direction_tag)
	wait_time = get_NextBus_time(start_tag, direction_tag, route_tag)
	return  ' '.join([str(result), str(wait_time)])

def getRoute(start_title, end_title):
	return get_possible_routes_and_directions(start_title, end_title)

def shouldWait(start_tag, end_tag, route_tag, direction_tag):

	'''Actually makes the decision to wait or walk '''
	#First get the time until next bus
	waitTime = get_NextBus_time(start_tag, direction_tag, route_tag)
	#Now add drive time to that. This should also include amount of time spent at stops.
	#Add an extra 15 seconds per stop made on the way
	driveTime = get_time(start_tag, end_tag, "driving") 
	stops = stops_between(start_tag, end_tag, route_tag, direction_tag)
	waitTime = waitTime + driveTime +  0.25*stops #that's .25 minutes
	#Get walk time
	walkTime = get_time(start_tag, end_tag, "walking")
	#compare two times
	if(waitTime < walkTime):
		return 1
	else:
		return 0

def get_time(start, end, method):
	#Get distance matrix for this trip
	json_data = open("data/"+method+"/"+start+".json").read()
	data = json.loads(json_data)
	#figure out destination number
	if(end == "fitten"):
		end = 0
	if(end == "mcm8th"):
		end = 1
	if(end == "8thhemp"):
		end = 2
	if(end == "fershemrt"):
		end = 3
	if(end == "fersstmrt"):
		end = 4
	if(end == "fersatmrt"):
		end = 5
	if(end == "ferschmrt"):
		end = 6
	if(end == "5thfowl"):
		end = 7
	if(end == "tech5th"):
		end = 8
	if(end == "tech4th"):
		end = 9
	if(end == "techbob"):
		end = 10
	if(end == "technorth"):
		end = 11
	if(end == "nortavea_a"):
		end = 12
	if(end == "ferstcher"):
		end = 13
	if(end == "hubfers"):
		end = 14
	if(end == "centrstud"):
		end = 15
	if(end == "765femrt"):
		end = 16
		
	expectedTime = data["rows"][0]["elements"][end]["duration"]["value"]
	expectedTime = int(expectedTime)/60 #convert to minutes
	
	return expectedTime

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 80))
	app.debug = os.environ.get('DEBUG', True)
	app.logger.info("Debug is set to: %s" % app.debug)
	app.run(host='0.0.0.0', port=port)

