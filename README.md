# Ring alarm component
Custom Component for integration with Home Assistant

# Installation
1. Open the directory for your HA configuration where the configuration.yaml file exists
2. If you do not have a custom_components directory (folder) there, you need to create it
3. In the custom_components directory (folder) create a new folder called ring_alarm
4. Download the zip from this repository
5. Place the files you downloaded in the new directory (ring_alarm) you created
6. Restart Home Assistant
 
# Configuration
To be added in the configuration.yaml file, this is your ring alarm username and password

    # configuration.yaml entry
    ring_alarm:     
      username: 'username'
      password: 'password'

# Features
These are the devices supported in the Ring Alarm and need more extensive testing
- Ring lighting
    - Floodlight wired
    - Motion sensor
    - Transformer
    - Others might work but can't test
- Ring security
    - Ring Contact and Motion Sensors
    - Ring Flood/Freeze Sensor 
    - Ring Smoke/CO Listener - Possibly supports, can't test
    - First Alert Z-Wave Smoke/CO Detector - testing needed)
    - Ring Alarm integrated door locks (status and lock control)
    - Ring Alarm Panel (Arm, Disarm, Home)

In addition the following attributes are available:
- Battery level, if available
- Tamper status for supported devices 
- Location name
- ZID (its a unique id that each Ring device has)
- Last update received from the device
 
# Issues
This component uses some other python modules, all of them install automatically except for python-socketio which I install within the component. 
Once I trace the problem will try to remove the manual installation. Not sure if this creates problems in Hassio since i use the installed python to install the pip modules

Assume these are all in need of extensive testing and not be dependent solely on the status produced by this compoonent