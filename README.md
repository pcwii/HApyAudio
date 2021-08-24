# HApyAudio
Utilize the lightweight MQTT protocol to create a Home Assistant notification Daemon
for Windows PC's.

## Usage
Edit the settings.json file with your broker and port address.
When the interface loads it will reveal the topic that can be used to push MQTT commands to the software.
<MACHINE_NAME>HApyAudio/control
<img src='/images/gui.png' width='100' height='64' style='vertical-align:bottom'/> 
## Examples
|   Key   	|                          Value                          	|                           Sample Payload                           	| Description                                 	|
|:-------:	|:-------------------------------------------------------:	|:------------------------------------------------------------------:	|---------------------------------------------	|
| command 	|                          pause                          	|                        {"command": "pause"}                        	| Pauses the Audio Playback                   	|
| command 	|                           stop                          	|                         {"command": "stop"}                        	| Stops the Audio Playback                    	|
| command 	|                           play                          	|                         {"command": "play"}                        	| Resumes Paused Audio                        	|
|  volume 	|                          0-100                          	|                           ("volume": 100}                          	| Sets the Playback Volume                    	|
|   play  	| https://www.myinstants.com/media/sounds/mlg-airhorn.mp3 	| {"play":"https://www.myinstants.com/media/sounds/mlg-airhorn.mp3"} 	| Plays the source Audio File                 	|
|   tts   	|       The quick Brown Fox Jumped Over the Lazy Dog      	|       {"tts": "The quick Brown Fox Jumped Over the Lazy Dog"}      	| Uses Google TTS services to speak the value 	|
|         	|                                                         	|                                                                    	|                                             	|

## About
This program will monitor for MQTT messages sent to the configured Topic

## Credits
pcwii

## Category
**IoT**
**Home Assistant**

## Tags
#plc
#HA
#control
#MQTT
#broker
#Homeassistant
#openHAB

## Requirements
- Windows
- you must have an active MQTT Broker
- [vlc](https://www.videolan.org/vlc/)
- [paho-mqtt](https://pypi.org/project/paho-mqtt/).

## Warnings!!
- I do NOT recommended to using a public MQTT broker as this could expose your commands to other devices subscribing to your topic.