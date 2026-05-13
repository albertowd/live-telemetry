[SIZE=6][B]App[/B][/SIZE]

The app show on screen real time telemetry of engine, each tire and suspension individually. The goal with this app is not to replace the Assetto Corsa built-in apps with these information, but to help developing better setups more efficiently.

[B]Important note![/B]

Now there is a standalone executable version of this plugin that can read AC1, ACC, AC Rally and AC EVO data and display it on screen, don't know for how many time I'll keep updating this AC1 only plugin.

[URL='https://www.overtake.gg/downloads/live-telemetry-evo.84121']Live Telemetry Evo Link[/URL]

[B]Important note end![/B]

The app uses the mod file directly or the encrypted Kunos files to calculate it's limits, does not need configuration.

[MEDIA=youtube]_nfAqOOu0QI[/MEDIA]

[SIZE=5][B]Telemetry Info[/B][/SIZE]

[LIST]
[*]Engine Boost Pressure (bar).
[*]Engine RPM/HP.
[*]Suspension height (mm).
[*]Suspension travel (%).
[*]Tire pressure (psi).
[*]Tire core, inner, middle and outer temperatures (ºC).
[*]Tire load (N).
[*]Tire wear (%).
[*]Wheel camber (rad).
[*]Wheel load (N).
[*]Wheel lock / ABS.
[/LIST]

[SIZE=5][B]Options Window[/B][/SIZE]

[IMG alt="Options Window"]https://raw.githubusercontent.com/albertowd/live-telemetry/master/resources/app-options.jpg[/IMG]

The options window should give you the ability to toggle every information drew by the other windows on screen. You can switch the app scale and if the app is logging the information (it will save on files only the information that was drew on screen, not the entire session).

[SIZE=5][B]Engine Window[/B][/SIZE]

[IMG alt="Engine Menu"]https://raw.githubusercontent.com/albertowd/live-telemetry/master/resources/app-engine.jpg[/IMG]

The engine window will display the actual RPM with some color variation. The color is based on the percentage of power produced by the current RPM by the last peak RPM power.

[LIST]
[*]white: current power below 98.5% (increasing curve).
[*][COLOR=rgb(44, 130, 201)]blue[/COLOR]: current power between 98.5% and 99.5% (increasing curve).
[*][COLOR=rgb(226, 80, 65)]red[/COLOR]: below 99.5% but over the peak RPM power (decreasing curve).
[*][COLOR=rgb(97, 189, 109)]green[/COLOR]: power above 99.5% (you should shift here, but some times not...).
[/LIST]

The power curve is a complex thing to calculate because it depends the actual RPM power combined with the next gear RPM power that will be shifted. But I don't know how much RPM will decrease over the shift action so I cannot predict the next gear RPM power. So the app calculates the best gear shift over the 99.5% RPM power and bellow the max RPM power on the engine power curve (.lut file defined in the engine.ini as POWER CURVE). Also, the HP displaed together is the current power or torque from the power cure mupltiplied by the current boost pressure `hp = power * ( 1 + boost )`.

Also, it displays the current boost bar pression:

[LIST]
[*]white current power below 90%.
[*][COLOR=rgb(97, 189, 109)]green[/COLOR]: current boost pressure above 90%.
[/LIST]

[SIZE=5][B]Wheel Window[/B][/SIZE]

[IMG alt="Wheel Window"]https://raw.githubusercontent.com/albertowd/live-telemetry/master/resources/app-wheel.jpg?[/IMG]

Each wheel window will display a lot of information:

