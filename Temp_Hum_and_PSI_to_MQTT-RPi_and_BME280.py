import RPi.GPIO as GPIO
import smbus2
import datetime
import time
import paho.mqtt.client as mqtt
import bme280
import sys
import subprocess
import os
import rssi
import yaml

def config(file_path):
    with open(file_path, 'r') as f:
        print('Config Successful')
        return yaml.safe_load(f)

config = config('/home/kevin/Desktop/pi_config.yaml')

########## Config Stuff #############
ssid = config['SECRETS']['SSID']
mqtt_server = config['SECRETS']['MQTT_SERVER']
client_name = config['SECRETS']['CLIENT_NAME']
mqtt_port = config['SECRETS']['MQTT_PORT']
t1 = config['SECRETS']['T1']
t2 = config['SECRETS']['T2']
interface = config['SECRETS']['INTERFACE']
#####################################

lwt = f'The {client_name} is Offline'
start_time = datetime.datetime.now()
#rssi_scanner = rssi.RSSI_Scan(interface)
DEVICE = 0x76 # Default device I2C address
client = mqtt.Client(client_name)
BUS = smbus2.SMBus(1)
mqtt.Client.connected_flag = False

count = 0
temp_day_count = 0
hum_day_count = 0
psi_day_count = 0
rssi_day_count = 0
avg_t_plus_t = 0
avg_t = 0
avg_t_plus_t_today = 0
avg_t_today = 0
max_t = 0
max_t_today = 0
min_t = 300
min_t_today = 300
avg_h_plus_h = 0
avg_h = 0
avg_h_plus_h_today = 0
avg_h_today = 0
max_h = 0
max_h_today = 0
min_h = 100
min_h_today = 100
avg_p_plus_p = 0
avg_p = 0
avg_p_plus_p_today = 0
avg_p_today = 0
max_p = 0
max_p_today = 0
min_p = 2000
min_p_today = 2000
avg_rssi_plus_rssi = 0
avg_rssi = 0
avg_r_plus_r_today = 0
avg_r_today = 0
max_rssi = 100
max_r_today = 100
min_rssi = -100
min_r_today = -100
motion_pin = 32
motion_count = 0

def on_publish(topic, payload = None, qos = 0, retained = False):
    if topic == f'{t1}/{t2}/motion':
        print(f'topic: {topic}')
        print(f'payload: {payload}')

def on_connect(client, userdata, flags, rc):
    print('Setting up MQTT...')
    print(f'Connected flags {flags}. Return code {rc} client_id')
    loop_flag = 0
    if rc == 0:
        client.connected_flag = True
        print(f'Connected to MQTT Server. Return code: {rc}')
    else:
        print(f'Not Connected to MQTT Server. Return code: {rc}')

def on_disconnect(client, userdata, rc):
    print('MQTT Disconnected...')
    print(f'Return code {rc}')
    loop_flag = 0
    if rc != 0:
        client.connected_flag = False
        print(f'Not Connected to MQTT Server. Return code: {rc}')
        try:
            mqtt_conn = client.connect(mqtt_server, mqtt_port, keepalive = 60)#RP5180
        except OSError as e:
            print(e)
    else:
        print(f'Connected to MQTT Server. Return code: {rc}')

def last_will_msg():
    print(f'Setting last will message to "{lwt}"')
    client.will_set(f'{t1}/{t2}/lwt', lwt, qos = 1, retain = False)

def day():
    day = datetime.datetime.now().strftime("%A")
    print(f'Day of the Week: {day}')
    client.publish(f'{t1}/{t2}/day', day)

def elapsed_time():
    elapsed_time_since_start = str(datetime.datetime.now() - start_time)
    print(f'Elapsed time: {elapsed_time_since_start[:-10]}')
    client.publish(f'{t1}/{t2}/elapsedTime', elapsed_time_since_start[:-10])
#    return elapsed_time_since_start

def date():
    date = datetime.datetime.now().strftime('%m/%d/%Y')
    print(f'Date: {date}')
    client.publish(f'{t1}/{t2}/date', date)

def timeOfDay():
    time = datetime.datetime.now().strftime('%H:%M:%S')
    print(f'Time of Day: {time}')
    client.publish(f'{t1}/{t2}/time', time)

def cycleCounter():
    print(f'Cycle Counter: {count}')
    client.publish(f'{t1}/{t2}/dataPts', count)
    
