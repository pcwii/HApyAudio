import PySimpleGUI as sg
from psgtray import SystemTray
import time

import vlc
import time

import os
# import sys, getopt
import json

import threading
import paho.mqtt.client as mqtt

from gtts import gTTS

MACHINE_NAME = os.environ['COMPUTERNAME']

MQTT_COMMAND_TOPIC = MACHINE_NAME + "/HApyAudio/control"
MQTT_BASE_TOPIC = "homeassistant/sensor/" + MACHINE_NAME + "/HApyAudio"
Instance = vlc.Instance()
media_player = Instance.media_player_new()


def main():
    myIcon = "ck_ico.ico"

    menu = ['',
            ['Show Window', 'Hide Window', '---', '!Disabled Item', 'Exit']]
    tooltip = 'HApyAudio'

    layout = [[sg.Text('HApy Audio by PCWii')],
              [sg.T('Closing this window will minimize to tray')],
              [sg.T('Double click the tray icon to restore or right click and choose Show Window')],
              [sg.Multiline(size=(120, 10), reroute_stdout=False, reroute_cprint=True, write_only=True, key='-OUT-')],
              [sg.Button('Go'), sg.B('Hide Icon'), sg.B('Show Icon'), sg.B('Hide Window'), sg.Button('Exit')]]
    window = sg.Window('HApyAudio', layout, finalize=True, enable_close_attempted_event=True, icon=myIcon)
    tray = SystemTray(menu, single_click_events=False, window=window, tooltip=tooltip, icon=myIcon)
    # tray.show_message('System Tray', 'System Tray Icon Started!')
    # sg.cprint(sg.get_versions())
    # Setup and Initialize the MQTT Events
    MQTT_Init()
    while True:
        event, values = window.read()
        # Set event to value from tray
        # if it's a tray event, change the event variable to be whatever the tray sent
        if event == tray.key:
            # sg.cprint(f'System Tray Event = ', values[event], c='white on red')
            event = values[event]  # use the System Tray's event as if was from the window

        if event in (sg.WIN_CLOSED, 'Exit'):
            break

        # sg.cprint(event, values)
        # tray.show_message(title=event, message=values)

        if event in ('Show Window', sg.EVENT_SYSTEM_TRAY_ICON_DOUBLE_CLICKED):
            window.un_hide()
            window.bring_to_front()
        elif event in ('Hide Window', sg.WIN_CLOSE_ATTEMPTED_EVENT):
            window.hide()
            tray.show_icon()  # if hiding window, better make sure the icon is visible
            # tray.notify('System Tray Item Chosen', f'You chose {event}')
        elif event == 'Happy':
            tray.change_icon(sg.EMOJI_BASE64_HAPPY_JOY)
        elif event == 'Sad':
            tray.change_icon(sg.EMOJI_BASE64_FRUSTRATED)
        elif event == 'Plain':
            tray.change_icon(sg.DEFAULT_BASE64_ICON)
        elif event == 'Hide Icon':
            tray.hide_icon()
        elif event == 'Show Icon':
            tray.show_icon()
        elif event == 'Change Tooltip':
            tray.set_tooltip(values['-IN-'])

    tray.close()  # optional but without a close, the icon may "linger" until moused over
    global mqttc
    mqttc.loop_stop()
    window.close()


def load_file(filename):
    with open(filename) as json_file:
        data = json.load(json_file)
        return data


def on_connect(mqttc, obj, flags, rc):
    sg.cprint("rc: " + str(rc))


def parse_message(key, value):
    """
    Examples
    {"command": "pause"}
    {"command": "stop"}
    {"command": "play"}
    ("volume": 100}
    {"play":"http://192.168.0.250:8123/local/mp3/horn.mp3"}
    {"tts": "The quick Brown Fox Jumped Over the Lazy Dog"}
    """
    if "play" in key:
        sg.cprint("Playing...")
        start_playback_thread(value)
    if "tts" in key:
        tts = gTTS(text=value, lang='en')
        tmpFilePath = "c:/temp/file.mp3"
        tts.save(tmpFilePath)
        start_playback_thread(tmpFilePath)
    try:
        PB_Monitor
    except NameError:
        return
    if "command" in key:
        sg.cprint("Recieved Command, " + value)
        if "stop" in value:
            halt_playback_thread()
        if "pause" in value:
            media_player.set_pause(1)
        if "play" in value:
            media_player.set_pause(0)
    if "volume" in key:
        sg.cprint("setting volume to: " + str(value))
        media_player.audio_set_volume(value)


def on_message(mqttc, obj, msg):
    sg.cprint('message received...')
    mqtt_message = str(msg.payload)[2:-1]
    new_message = json.loads(mqtt_message)
    sg.cprint(msg.topic + " " + str(msg.qos) + ", " + mqtt_message)
    for key, value in new_message.items():
        parse_message(key, value)


def on_publish(mqttc, obj, mid):
    sg.cprint("mid: " + str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
    sg.cprint("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    sg.cprint("Log: " + string)


def MQTT_Init():
    settings = load_file("settings.json")
    BROKER_ADDRESS = str(settings["broker_address"])
    BROKER_PORT = int(settings["broker_port"])
    sg.cprint('Control this instance of HApyAudio with the following MQTT Topic...')
    sg.cprint(MQTT_COMMAND_TOPIC)
    mqttConfigPayload = [{
        "name": "HApyAudioStatus",
        "command_topic": MQTT_COMMAND_TOPIC,
        "state_topic": MQTT_BASE_TOPIC + "/state",
        "value_template": "{{value_json.HApyAudioStatus}}"
    }]
    global mqttc
    mqttc = mqtt.Client()
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    mqttc.connect(BROKER_ADDRESS, BROKER_PORT)  # establish connection
    for each_config in mqttConfigPayload:
        sg.cprint('Publishing Configuration for ' + json.dumps(each_config))
        mqttc.publish(MQTT_BASE_TOPIC + "/" + each_config["name"] + "/config", json.dumps(each_config))
        time.sleep(1)
    mqttc.subscribe(MQTT_COMMAND_TOPIC, 0)
    mqttc.loop_start()


def start_playback_thread(value):  # creates the workout thread
    global stop_threads
    stop_threads = False
    global PB_Monitor
    PB_Monitor = threading.Thread(target=playbackThread, args=(value,))
    PB_Monitor.start()


def halt_playback_thread():  # requests an end to the workout
    global stop_threads
    stop_threads = True
    global PB_Monitor
    PB_Monitor.join()


def playbackThread(my_media):
    Media = Instance.media_new(my_media)
    Media.get_mrl()
    media_player.set_media(Media)
    media = media_player.get_media()
    media.parse_with_options(1, 0)
    while True:
        if str(media.get_parsed_status()) == 'MediaParsedStatus.done':
            break  # Might be a good idea to add a failsafe in here.
    sg.cprint(media.get_parsed_status())
    sg.cprint(media.get_duration())
    MediaLength = round(media.get_duration() / 1000)
    sg.cprint(MediaLength)
    media_player.audio_set_volume(75)
    media_player.play()
    time.sleep(2)
    global stop_threads
    while not stop_threads:
        pass
    media_player.stop()


if __name__ == '__main__':
    main()
