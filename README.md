# Live Telemetry 1.7.0

An Assetto Corsa app to view real time telemetry.

## App

The app show on screen real time telemetry of engine, each tire and suspension individually. The goal with this app is not to replace the Assetto Corsa built-in apps with these information, but to help developing better setups more efficiently.

The app uses the mod file directly or the encrypted Kunos files to calculate it's limits, does not need configuration.

[![Screen-shot](https://raw.githubusercontent.com/albertowd/live-telemetry/master/resources/screenshot.jpg)](https://www.youtube.com/watch?v=TQ6D9RuJS1g)

### Telemetry Info

* Engine boost pressure (bar).
* Engine RPM/HP.
* Suspension height (mm).
* Suspension travel (%).
* Tire pressure (psi).
* Tire core, inner, middle and outer temperatures (ºC).
* Tire load (N).
* Tire wear (%).
* Wheel camber (rad).
* Wheel load (N).
* Wheel lock / ABS.

### Options Window

![Options Window](https://raw.githubusercontent.com/albertowd/live-telemetry/master/resources/app-options.jpg)

The options window should give you the ability to toggle every information drew by the other windows on screen. You can switch the app scale and if the app is logging the information (it will save on files only the information that was drew on screen, not the entire session).

### Engine Window

![Engine Menu](https://raw.githubusercontent.com/albertowd/live-telemetry/master/resources/app-engine.jpg)

The engine window will display the actual RPM with some color variation. The color is based on the percentage of power produced by the current RPM by the last peak RPM power.

* <span style="color:white">white</span>: current power below 98.5% (increasing curve).
* <span style="color:blue">blue</span>: current power between 98.5% and 99.5% (increasing curve).
* <span style="color:red">red</span>: below 99.5% but over the peak RPM power (decreasing curve).
* <span style="color:green">green</span>: power above 99.5% (you should shift here, but some times not...).

The power curve is a complex thing to calculate because it depends the actual RPM power combined with the next gear RPM power that will be shifted. But I don't know how much RPM will decrease over the shift action so I cannot predict the next gear RPM power. So the app calculates the best gear shift over the 99.5% RPM power and bellow the max RPM power on the engine power curve (`.lut` file defined in the `engine.ini` as `POWER CURVE`). Also, the HP displaed together is the current power or torque from the power cure mupltiplied by the current boost pressure `hp = power * ( 1 + boost )`.

Also, it displays the current boost bar pression:
* <span style="color:white">white</span>: current power below 90%.
* <span style="color:green">green</span>: current boost pressure above 90%.

### Wheel Window

![Wheel Window](https://raw.githubusercontent.com/albertowd/live-telemetry/master/resources/app-wheel.jpg)

Each wheel window will display a lot of information:

* Suspension height (mm).
  
  Suspension height from the floor is the same on each side because the AC only tells the front and rear ride height.

* Suspension travel (%).
  
  The suspension bar shows the actual travel. Now it uses the Python API to fetch correct values. But if the mod does not have max suspension travel, it will dynamically change the max value based on each data current travel value and change its normal color to blue (aka Kunos Alfa 155). Also, the drawed color is the worst of the last 60 frames to not change it so fast (the log will still logs each frame data). It changes color warn about the percentage level:

  * <span style="color:white">white</span>: between 90% and 10%.
  * <span style="color:blue">blue</span>: between 90% and 10% if the suspension is using dynamic values.
  * <span style="color:yellow">yellow</span>: between 95% and 90% and between 10% and 5%.
  * <span style="color:red">red</span>: above 95% and below 5%.
  
* Tire dirt level (as an uprising brown bar).
* Tire pressure (psi).
  
  It interpolates its colors based on the the `PRESSURE_IDEAL` in the `tyres.ini` file:

  * <span style="color:blue">blue</span>: below 95%.
  * <span style="color:blue">blue</span> - <span style="color:green">green</span>: 95% to 100%.
  * <span style="color:green">green</span> - <span style="color:red">red</span>: 100% to 105%.
  * <span style="color:red">red</span>: above 105%.
  
* Tire temps (ºC).
  
  Displays the core, three outer temperatures (inner, middle and outer from the suspension point of view) and the tire average (as the border color).

  * <span style="color:blue">blue</span>: below 98%.
  * <span style="color:blue">blue</span> - <span style="color:green">green</span>: between 98% and 100%.
  * <span style="color:green">green</span> - <span style="color:red">red</span>: between 100% and 102%.
  * <span style="color:red">red</span>: above 102%.
  
  The tire border color is determined with 75% of the core and the 25% of the average of of each outer temperatures.

* Tire wear (%).
  
  Represented by the vertical bar. It changes its color by wear percentage:

  * <span style="color:green">green</span>: above 98%.
  * <span style="color:yellow">yellow</span>: between 98% and 96%.
  * <span style="color:red">red</span>: below 96%.

* Wheel camber (Rad).
  
  Represented by the surface inclination below the wheel.

* Wheel load (N).
  
  Represented as the white circle that increases its sized based on the wheel load.

* Wheel lock / ABS.
  
  A new brake indicator that turns red when the wheel has locked up and blue when the ABS is working (based on the angular velocity and slip coefficient).

  * <span style="color:blue">blue</span>: ABS working.
  * <span style="color:white">red</span>: wheel locked up (mostly cars with no ABS).
  * <span style="color:white">white</span>: wheel being a regular wheel.

### CSV Log

All engine and wheels logs are stored in the folder `Documents/Assetto Corsa/logs` within CSV files. It can be toggled in the `Logging` button on options window (default is off).

* LiveTelemetry_EN.csv - session engine data.
* LiveTelemetry_[FL|FR|RL|RR].csv - session wheels data.

### Resolutions

Each component have a button designed to scale all the components to best fit each default resolution. Choose be free to choose the best scale for your taste. ;)

* 240p: 352x240
* 360p: 480x360
* 480p:  640x480
* 576p: 768x576
* HD:  1280x720
* FH:  1920x1080
* 1440p:  2560x1440
* UHD: 3840x2160
* 4K:  4096x2304
* 8K:  7680x4320

### App Install

#### Content Manager Installation and Update

Just drag the compressed folder to the Content Manager windows and accept the installation/update prompt.

After the first initialization, it detects the default configurations of the app and it can be modified via Content Manager Settings page, as bellow:

![Live Telemetry Settings on Content Manager](https://raw.githubusercontent.com/albertowd/live-telemetry/master/resources/content-manager-app-settings.jpg)

#### New Manual Installation

First unzip the release content direct on your Assetto Corsa main folder (C:/Program Files (x86)/steam/steamapps/common/assettocorsa) and load the game. Select the option menu and the general sub menu. In the UI Module section will be listed this app to be checked.

![Launcher Menu](https://raw.githubusercontent.com/albertowd/live-telemetry/master/resources/launcher-menu.jpg)

Last step is to enter any session (online, practice, race) and select the desired app window on the right app bar to see it on screen.

![Session Menu](https://raw.githubusercontent.com/albertowd/live-telemetry/master/resources/session-menu.jpg)

#### Update Manual Insatllation

For 1.4.1+ versions, just extract the .zip file on the AC folder.

For olders versions, its recommended to delete the plugins files from the foder `apps/python/LiveTelemetry` before extracting the new content.

## Changelog

1.7.0
   - Added Turbo boost bar.
   - Added HP value on RPM bar.
   - Config file now uses the `<install folder>/cfg` folder.
   - Fixed more compatibility issues due to missmoduling by name.
   - Fixed texts still drawing on screen on engine hide.
   - Now it supports AC Manager configuration.

1.6.1
   - Config file now uses the `Document/Assetto Corsa/cfg` folder.
   - Fixed 100% static revbar (Mazda Rx7, ...).
   - Fixed crashes on RSS other mods with Copyright comments within `.lut` files.
   - New ABS indicator (still in beta) can be enabled through the config LT window.

1.6.0
   - Cars with no max suspension travel now use dynamic value based on travel itself.
   - Fixed wrong suspension travel data from Shared Memory to the Python API call.
   - Fixed some mods using invalid unicodes characters (ex. @) on internal files now being replaced with !.
   - New suspension color for dynamic max travel.
   - New wheel lock white indicator.
   - Suspension now uses the worst of the last 60 values to change color.

1.5.2
   - Limit the revbar to 100%.
   - New documentation.
   - Newer and smaller resolutions.

1.5.1
   - Better ACD file load handling.
   - Sim_info.py syntax fix.
   - Works with proTyres as well.

1.5.0
   - All infos are now toggleble
   - Changed back suspension colors to 95% and 90%
   - Fix ghosts labels when window is inactive but the plugin thinks it's active
   - New info available by `Please Stop This`
   - Suspension now works properly with the rigth data
   - Trying to work with the suspension, AC gives me negative and above maximum travel as well...

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

`Please Stop This` from RaceDepartment who helped me with some code and others to work this app out.

`Jens Roos` from proTyres to fix some issues.

`giodelmare` for helping me test the suspension issues while my PC was dead.