def temp():
    temperature = bme_data.temperature
    temperature = (temperature * 9 / 5) + 32
    t = round(temperature, 2)
    print(f'Temperature: {t}F')
    client.publish(f'{t1}/{t2}/temp', t)
    return t

def calcAvgTemp(t):
    global avg_t_plus_t
    global avg_t
    avg_t_plus_t += t
    if count == 1:
        avg_t = t
    else:
        avg_t = round(avg_t_plus_t / count, 2)
    print(f'Avg Temperature: {avg_t}F')
    client.publish(f'{t1}/{t2}/avgTemp', avg_t)
    return avg_t

def calcAvgTempToday(t):
    global avg_t_plus_t_today
    global avg_t_today
    global temp_day_count
    avg_t_plus_t_today += t
    if datetime.datetime.now().strftime("%H") == '00' and datetime.datetime.now().strftime("%M") == '00':
        avg_t_today = t
        avg_t_plus_t_today = 0
        temp_day_count = 0
    else:
        temp_day_count += 1
        avg_t_today = round(avg_t_plus_t_today / temp_day_count, 2)
    print(f'Avg Temperature Today: {avg_t_today}F')
    client.publish(f'{t1}/{t2}/avgTempToday', avg_t_today)
    return avg_t_today

def calcMaxTemp(t):
    global max_t
    max_t = max(max_t, t)
    print(f'Max Temperature: {max_t}F')
    client.publish(f'{t1}/{t2}/maxTemp', max_t)
    
def calcMaxTempToday(t):
    global max_t_today
    if datetime.datetime.now().strftime("%H") == '00' and datetime.datetime.now().strftime("%M") == '00':
        max_t_today = t
    else:
        max_t_today = max(max_t_today, t)
    print(f'Max Temperature Today: {max_t_today}F')
    client.publish(f'{t1}/{t2}/maxTempToday', max_t_today)
    
def calcMinTemp(t):
    global min_t
    min_t = min(min_t, t)
    print(f'Min Temperature: {min_t}F')         
    client.publish(f'{t1}/{t2}/minTemp', min_t)

def calcMinTempToday(t):
    global min_t_today
    if datetime.datetime.now().strftime("%H") == '00' and datetime.datetime.now().strftime("%M") == '00':
        min_t_today = t
    else:
        min_t_today = min(min_t_today, t)
    print(f'Min Temperature Today: {min_t_today}F')
    client.publish(f'{t1}/{t2}/minTempToday', min_t)
    
def hum():
    humidity = bme_data.humidity
    h = round(humidity, 2)
    print(f'Humidity: {h}%')
    client.publish(f'{t1}/{t2}/hum', h)
    return h

def calcAvgHum(h):
    global avg_h_plus_h
    global avg_h
    avg_h_plus_h += h
    if count == 1:
        avg_h = h
    else:
        avg_h = round(avg_h_plus_h / count, 2)
    print(f'Avg Humidity: {avg_h}%')
    client.publish(f'{t1}/{t2}/avgHum', avg_h)
    return avg_h

def calcAvgHumToday(h):
    global avg_h_plus_h_today
    global avg_h_today
    global hum_day_count
    avg_h_plus_h_today += h
    if datetime.datetime.now().strftime("%H") == '00' and datetime.datetime.now().strftime("%M") == '00':
        avg_h_today = h
        avg_h_plus_h_today = 0
        hum_day_count = 0
    else:
        hum_day_count += 1
        avg_h_today = round(avg_h_plus_h_today / hum_day_count, 2)
    print(f'Avg Humidity Today: {avg_h_today}%')
    client.publish(f'{t1}/{t2}/avgHumToday', avg_h_today)
    return avg_h_today

def calcMaxHum(h):
    global max_h
    max_h = max(max_h, h)
    print(f'Max Humidity: {max_h}%')
    client.publish(f'{t1}/{t2}/maxHum', max_h)

def calcMaxHumToday(h):
    global max_h_today
    if datetime.datetime.now().strftime("%H") == '00' and datetime.datetime.now().strftime("%M") == '00':
        max_h_today = h
    else:
        max_h_today = max(max_h_today, h)
    print(f'Max Humiduty Today: {max_h_today}%')
    client.publish(f'{t1}/{t2}/maxHumToday', max_h_today)
    
