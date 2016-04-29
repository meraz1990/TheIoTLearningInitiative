#!/usr/bin/python

import paho.mqtt.client as paho
import psutil
import pywapi
import signal
import sys
import time
import string
import dweepy



############################
from flask import Flask
from flask_restful import Api, Resource
############################



from threading import Thread

import plotly.plotly as py
from plotly.graph_objs import Scatter, Layout, Figure

username = 'TheIoTLearningInitiative'
api_key = 'twr0hlw78c'
stream_token = '2v04m1lk1x'

def GetMACAddress():
	myMAC = open('/sys/class/net/wlan0/address').read()
	return myMAC[0:17]

idDevice = GetMACAddress()

def interruptHandler(signal, frame):
    sys.exit(0)

def on_publish(mosq, obj, msg):
    pass

def dataNetwork():
    netdata = psutil.net_io_counters()
    return netdata.packets_sent + netdata.packets_recv

def dataNetworkHandler():

    mqttclient = paho.Client()
    mqttclient.on_publish = on_publish
    mqttclient.connect("test.mosquitto.org", 1883, 60)
    while True:
        packets = dataNetwork()
        message = idDevice + " " + str(packets)
        print "MQTT dataNetworkHandler " + message
        mqttclient.publish("IoT101/" + idDevice + "/Network", message)
        time.sleep(1)

def on_message(mosq, obj, msg):
    print "MQTT dataMessageHandler %s %s" % (msg.topic, msg.payload)


def dataMessageHandler():
    mqttclient = paho.Client()
    mqttclient.on_message = on_message
    mqttclient.connect("test.mosquitto.org", 1883, 60)
    mqttclient.subscribe("IoT101/" + idDevice + "/Message", 0)
    while mqttclient.loop() == 0:
        pass

def dataWeatherHandler():
    weather = pywapi.get_weather_from_weather_com('MXJO0043', 'metric')
    message = "Weather Report in " + weather['location']['name']
    message = message + ", Temperature " + weather['current_conditions']['temperature'] + " C"
    message = message + ", Atmospheric Pressure " + weather['current_conditions']['barometer']['reading'][:-3] + " mbar"
    print message


def dataPlotly():
    return dataNetwork()

def dataPlotlyHandler():

    py.sign_in(username, api_key)

    trace1 = Scatter(
        x=[],
        y=[],
        stream=dict(
            token=stream_token,
            maxpoints=200
        )
    )

    layout = Layout(
        title='Hello Internet of Things 101 Data'
    )

    fig = Figure(data=[trace1], layout=layout)

    print py.plot(fig, filename='Hello Internet of Things 101 Plotly')

    i = 0
    stream = py.Stream(stream_token)
    stream.open()

    while True:
        stream_data = dataPlotly()
        stream.write({'x': i, 'y': stream_data})
        i += 1
        time.sleep(0.25)

################################

app = Flask(__name__)
api = Api(app)

class Network(Resource):
    def get(self):
        data = dataNetwork()
        return data

api.add_resource(Network, '/network')

##################################
	


if __name__ == '__main__':

    
	
    app.run(host='0.0.0.0', debug=True)

    signal.signal(signal.SIGINT, interruptHandler)

    threadx = Thread(target=dataNetworkHandler)
    threadx.start()

    thready = Thread(target=dataMessageHandler)
    thready.start()

    threadz = Thread(target=dataPlotlyHandler)
    threadz.start()
    
    dataWeatherHandler()
        

    while True:
        
        json= {'network':dataNetwork()}
        dweepy.dweet_for('meraz1990', json)
        print "Hello Internet of Things 101"
        time.sleep(5)

# End of File
