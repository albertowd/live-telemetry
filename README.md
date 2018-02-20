# WheelTelemetry 1.1
An Assetto Corsa app to view real time tyre and suspension telemetry

## App

The app show on screen real time telemetry of each tyre and suspension individualy. The goal with this app is not to replace the Assetto Corsa built-in apps with theese informations, but to help developing better setups more efficiently.

![Screenshot](https://raw.githubusercontent.com/albertowd/WheelTelemetry/master/img/screenshot.png)

### Telemetry Info

   - Brake temperature (ºC): some cars doesn't have this info yet.
   - Suspension height (mm)
   - Suspension travel (%): gets warning yellow above 80% and danger red above 90% of the maximum and minimum values
   - Tyre pressure (psi)
   - Tyre core, inner, middle and outter temperatures (ºC)
   - Tyre load (N)
   - Tyre wear: bar gets warning yellow below 98% and danger red belo 96%
   - Wheel camber (rad)

### Resolutions

Each component have a button designed to scale all the components to best fit each default resolution. Choose be free to choose the best scale for your taste. ;)
   - HD:  1280x720
   - FH:  1920x1080
   - 2K:  2048x1152
   - UHD: 3840x2160
   - 4K:  4096x2304
   - 8K:  7680x4320

### App Install

First unzip the release content direct on your assetto corsa main folder (C:/Program Files (x86)/steam/steamapps/common/assettocorsa) and load the game.

![Game Menu](https://raw.githubusercontent.com/albertowd/WheelTelemetry/master/img/game-menu.png)

Select the option menu and the general sub menu. In the UI Module section will be listed this app to be checked.

![Session Menu](https://raw.githubusercontent.com/albertowd/WheelTelemetry/master/img/session-menu.png)

Last step is to enter a session and select it on the right app bar to see it on screen.

![App Window](https://raw.githubusercontent.com/albertowd/WheelTelemetry/master/img/app.png)

## Changelog
1.1
   - Pressure and tyres now uses colors based on the tyres.ini configuration.
   - Tyre core, inner. middle and outer temperature with colors
   
1.0.1
   - Resolution adaptive HUD up to 8k
   - New 8k textures
   - Brake temperatures (not working in AC yet)
   - Tyre inner, middle, outer temperatures
   - Fix camber asfalt angle

## Noted Bugs

   - Brake temperatures are not updated
   - Tyre temperatures are with transparent background (WHY ASSETTO, WHY???)

## Big Thanks

My newest best friend [aluigi@zenhax.com](http://zenhax.com/viewtopic.php?f=9&t=90) who helped me to understand how to open .acd files!