def calcMinHum(h):
    global min_h
    min_h = min(min_h, h)
    print(f'Min Humidity: {min_h}%')        
    client.publish(f'{t1}/{t2}/minHum', min_h)

def calcMinHumToday(h):
    global min_h_today
    if datetime.datetime.now().strftime("%H") == '00' and datetime.datetime.now().strftime("%M") == '00':
        min_h_today = h
    else:
        min_h_today = min(min_h_today, h)
    print(f'Min Humidity Today: {min_h_today}%')
    client.publish(f'{t1}/{t2}/minHumToday', min_h)
    
def psi():
    pressure = bme_data.pressure
    p = round(pressure, 2)
    print(f'Pressure: {p}hPa')
    client.publish(f'{t1}/{t2}/psi', p)
    return p

def calcAvgPsi(p):
    global avg_p_plus_p
    global avg_p
    avg_p_plus_p += p
    if count == 1:
        avg_p = p
    else:
        avg_p = round(avg_p_plus_p / count, 2)
    print(f'Avg Pressure: {avg_p}hPa')
    client.publish(f'{t1}/{t2}/avgPsi', avg_p)
    return avg_p

def calcAvgPsiToday(p):
    global avg_p_plus_p_today
    global avg_p_today
    global psi_day_count
    avg_p_plus_p_today += p
    if datetime.datetime.now().strftime("%H") == '00' and datetime.datetime.now().strftime("%M") == '00':
        avg_p_today = p
        avg_p_plus_p_today = 0
        psi_day_count = 0
    else:
        psi_day_count += 1
        avg_p_today = round(avg_p_plus_p_today / psi_day_count, 2)
    print(f'Avg Pressure Today: {avg_p_today}hPa')
    client.publish(f'{t1}/{t2}/avgPsiToday', avg_p_today)
    return avg_p_today

def calcMaxPSI(p):
    global max_p
    max_p = max(max_p, p)
    print(f'Max Pressure: {max_p}hPa')
    client.publish(f'{t1}/{t2}/maxPsi', max_p)
    
def calcMaxPsiToday(p):
    global max_p_today
    if datetime.datetime.now().strftime("%H") == '00' and datetime.datetime.now().strftime("%M") == '00':
        max_p_today = p
    else:
        max_p_today = max(max_p_today, p)
    print(f'Max Pressure Today: {max_p_today}hPa')
    client.publish(f'{t1}/{t2}/maxPsiToday', max_p_today)
    
def calcMinPSI(p):
    global min_p
    min_p = min(min_p, p)
    print(f'Min Pressure: {min_p}hPa')
    client.publish(f'{t1}/{t2}/minPsi', min_p)

def calcMinPsiToday(p):
    global min_p_today
    if datetime.datetime.now().strftime("%H") == '00' and datetime.datetime.now().strftime("%M") == '00':
        min_p_today = p
    else:
        min_p_today = min(min_p_today, p)
    print(f'Min Pressure Today: {min_p_today}hPa')
    client.publish(f'{t1}/{t2}/minPsiToday', min_p_today)
    
def rssi():
    command = 'iw wlan0 station dump | grep signal'
    try:
        sub_proc = subprocess.check_output(command, shell = True).decode('utf-8')
    except TypeError as e:
        print(e)
    except subprocess.CalledProcessError:
        dbm = f'-100'
    except:
        dbm = '-99'
    else:
        dbm = sub_proc[-8:-5]
        print(f'RSSI: {dbm}dBm')
        client.publish(f'{t1}/{t2}/rssi', dbm)
    return int(dbm)

def calcAvgRssi(rssi):
    global avg_rssi_plus_rssi
    global avg_rssi
    avg_rssi_plus_rssi += rssi
    if count == 1:
        avg_rssi = rssi
    else:
        avg_rssi = round(avg_rssi_plus_rssi / count, 1)
    print(f'Avg RSSI: {avg_rssi}dBm')
    client.publish(f'{t1}/{t2}/avgRssi', avg_rssi)
    return avg_rssi

