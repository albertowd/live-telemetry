# Changelog

**1.8.1**
- Tire IMO temperature readouts (inner / middle / outer) bumped in size and switched to Arial Bold for legibility against the coloured bump quads.
- Core tire temperature readout shows the degree symbol (e.g. `85°C`).
- Tire wear label font bumped and switched to Arial Bold; layout retuned to keep the title row + bar inside the existing box.
- All other telemetry labels (BoostBar, Height, Pressure, RPM/HP, wheel ID + compound, engine chips, fuel, brake bias) switched to Arial Bold for consistency.
- Dropped sub-720p resolution presets (240p, 360p, 480p, 576p) from the Size cycle and docs; stale `Size` entries in `conf.ini` are coerced to `FHD` on load.

**1.8.0**
- New GitHub actions to make automatic release assets

Wheel widgets
- Tire, suspension and height widgets rebuilt as GL primitives; tire group (silhouette, IMO grid, dirt, contact patch, per-zone readouts) rotates together under camber.
- Per-zone IMO temperature readouts (inner / middle / outer / core); inner zone faces screen-centre; positions follow the rotation.
- Tire-load circle scales linearly with wheel load; contact-patch bars (camber × pressure × load) replace the camber strip — same `Camber` toggle.
- Wheel ID + compound abbreviation stacked above the height widget; tire-wear moved into the brake column as a horizontal left→right fill.
- Layout retuned for camber clearance; lock indicator on by default.

Engine widget
- Driver-aid chip strip (PIT, TC, ABS, DRS, ERS).
- Fuel and brake-bias readouts row.
- Widget height bumped 85 → 120 to fit the new rows.

Internal
- `BoxComponent` ships rotation helpers (`_rotate`, `_camber_rotation`, `_emit_rotated_quad`, `_emit_rotated_rect`) so any widget can share the tire-pivot rotation.
- `InfoWindow.draw` defaults to enabled for components without a config toggle.
- Config: version bump resets `cfg/conf.ini` on first run.


**1.7.1**
- BoostBar widget and its options-window toggle are now hidden on naturally aspirated cars (detected via `info.static.maxTurboBoost`).
- BoostBar option now persists across sessions (was being dropped on `acShutdown`).
- ABS / lock detection rewritten: now reads `SLIP_RATIO_LIMIT` from each car's `electronics.ini` (`ACD.get_abs_slip_limit`), gates ABS on the player's assist setting (`physics.abs > 0`), and detects lock-up via either a near-zero angular velocity *or* an extreme slip ratio. Previously compared `wheelSlip` directly against `physics.abs`, which is the assist *level* and not a threshold — the indicator misfired on cars without ABS and was unreliable on cars with ABS.
- Lock indicator now blinks yellow at 5 Hz instead of solid red, making brief lock-ups easier to spot.
- Default window-active state on a fresh config is now `True` for all five widgets, fixing the "checked-but-empty" symptom after a version bump (AC's app-bar restoration does not fire the activation listener).
- Config defaults documented in `cfg/settings_defaults.ini` now match the runtime defaults in `Config.__init__`.
- `7z-maker.bat` accepts an optional version argument and defaults to the current release.
- Internal: removed dead `ABSSlipList` class and dead `get_abs_slip_ratio_list` method, tightened the `acShutdown` data-flush guard (was checking the same wheel twice), assorted lint/dead-code cleanup.

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
