# Live Telemetry 1.4.1

An Assetto Corsa app to view real time telemetry

## App

The app show on screen real time telemetry of engine, each tire and suspension individually. The goal with this app is not to replace the Assetto Corsa built-in apps with these information, but to help developing better setups more efficiently.

The app uses the mod file directly or the encrypted Kunos files to calculate it's limits, does not need configuration.

[![Screen-shot](https://raw.githubusercontent.com/albertowd/live-telemetry/master/resources/screenshot.jpg)](https://www.youtube.com/watch?v=KI4pK0c7n1Q)

### Telemetry Info

   - Engine Ideal RPM/Power
   - Suspension height (mm)
   - Suspension travel (%): gets warning yellow above 95% and danger red above 98% of the maximum and minimum values
   - Tire pressure (psi)
   - Tire core, inner, middle and outer temperatures (ºC)
   - Tire load (N)
   - Tire wear: bar gets warning yellow below 98% and danger red below 96%
   - Wheel camber (rad)

### CSV Log

All engine and wheels logs are stored in the folder `Documents/Assetto Corsa/logs` within CSV files. It can be toggled in the `Logging` button on options window (default is off).

   - LiveTelemetry_EN.csv - session engine data.
   - LiveTelemetry_[FL|FR|RL|RR].csv - session wheels data.

### Resolutions

Each component have a button designed to scale all the components to best fit each default resolution. Choose be free to choose the best scale for your taste. ;)
   - 480p:  854x480
   - HD:  1280x720
   - FH:  1920x1080
   - 1440p:  2560x1440
   - UHD: 3840x2160
   - 4K:  4096x2304
   - 8K:  7680x4320

### App Install

#### New Installation

First unzip the release content direct on your Assetto Corsa main folder (C:/Program Files (x86)/steam/steamapps/common/assettocorsa) and load the game. Select the option menu and the general sub menu. In the UI Module section will be listed this app to be checked.

![Launcher Menu](https://raw.githubusercontent.com/albertowd/live-telemetry/master/resources/launcher-menu.jpg)

Last step is to enter any session (online, practice, race) and select it on the right app bar to see it on screen.

![Session Menu](https://raw.githubusercontent.com/albertowd/live-telemetry/master/resources/session-menu.jpg)

Each windows will apear separately on screen.

![Options Window](https://raw.githubusercontent.com/albertowd/live-telemetry/master/resources/app-options.jpg) ![Engine Menu](https://raw.githubusercontent.com/albertowd/live-telemetry/master/resources/app-engine.jpg) ![Wheel Window](https://raw.githubusercontent.com/albertowd/live-telemetry/master/resources/app-wheel.jpg)

#### Update Insatllation

For 1.4.1+ versions, just extract the .zip file on the AC folder.

For olders versions, its recommended to delete the plugins files from the foder `apps/python/LiveTelemetry` before extracting the new content.

## Changelog

1.5.0
   - All infos are now toggleble
   - Fix ghosts labels when window is inactive but the plugin thinks it's active

1.4.1
   - Changed suspension colors to 95% and 98%
   - Fixed: _ctypes.pyd loading errors
   - Fixed: data not being saved on session end
   - Fixed: suspension travel above maximum draw
   - Config error handling
   - Auto delete old version config files

1.4.0
   - Fixed: not showing 480p scale
   - Log can be enabled (it will not save data while disabled) in run time
   - Log is deleted if not enabled at the end of a session
   - New options window to change scale and toggle log
   - New scales dimensions
   - Tire load back available

1.3.1
   - Changed sim_info.py path to work on all installations
   - Save engine data in a csv file after the session

1.3
   - Unpacked car support (for debugging unfinished mods)
   - Save each wheel data in a csv file after the session
   - Suspension height is now being interpolated with half of suspension difference of oposite wheel

1.2
   - Engine telemetry
   - RPM x HP curve user through the engine.ini configuration
   - Brake Temp does not work, so it's not visible anymore
   - No tire temp text anymore due label transparency issue
   - Load not visible either cause it doest not have the ideal value yet (to be developed)
   - Fix importing sim_info after other imports
   - Added 480p resolution

1.1
   - Pressure and tires now uses colors based on the tires.ini configuration.
   - Tire core, inner. middle and outer temperature with colors
   
1.0.1
   - Resolution adaptive HUD up to 8k
   - New 8k textures
   - Brake temperatures (not working in AC yet)
   - Tire inner, middle, outer temperatures
   - Fix camber asphalt angle

## Noted Bugs

All the issues can be found on the issues page of the github repository: [Live Telemetry Issues](https://github.com/albertowd/live-telemetry/issues).

## Big Thanks

My newest best friend [aluigi@zenhax.com](http://zenhax.com/viewtopic.php?f=9&t=90) who helped me to understand how to open .acd files!