def calcAvgRssiToday(rssi):
    global avg_r_plus_r_today
    global avg_r_today
    global rssi_day_count
    avg_r_plus_r_today += rssi
    if datetime.datetime.now().strftime("%H") == '00' and datetime.datetime.now().strftime("%M") == '00':
        avg_r_today = rssi
        avg_r_plus_r_today = 0
        rssi_day_count = 0
    else:
        rssi_day_count += 1
        avg_r_today = round(avg_r_plus_r_today / rssi_day_count, 1)
    print(f'Avg RSSI Today: {avg_r_today}dBm')
    client.publish(f'{t1}/{t2}/avgRssiToday', avg_r_today)
    return avg_r_today

def calcMaxRssi(rssi):
    global max_rssi
    max_rssi = min(max_rssi, rssi)
    print(f'Max RSSI: {max_rssi}dBm')
    client.publish(f'{t1}/{t2}/maxRssi', max_rssi)
    
def calcMaxRssiToday(rssi):
    global max_r_today
    if datetime.datetime.now().strftime("%H") == '00' and datetime.datetime.now().strftime("%M") == '00':
        max_r_today = rssi
    else:
        max_r_today = min(max_r_today, rssi)
    print(f'Max RSSI Today: {max_r_today}dBm')
    client.publish(f'{t1}/{t2}/maxRssiToday', max_r_today)
    
def calcMinRssi(rssi):
    global min_rssi
    min_rssi = max(min_rssi, rssi)
    print(f'Min RSSI: {min_rssi}dBm')
    client.publish(f'{t1}/{t2}/minRssi', min_rssi)

def calcMinRssiToday(rssi):
    global min_r_today
    if datetime.datetime.now().strftime("%H") == '00' and datetime.datetime.now().strftime("%M") == '00':
        min_r_today = rssi
    else:
        min_r_today = max(min_r_today, rssi)
    print(f'Min RSSI Today: {min_r_today}dBm')
    client.publish(f'{t1}/{t2}/minRssiToday', min_r_today)

def motion_counter():
    print(f'Motion Count: {motion_count}')
    client.publish(f'{t1}/{t2}/motionCount', motion_count)

def motion():
    global motion_count
    if GPIO.input(motion_pin) == 1:
        motion_count += 1
        print(f'\nmotion has been detected ({motion_count})')
        client.publish(f'{t1}/{t2}/motion', 'motion')
        return True

last_will_msg()
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(motion_pin, GPIO.IN)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
#client.on_publish = on_publish
client.loop_start()

wait = ''
# while not client.connected_flag:
#     wait += '.'
#     print(wait)
#     time.sleep(1)
#     mqtt_conn = client.connect(mqtt_server, mqtt_port, keepalive = 60)#RP5180

try:
    mqtt_conn = client.connect(mqtt_server, mqtt_port, keepalive = 60)#RP5180
except OSError as e:
    print(e)

while True:

    print(f'Client Connected: {client.connected_flag}')
    
    if not client.connected_flag:
        wait += '.'
        print(wait)
        time.sleep(1)
        try:
            mqtt_conn = client.connect(mqtt_server, mqtt_port, keepalive = 60)#RP5180
        except OSError as e:
            print(e)

    else:
        try:
            bme_data = bme280.sample(BUS, DEVICE)
            count += 1
            print()
            print()
            cycleCounter()
            day()
            elapsed_time()
            date()
            timeOfDay()
            t = temp()
            calcAvgTemp(t)
            calcAvgTempToday(t)
            calcMaxTemp(t)
            calcMaxTempToday(t)
            calcMinTemp(t)
            calcMinTempToday(t)
            h  = hum()
            calcAvgHum(h)
            calcAvgHumToday(h)
            calcMaxHum(h)
            calcMaxHumToday(h)
            calcMinHum(h)
            calcMinHumToday(h)
            p = psi()
            calcAvgPsi(p)
            calcAvgPsiToday(p)
            calcMaxPSI(p)
            calcMaxPsiToday(p)
            calcMinPSI(p)
            calcMinPsiToday(p)
            r = rssi()
            calcAvgRssi(r)
            calcAvgRssiToday(r)
            calcMaxRssi(r)
            calcMaxRssiToday(r)
            calcMinRssi(r)
            calcMinRssiToday(r)
            motion_counter()
        #    time.sleep(60)

            motion_timer = 0
            while motion_timer < 120:
                if motion():
                    motion_timer += 6
                    time.sleep(3)
                time.sleep(.5)
                motion_timer += 1

        except OSError:
            subprocess.call('sudo shutdown', shell=True)