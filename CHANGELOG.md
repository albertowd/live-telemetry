# Changelog

**1.8.5**
- KERS-aware HP on the RPM bar: combustion HP plus electric deploy kW while the battery is draining.
- EMA smoothing on `kers_deploy_kw` so AC's quantised SoC doesn't flicker the HP readout.
- New `BatteryBar` widget — fill = SoC; shows kJ when AC exposes battery capacity, else percentage.
- BatteryBar auto-hides on pure-ICE cars; reveals on the first frame of detected battery activity.
- Tri-state `Battery` toggle in Options (yellow AUTO / red ON / white OFF), static label.
- Deploy detection gates on SoC falling, not the KERS button — fixes false-positive HP during regen.

**1.8.1**
- IMO temperature readouts (inner / middle / outer) larger and bold for clearer reading.
- Tire-wear label larger and bold; row + bar layout retuned to fit the existing box.
- All remaining telemetry labels switched to Arial Bold for consistency.
- Dropped sub-720p Size presets; stale `Size` in `conf.ini` is coerced to `FHD` on load.
- Window positions stored in anchor-space — each widget pins to its screen corner.
- New `Reset` button — snaps every widget back to its default screen-edge anchor.
- Tire-wear bar self-calibrates against per-wheel peak `tyreWear`; fresh tyres read 100%.

**1.8.0**
- New GitHub actions to make automatic release assets

Wheel widgets
- Tire / suspension / height widgets rebuilt as GL primitives; tire group rotates under camber.
- Per-zone IMO readouts (I / M / O / C); inner faces screen-centre and follows the rotation.
- Tire-load circle scales with wheel load; contact-patch bars replace the camber strip.
- Wheel ID + compound stacked above height; tire-wear moved into the brake column as a fill bar.
- Layout retuned for camber clearance; lock indicator on by default.

Engine widget
- Driver-aid chip strip (PIT, TC, ABS, DRS, ERS).
- Fuel and brake-bias readouts row.
- Widget height bumped 85 → 120 to fit the new rows.

Internal
- `BoxComponent` exposes camber-rotation helpers shared by all rotated widgets.
- `InfoWindow.draw` defaults to enabled for components without a config toggle.
- Config: version bump resets `cfg/conf.ini` on first run.


**1.7.1**
- BoostBar widget + toggle now hidden on naturally aspirated cars.
- BoostBar option now persists across sessions (was dropped on `acShutdown`).
- ABS / lock detection rewritten — uses per-car slip limits, fixes false positives on cars w/o ABS.
- Lock indicator blinks yellow at 5 Hz instead of solid red — brief lock-ups are easier to spot.
- Default window-active is now `True` for all widgets — fixes "checked-but-empty" after upgrades.
- `cfg/settings_defaults.ini` now matches the runtime defaults in `Config.__init__`.
- `7z-maker.bat` accepts an optional version argument and defaults to the current release.
- Internal: removed dead ABS slip-list code; tightened `acShutdown` data-flush guard; lint cleanup.

**1.7.0**
- Added Turbo boost bar.
- Added HP value on RPM bar.
- Config file now lives under `<install folder>/cfg/`.
- Fixed compatibility issues caused by module-name collisions (re-namespacing under `lib/`).
- Fixed text still being drawn on screen after the engine widget was hidden.
- Now supports Content Manager configuration.

**1.6.1**
- Config file moved to `Documents/Assetto Corsa/cfg/`.
- Fixed 100% static revbar (Mazda RX-7, …).
- Fixed crashes on RSS and other mods with copyright comments inside `.lut` files.
- New ABS indicator (beta) — toggleable from the LT options window.

**1.6.0**
- Cars without `suspensionMaxTravel` now use a dynamic max derived from observed travel.
- Fixed wrong suspension travel data from shared memory by switching to the Python API.
- Fixed mods using invalid Unicode characters (e.g. `@`) in internal files — replaced with `!`.
- New suspension colour for dynamic max travel.
- New wheel-lock white indicator.
- Suspension now uses the worst of the last 60 values when colouring.

**1.5.2**
- Limit the revbar to 100%.
- New documentation.
- Newer and smaller resolutions.

**1.5.1**
- Better ACD file load handling.
- `sim_info.py` syntax fix.
- Works with proTyres as well.

**1.5.0**
- All info elements are now toggleable.
- Reverted suspension colours to 95%/90% thresholds.
- Fixed ghost labels when the window was inactive but the plugin still considered it active.
- New info contributed by `Please Stop This`.
- Suspension now works correctly with the right data source.
- Working around AC reporting negative and above-maximum suspension travel for some cars.

**1.4.1**
- Suspension colour thresholds at 95%/98%.
- Fixed `_ctypes.pyd` loading errors.
- Fixed data not being saved on session end.
- Fixed suspension travel being drawn above maximum.
- Config error handling.
- Auto-delete old version config files.

**1.4.0**
- Fixed: 480p scale not showing.
- Logging can now be enabled at runtime (no data is saved while disabled).
- Logs are deleted at session end if logging was never enabled.
- New options window (scale + log toggle).
- New scale dimensions.
- Tire load back available.

**1.3.1**
- Changed `sim_info.py` path to work on all installations.
- Save engine data to a CSV file at session end.

**1.3**
- Unpacked car support (for debugging unfinished mods).
- Save each wheel's data to a CSV file at session end.
- Suspension height interpolated using half of the opposite wheel's suspension delta.

**1.2**
- Engine telemetry.
- RPM × HP curve via `engine.ini`.
- Brake temp removed (AC doesn't expose it correctly).
- Tire temp text removed (label transparency issue).
- Load hidden until an ideal value is defined.
- Fixed `sim_info` import order.
- Added 480p resolution.

**1.1**
- Pressure and tires now use colours derived from `tyres.ini`.
- Tire core, inner, middle, outer temperatures with colour coding.

**1.0.1**
- Resolution-adaptive HUD up to 8K.
- New 8K textures.
- Brake temperatures (not yet exposed by AC).
- Tire inner / middle / outer temperatures.
- Fixed camber asphalt angle.