[LIST]
[*]Suspension height (mm).
Suspension height from the floor is the same on each side because the AC only tells the front and rear ride height.
[*]Suspension travel (%).
The suspension bar shows the actual travel. Now it uses the Python API to fetch correct values. But if the mod does not have max suspension travel, it will dynamically change the max value based on each data current travel value and change its normal color to blue (aka Kunos Alfa 155). Also, the drawed color is the worst of the last 60 frames to not change it so fast (the log will still logs each frame data). It changes color warn about the percentage level :
[LIST]
[*]white: between 90% and 10%.
[*][COLOR=rgb(44, 130, 201)]blue[/COLOR]: between 90% and 10% if the suspension is using dynamic values.
[*][COLOR=rgb(247, 218, 100)]yellow[/COLOR]: between 95% and 90% and between 10% and 5%.
[*][COLOR=rgb(226, 80, 65)]red[/COLOR]: above 95% and below 5%.
[/LIST]
[*]Tire dirt level (as an uprising brown bar).
[*]Tire pressure (psi).
It interpolates its colors based on the the PRESSURE_IDEAL in the tyres.ini file:
[LIST]
[*][COLOR=rgb(44, 130, 201)]blue[/COLOR]: below 95%.
[*][COLOR=rgb(44, 130, 201)]blue [/COLOR]- [COLOR=rgb(97, 189, 109)]green[/COLOR]: 95% to 100%.
[*][COLOR=rgb(97, 189, 109)]green [/COLOR]- [COLOR=rgb(226, 80, 65)]red[/COLOR]: 100% to 105%.
[*][COLOR=rgb(226, 80, 65)]red[/COLOR]: above 105%.
[/LIST]
[*]Tire temps (ºC).
Displays the core, three outer temperatures (inner, middle and outer from the suspension point of view) and the tire average (as the border color).
[LIST]
[*][COLOR=rgb(44, 130, 201)]blue[/COLOR]: below 98%.
[*][COLOR=rgb(44, 130, 201)]blue [/COLOR]- [COLOR=rgb(97, 189, 109)]green[/COLOR]: between 98% and 100%.
[*][COLOR=rgb(97, 189, 109)]green [/COLOR]- [COLOR=rgb(226, 80, 65)]red[/COLOR]: between 100% and 102%.
[*][COLOR=rgb(226, 80, 65)]red[/COLOR]: above 102%.
[/LIST]
[*]The tire border color is determined with 75% of the core and the 25% of the average of of each outer temperatures.
[*]Tire wear (%).
Represented by the vertical bar. It changes its color by wear percentage:
[LIST]
[*][COLOR=rgb(97, 189, 109)]green[/COLOR]: above 98%.
[*][COLOR=rgb(247, 218, 100)]yellow[/COLOR]: between 98% and 96%.
[*][COLOR=rgb(226, 80, 65)]red[/COLOR]: below 96%.
[/LIST]
[*]Wheel camber (Rad).
Represented by the surface inclination below the wheel.
[*]Wheel load (N).
Represented as the white circle that increases its sized based on the wheel load.
[*]Wheel lock / ABS
A new brake indicator that turns red when the wheel has locked up and blue when the ABS is working (based on the angular velocity and slip coefficient).
[LIST]
[*][COLOR=rgb(44, 130, 201)]blue[/COLOR]: ABS working.
[*][COLOR=rgb(226, 80, 65)]red[/COLOR]: wheel locked up (mostly cars with no ABS).
[*][COLOR=rgb(226, 226, 226)]white[/COLOR]: wheel being a regular wheel.
[/LIST]
[/LIST]

[SIZE=5][B]CSV Log[/B][/SIZE]

All engine and wheels logs are stored in the folder Documents/Assetto Corsa/logs within CSV files. It can be toggled in the Logging button on options window (default is off).

[LIST]
[*]LiveTelemetry_EN.csv - session engine data.
[*]LiveTelemetry_[FL|FR|RL|RR].csv - session wheels data.
[/LIST]

[SIZE=5][B]Resolutions[/B][/SIZE]

Each component have a button designed to scale all the components to best fit each default resolution. Choose be free to choose the best scale for your taste. ;)

[LIST]
[*]240p: 352x240
[*]360p: 480x360
[*]480p: 640x480
[*]576p: 768x576
[*]HD: 1280x720
[*]FH: 1920x1080
[*]1440p: 2560x1440
[*]UHD: 3840x2160
[*]4K: 4096x2304
[*]8K: 7680x4320
[/LIST]

[B]App Install

Content Manager Installation and Update[/B]

Just drag the compressed folder to the Content Manager windows and accept the installation/update prompt.

After the first initialization, it detects the default configurations of the app and it can be modified via Content Manager Settings page, as bellow:

[IMG alt="Live Telemetry Settings on Content Manager"]https://raw.githubusercontent.com/albertowd/live-telemetry/master/resources/content-manager-app-settings.jpg[/IMG]

[B]New Manual Installation[/B]
First unzip the release content direct on your Assetto Corsa main folder (C:/Program Files (x86)/steam/steamapps/common/assettocorsa) and load the game. Select the option menu and the general sub menu. In the UI Module section will be listed this app to be checked.

[IMG alt="Launcher Menu"]https://raw.githubusercontent.com/albertowd/live-telemetry/master/resources/launcher-menu.jpg[/IMG]

Last step is to enter any session (online, practice, race) and select the desired app window on the right app bar to see it on screen.

[IMG alt="Session Menu"]https://raw.githubusercontent.com/albertowd/live-telemetry/master/resources/session-menu.jpg[/IMG]

[B]Update Insatllation[/B]

For 1.4.1+ versions, just extract the .zip file on the AC folder.For olders versions, its recommended to delete the plugins files from the foder apps/python/LiveTelemetry before extracting the new content.

[SIZE=6][B]Noted Bugs[/B][/SIZE]

All the issues can be found on the issues page of the github repository: [URL='https://github.com/albertowd/live-telemetry/issues']Live Telemetry Issues[/URL].

[SIZE=6][B]Big Thanks[/B][/SIZE]

My newest best friend [URL='http://zenhax.com/viewtopic.php?f=9&t=90']aluigi@zenhax.com[/URL] who helped me to understand how to open .acd files!

[B]Please Stop This[/B] from RaceDepartment who helped me with some code and others to work this app out.

[B]Jens Roos[/B] from proTyres to fix some issues.

[B]giodelmare[/B] for helping me test the suspension issues while my PC was dead.
