# Live Telemetry 1.3.1
An Assetto Corsa app to view real time telemetry

## App

The app show on screen real time telemetry of engine, each tire and suspension individually. The goal with this app is not to replace the Assetto Corsa built-in apps with these information, but to help developing better setups more efficiently.

The app uses the mod file directly or the encrypted Kunos files to calculate it's limits, does not need configuration.

[![Screen-shot](https://raw.githubusercontent.com/albertowd/live-telemetry/master/img/screenshot.png)](https://www.youtube.com/watch?v=i7jyqPhZp4Y)

### Telemetry Info

   - Engine Ideal RPM/Power
   - Suspension height (mm)
   - Suspension travel (%): gets warning yellow above 80% and danger red above 90% of the maximum and minimum values
   - Tyre pressure (psi)
   - Tyre core, inner, middle and outer temperatures (ºC)
   - Tyre load (N)
   - Tyre wear: bar gets warning yellow below 98% and danger red below 96%
   - Wheel camber (rad)

### Telemetry Log

All engine and wheels logs are stored in the folder `Documents/Assetto Corsa/logs`.

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

First unzip the release content direct on your Assetto Corsa main folder (C:/Program Files (x86)/steam/steamapps/common/assettocorsa) and load the game. Select the option menu and the general sub menu. In the UI Module section will be listed this app to be checked.

![Session Menu](https://raw.githubusercontent.com/albertowd/live-telemetry/master/img/session-menu.png)

Last step is to enter any session (online, practice, race) and select it on the right app bar to see it on screen.

![App Window](https://raw.githubusercontent.com/albertowd/live-telemetry/master/img/app.png)

## Change-log

1.3
   - Unpacked car support (for debugging unfinished mods)
   - Save each wheel data in a csv file after the session
   - Suspension height is now being interpolated with half of suspension difference of oposite wheel

1.2
   - Engine telemetry
   - RPM x HP curve user through the engine.ini configuration
   - Brake Temp does not work, so it's not visible anymore
   - No tyre temp text anymore due label transparency issue
   - Load not visible either cause it doest not have the ideal value yet (to be developed)
   - Fix importing sim_info after other imports
   - Added 480p resolution

1.1
   - Pressure and tyres now uses colors based on the tyres.ini configuration.
   - Tyre core, inner. middle and outer temperature with colors
   
1.0.1
   - Resolution adaptive HUD up to 8k
   - New 8k textures
   - Brake temperatures (not working in AC yet)
   - Tyre inner, middle, outer temperatures
   - Fix camber asphalt angle

## Noted Bugs

   - ???

## Big Thanks

My newest best friend [aluigi@zenhax.com](http://zenhax.com/viewtopic.php?f=9&t=90) who helped me to understand how to open .acd files!