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
[*]Driver-aid chips: PIT, TC, ABS, DRS, ERS.
[*]Fuel and brake-bias readouts.
[*]Suspension height (mm).
[*]Suspension travel (%).
[*]Tire pressure (psi).
[*]Tire core, inner, middle and outer temperatures (ºC), with per-zone numeric readouts on the IMO grid.
[*]Tire load (N).
[*]Tire wear (%).
[*]Tyre compound abbreviation and wheel ID label.
[*]Contact-patch bars (camber × pressure × load heuristic).
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

Below the RPM bar, a strip of driver-aid chips lights up only while each condition is true (so the bar stays compact): [B]PIT[/B] limiter, [B]TC[/B] (bright when cutting, dim when armed), [B]ABS[/B] (same scheme), [B]DRS[/B] (bright when deployed), [B]ERS[/B] charging. The bottom row shows fuel litres and brake-bias percentage.

[SIZE=5][B]Wheel Window[/B][/SIZE]

[IMG alt="Wheel Window"]https://raw.githubusercontent.com/albertowd/live-telemetry/master/resources/app-wheel.jpg?[/IMG]

Each wheel window will display a lot of information. The tire silhouette, IMO temperature grid, dirt overlay, contact-patch bars and per-zone temperature readouts share a single pivot and rotate together with the wheel under camber (the tilt is amplified ×2 so a typical setup camber reads clearly at a glance).

[LIST]
[*][B]Tire silhouette[/B].
Drawn as pure GL primitives (no PNG textures); tinted by composite tire temperature (75 % core + 25 % average of inner / middle / outer) on the same compound-normalised scale as the IMO grid.
[*][B]Inner / middle / outer / core temp grid[/B] (ºC).
Per-face temperature blocks colour-coded by the compound's thermal curve, with numeric readouts that follow the camber rotation each frame. The inner zone always faces screen-centre so reading temperature bias is consistent across the four wheels.
[LIST]
[*][COLOR=rgb(44, 130, 201)]blue[/COLOR]: below 98%.
[*][COLOR=rgb(44, 130, 201)]blue [/COLOR]- [COLOR=rgb(97, 189, 109)]green[/COLOR]: between 98% and 100%.
[*][COLOR=rgb(97, 189, 109)]green [/COLOR]- [COLOR=rgb(226, 80, 65)]red[/COLOR]: between 100% and 102%.
[*][COLOR=rgb(226, 80, 65)]red[/COLOR]: above 102%.
[/LIST]
[*][B]Suspension height[/B] (mm).
Per-axle ride height with a small up/down arrow icon (also rebuilt as GL primitives). Bars + arrows + readout flash [COLOR=rgb(226, 80, 65)]red[/COLOR] for 0.5 s when the chassis bottoms out (below 0.02 mm).
[*][B]Suspension travel[/B] (%).
Strut graphic with a fill that shrinks as the suspension compresses. Uses the Python API to fetch correct values; if the mod does not publish a max travel, it self-calibrates against the running maximum (aka Kunos Alfa 155) and turns blue. The drawn colour is the worst of the last 60 frames so the indicator doesn't flicker (the CSV log still records every frame).
[LIST]
[*]white: between 90% and 10%.
[*][COLOR=rgb(44, 130, 201)]blue[/COLOR]: between 90% and 10% with a self-calibrated max.
[*][COLOR=rgb(247, 218, 100)]yellow[/COLOR]: between 95% and 90%, and between 10% and 5%.
[*][COLOR=rgb(226, 80, 65)]red[/COLOR]: above 95% or below 5%.
[/LIST]
[*][B]Tire dirt[/B].
Brown bar that rises from the bottom of the tire as it picks up off-track grass and gravel.
[*][B]Tire pressure[/B] (psi).
Pressure icon tinted by per-compound normalised pressure (`PRESSURE_IDEAL` in `tyres.ini`); the label shows the raw psi value.
[LIST]
[*][COLOR=rgb(44, 130, 201)]blue[/COLOR]: below 95%.
[*][COLOR=rgb(44, 130, 201)]blue [/COLOR]- [COLOR=rgb(97, 189, 109)]green[/COLOR]: 95% to 100%.
[*][COLOR=rgb(97, 189, 109)]green [/COLOR]- [COLOR=rgb(226, 80, 65)]red[/COLOR]: 100% to 105%.
[*][COLOR=rgb(226, 80, 65)]red[/COLOR]: above 105%.
[/LIST]
[*][B]Tire wear[/B] (%).
Horizontal "Tire Wear" bar in the brake column (between the lock and pressure icons), left → right fill (full = fresh).
[LIST]
[*][COLOR=rgb(97, 189, 109)]green[/COLOR]: above 98%.
[*][COLOR=rgb(247, 218, 100)]yellow[/COLOR]: between 98% and 96%.
[*][COLOR=rgb(226, 80, 65)]red[/COLOR]: below 96%.
[/LIST]
[*][B]Contact-patch bars[/B] (camber × pressure × load).
Three white bars at the tire-ground line — inner / middle / outer — whose heights are a qualitative load-distribution heuristic. Replaces the older tilted "asphalt quad" camber strip and is still toggled by the [B]Camber[/B] option for backward compatibility.
[*][B]Wheel load[/B] (N).
White circle behind the tire whose diameter scales linearly with vertical wheel load; useful for spotting weight transfer at a glance.
[*][B]Wheel lock / ABS[/B].
Brake icon that blinks to flag pedal events on this corner. Enabled by default in 1.8.0.
[LIST]
[*][COLOR=rgb(44, 130, 201)]blue[/COLOR]: ABS modulating on this wheel (pulses at the car's `RATE_HZ`).
[*][COLOR=rgb(247, 218, 100)]yellow[/COLOR]: wheel locked up, blinking at 5 Hz (mostly cars without ABS).
[*][COLOR=rgb(226, 226, 226)]white[/COLOR]: neutral.
[/LIST]
[*][B]Wheel ID + tyre compound[/B].
Two-line caption ([B]FL[/B] / [B]FR[/B] / [B]RL[/B] / [B]RR[/B] over a 3-character compound abbreviation — [B]SOF[/B] / [B]MED[/B] / [B]HAR[/B] / [B]INT[/B] / [B]WET[/B]) stacked at the top of the inboard column, lined up with the ride-height readout below.
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
[*]FHD: 1920x1080
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

For 1.4.1+ versions, just extract the .7z archive on the AC folder. For older versions, it's recommended to delete the plugin files from the folder apps/python/LiveTelemetry before extracting the new content.

[SIZE=6][B]Noted Bugs[/B][/SIZE]

All the issues can be found on the issues page of the github repository: [URL='https://github.com/albertowd/live-telemetry/issues']Live Telemetry Issues[/URL].

[SIZE=6][B]Big Thanks[/B][/SIZE]

My newest best friend [URL='http://zenhax.com/viewtopic.php?f=9&t=90']aluigi@zenhax.com[/URL] who helped me to understand how to open .acd files!

[B]Please Stop This[/B] from RaceDepartment who helped me with some code and others to work this app out.

[B]Jens Roos[/B] from proTyres to fix some issues.

[B]giodelmare[/B] for helping me test the suspension issues while my PC was dead.
