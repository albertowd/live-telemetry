# Live Telemetry 1.7.1

An Assetto Corsa in-game app (Python plugin) that renders real-time, per-frame telemetry for engine, suspension, and each tire individually. The goal is not to replace AC's built-in apps but to give a richer signal while iterating on car setups.

The app reads live data through AC's shared-memory ABI and Python API, and resolves per-car limits directly from the encrypted Kunos `data.acd` files (or the unpacked `data/` folder for mods in development), so it works with no per-car configuration.

[![Screen-shot](https://raw.githubusercontent.com/albertowd/live-telemetry/master/resources/screenshot.jpg)](https://www.youtube.com/watch?v=TQ6D9RuJS1g)

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Project Layout](#project-layout)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Telemetry Reference](#telemetry-reference)
- [Resolutions](#resolutions)
- [CSV Log](#csv-log)
- [Installation](#installation)
- [Developer Guide](#developer-guide)
- [Changelog](#changelog)
- [Known Bugs](#known-bugs)
- [Acknowledgements](#acknowledgements)

---

## Tech Stack

| Concern | Choice |
| --- | --- |
| Runtime | AC's embedded **Python 3.3** interpreter (32/64-bit dispatched at load time) |
| AC bridge | `ac` and `acsys` modules (provided by Assetto Corsa) |
| Telemetry source | AC Shared Memory via `mmap` + `ctypes` (`lib/sim_info.py`, AC SDK 1.14.3) |
| Car data | Custom decoder for Kunos `data.acd` files (`lib/lt_acd.py`) |
| UI | AC's immediate-mode app API (`ac.newApp`, `ac.glQuad`, `ac.glColor4f`, `ac.addLabel`, …) |
| Config | `configparser` against versioned `cfg/conf.ini` with defaults in `cfg/settings_defaults.ini` |
| Persistence | CSV files written to `Documents/Assetto Corsa/logs/` |
| Lint | `pylint` with project-level `.pylintrc` |
| Packaging | `7z-maker.bat` (7-Zip) producing `live-telemetry-<version>.7z` |

> **No external Python dependencies.** Everything ships inside `apps/python/LiveTelemetry/`. There is no `pip install` step — AC loads the folder directly.

---

## Project Layout

```
live-telemetry/
├── apps/python/LiveTelemetry/        # The AC plugin package
│   ├── LiveTelemetry.py              # Plugin entry point (acMain / acUpdate / acShutdown)
│   ├── a_ctypes_aux.py               # MUST load first — picks 32/64-bit _ctypes.pyd
│   ├── cfg/
│   │   └── settings_defaults.ini     # Documented defaults; conf.ini is generated next to it
│   ├── img/                          # Widget textures (PNG; PSD/SVG sources excluded from build)
│   ├── lib/
│   │   ├── sim_info.py               # AC Shared Memory reader (ctypes structs + mmap)
│   │   ├── lt_acd.py                 # data.acd decoder + data/ folder fallback
│   │   ├── lt_config.py              # ConfigParser-based settings, versioned
│   │   ├── lt_colors.py              # Palette (RGBA tuples)
│   │   ├── lt_interpolation.py       # Power / TirePsi / TireTemp curve math
│   │   ├── lt_components.py          # All renderable widgets (Box, BoostBar, RPMPower, Tire, …)
│   │   ├── lt_engine_info.py         # Engine window: data + components + lifecycle
│   │   ├── lt_wheel_info.py          # Per-wheel window: data + components + lifecycle
│   │   ├── lt_options_info.py        # Options window with toggle buttons
│   │   └── lt_util.py                # Logging, CSV export, Windows MyDocs lookup
│   ├── stdlib/   _ctypes.pyd         # 32-bit fallback runtime
│   └── stdlib64/ _ctypes.pyd         # 64-bit fallback runtime
├── content/gui/icons/                # App-bar icons (ON/OFF states for each window)
├── resources/                        # Screenshots used by this README only
├── 7z-maker.bat                      # Release packaging script
├── .pylintrc                         # Lint config (max-line-length=180, AC-friendly disables)
├── .env                              # Local PYTHONPATH for IDE auto-completion against AC's stubs
└── README.md
```

---

## Architecture

### Plugin lifecycle

Assetto Corsa drives the app through three callbacks, all wired in `LiveTelemetry.py`:

```
acMain(ac_version)   → load configs, decrypt ACD, build windows, register listeners
acUpdate(delta_t)    → physics tick: each active info object pulls from sim_info
on_render_*(delta_t) → frame tick: each active info object draws its components
acShutdown()         → persist options/positions, flush CSV (or wipe if logging was off)
```

### Module dependencies

```
                    ┌──────────────────────────┐
                    │   LiveTelemetry.py       │ (entry point, AC callbacks, click handlers)
                    └──────────────┬───────────┘
                                   │
        ┌──────────────────┬───────┴────────┬───────────────────┐
        ▼                  ▼                ▼                   ▼
┌──────────────┐  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────┐
│ EngineInfo   │  │ WheelInfo (×4)   │ │ OptionsInfo      │ │ Config       │
│  (engine     │  │  (FL/FR/RL/RR)   │ │  (toggle window) │ │  conf.ini    │
│  window)     │  │                  │ │                  │ │              │
└──────┬───────┘  └─────────┬────────┘ └────────┬─────────┘ └──────┬───────┘
       │                    │                   │                  │
       └────────────┬───────┴───────────────────┘                  │
                    ▼                                              │
            ┌───────────────┐    ┌──────────────────┐              │
            │ lt_components │◄───│ lt_interpolation │              │
            │ (renderables) │    │ (Power/Psi/Temp) │              │
            └───────┬───────┘    └─────────┬────────┘              │
                    │                      │                       │
                    ▼                      ▼                       ▼
              ┌──────────┐           ┌─────────┐           ┌──────────────┐
              │ Colors   │           │  ACD    │◄──────────│  lt_util     │
              └──────────┘           │ decoder │           │ (log, paths) │
                                     └─────────┘           └──────────────┘
                                          ▲
                                          │ reads engine.ini / tyres.ini / power.lut
                              ┌───────────┴────────────┐
                              │ content/cars/<car>/    │
                              │   data.acd  OR  data/  │
                              └────────────────────────┘
```

### Data flow per frame

1. **AC physics tick** invokes `acUpdate(delta_t)`.
2. Each active `EngineInfo` / `WheelInfo` calls its inner `Data.update(info)`, copying the values it cares about out of the shared-memory `info` proxy and (where shared memory is unreliable) the Python API — e.g. `ac.getCarState(0, acsys.CS.SuspensionTravel)` is used because some mods publish broken `suspensionTravel` in shared memory (see `lt_wheel_info.py`).
3. If `Logging` is on, a deep copy of the `Data` snapshot is appended to the per-window in-memory log.
4. **AC render tick** invokes `on_render_*(delta_t)` which delegates to `info.draw(delta_t)`, which iterates components and calls `component.draw(self.__data, delta_t)` for every option that is currently enabled. Disabled components get `clear()` instead, so labels don't ghost on screen.
5. On `acShutdown`, options + window positions are written back to `cfg/conf.ini`, and the in-memory CSV buffers are flushed via `lt_util.export_saved_log` — or deleted (`clear_logs`) when nothing was captured.

### Two interesting subsystems

**`lib/lt_acd.py` — Kunos data decryption.** Cars ship with their parameters packed into an encrypted `data.acd`. The decoder derives a per-car key from the car folder name, walks the file's `(name, size, payload)` records, and decrypts each payload in place. This is what lets the plugin compute power curves, tire pressure references, and suspension limits without per-car configuration. Unpacked `data/` folders (used by mod authors) are auto-detected as a fallback.

**`a_ctypes_aux.py` — runtime bootstrap.** AC's embedded Python ships an incomplete stdlib; `_ctypes` in particular is missing on some installs. This module **must** be the first import in `LiveTelemetry.py`. It detects the architecture (`platform.architecture()`) and prepends `stdlib64/` or `stdlib/` to `sys.path` before any `ctypes`-using module (notably `sim_info.py`) is loaded. Removing or reordering this import will break the plugin on a fresh install — see the 1.4.1 changelog entry.

---

## Configuration

### Where settings live

| File | Purpose |
| --- | --- |
| `apps/python/LiveTelemetry/cfg/settings_defaults.ini` | Read-only documented defaults shipped with the release. |
| `apps/python/LiveTelemetry/cfg/conf.ini` | User-mutated settings (toggles, window positions, scale). Created on first run, regenerated when the version field doesn't match. |
| `Documents/Assetto Corsa/cfg/video.ini` | Read once on first run to seed window positions for the current resolution. |

> **Versioning.** `Config.__init__` compares `[About] version` against `LT_VERSION`. A mismatch triggers a full reset to defaults — the trade-off for being able to add or rename options without writing a migration each time. If you bump `LT_VERSION` in `LiveTelemetry.py`, also bump it in `cfg/settings_defaults.ini`.

### Available options

All toggleable from the in-game **Options** window (or via Content Manager):

`BoostBar`, `Camber`, `Dirt`, `Height`, `Load`, `Lock`, `Logging`, `Pressure`, `RPMPower`, `Size`, `Suspension`, `Temps`, `Tire`, `Wear`.

`Tire` is a parent toggle that hides every tire-related widget at once.

---

## Telemetry Reference

### What gets shown

* Engine boost pressure (bar)
* Engine RPM and live HP
* Suspension height (mm) and travel (%)
* Tire pressure (psi)
* Tire core, inner, middle, outer temperatures (ºC)
* Tire load (N) and wear (%)
* Wheel camber (rad) and load (N)
* Wheel lock / ABS

### Options Window

![Options Window](https://raw.githubusercontent.com/albertowd/live-telemetry/master/resources/app-options.jpg)

Toggles every overlay element, switches the global scale, and turns CSV logging on or off. Logging only persists the elements that were actually drawn — disabled fields are not written.

### Engine Window

![Engine Menu](https://raw.githubusercontent.com/albertowd/live-telemetry/master/resources/app-engine.jpg)

The RPM bar uses the power curve from `engine.ini` (`POWER CURVE` → `power.lut`) to colour the current RPM by how close it is to peak power:

* <span style="color:white">white</span> — current power below 98.5% (rising side of the curve)
* <span style="color:blue">blue</span> — between 98.5% and 99.5% (rising side)
* <span style="color:red">red</span> — past peak RPM but still above 99.5%
* <span style="color:green">green</span> — at or above 99.5% (the shift hint, though sometimes you should hold)

Predicting the *true* optimal shift point would require knowing the next-gear RPM after the shift, which AC doesn't expose, so the heuristic targets the >99.5% / pre-redline window. The HP value displayed alongside is `hp = power(rpm) * (1 + boost)`.

Boost bar:

* <span style="color:white">white</span> — boost below 90% of session-max
* <span style="color:green">green</span> — boost at or above 90%

### Wheel Window

![Wheel Window](https://raw.githubusercontent.com/albertowd/live-telemetry/master/resources/app-wheel.jpg)

Every element is laid out around a central tire silhouette and mirrored on the left/right windows. Per-frame values are computed in `lib/lt_wheel_info.py:Data.update` and rendered by the matching subclass in `lib/lt_components.py`. Per-car limits (ideal pressure, thermal curves, suspension max, ABS slip target, …) come from the car's `data.acd` (or unpacked `data/` folder) at construction time — no value is "hardcoded per car".

* **Suspension height (mm).** AC's shared memory only exposes one ride-height per axle (`physics.rideHeight[0]` for front, `[1]` for rear), so per-wheel height is reconstructed by subtracting half the difference between this wheel's suspension travel and the opposite-side wheel's. The textured background flashes red for `WARNING_TIME_S = 0.5 s` whenever the value drops below 0.02 mm — i.e. the chassis is scraping the surface.

* **Suspension travel (%).** Bar uses `acsys.CS.SuspensionTravel` (the Python API value) instead of `physics.suspensionTravel`, because the shared-memory field is broken on several mods — the original 1.6.0 changelog and the comment in `Data.update` document a specific case where shared memory reported >100% travel while the API reported ~55%. When the car has no `suspensionMaxTravel` (some mods, e.g. Kunos Alfa 155), the max is computed dynamically from the running observed maximum and the bar turns blue to indicate "max is an estimate". The displayed colour is the *worst* of the last 60 frames, so a single-frame compression spike won't make the indicator flicker — but the CSV log records every frame untouched.
  * <span style="color:white">white</span> — 10%–90%
  * <span style="color:blue">blue</span> — 10%–90% with dynamic max
  * <span style="color:yellow">yellow</span> — 5%–10% or 90%–95%
  * <span style="color:red">red</span> — below 5% or above 95%

* **Tire dirt.** Vertical brown bar that rises with `physics.tyreDirtyLevel[i]`, scaled ×4 so the bar reaches full height around AC's typical dirty-level cap (~0.25). No colour states — height only — and no per-car configuration.

* **Tire pressure (psi).** `physics.wheelsPressure[i]` interpolated against the per-compound `PRESSURE_IDEAL` from `tyres.ini`. The compound section is resolved by scanning `FRONT_<n>` / `REAR_<n>` blocks for a `SHORT_NAME` matching the current `ac.getCarTyreCompound(0)`, falling back to the `[COMPOUND_DEFAULT] INDEX` value. The colour interpolation thresholds live in `lib/lt_interpolation.py:TirePsi.interpolate_color`.
  * <span style="color:blue">blue</span> — below 95%
  * <span style="color:blue">blue</span>→<span style="color:green">green</span> — 95%–100%
  * <span style="color:green">green</span>→<span style="color:red">red</span> — 100%–105%
  * <span style="color:red">red</span> — above 105%

* **Tire temps (ºC).** Inner / middle / outer probes (`physics.tyreTempI/M/O[i]`) plus the core (`physics.tyreCoreTemperature[i]`). Each segment is coloured independently against the compound's `THERMAL_<section> → PERFORMANCE_CURVE` lookup from `tyres.ini`, parsed once on plugin start and interpolated by `lib/lt_interpolation.py:TireTemp`. The "I/M/O" labelling is *suspension-relative* — the inner edge of the tire as the suspension geometry sees it, not the steering rack — so on a left-side wheel the rendered "Inner" probe is the chassis-side temperature.

  Separately, the **`Tire` widget** (the whole-tire silhouette) is tinted using a weighted average — `0.75 × core + 0.25 × mean(I, M, O)` — so the overall colour reflects bulk working temperature instead of just surface contact. `Tire` and `Temps` are independently toggleable from the Options window.
  * <span style="color:blue">blue</span> — below 98%
  * <span style="color:blue">blue</span>→<span style="color:green">green</span> — 98%–100%
  * <span style="color:green">green</span>→<span style="color:red">red</span> — 100%–102%
  * <span style="color:red">red</span> — above 102%

* **Tire wear (%).** `physics.tyreWear[i] / 100`. The bar maps the last **6 %** of tread (94 %–100 %) to its full vertical range — most of a tire's life is "green" and the bar only starts visibly retreating once wear becomes meaningful. Below 94 % wear the bar is fully drained but still present (red).
  * <span style="color:green">green</span> — above 98%
  * <span style="color:yellow">yellow</span> — 96%–98%
  * <span style="color:red">red</span> — below 96%

* **Wheel camber (rad).** `physics.camberRAD[i]`. Drawn as a tilted asphalt quad beneath the tire — the inboard/outboard vertex is offset by `tan(camber) × bar_width` so the road plane visibly tips towards positive or negative camber. Always white; no colour coding (read the angle, not the colour).

* **Wheel load (N).** `physics.wheelLoad[i]`, divided by `5 × g` (49.03) before being used as the diameter of the white circle drawn behind the tire. The conversion is purely visual scaling — there's no numeric readout. The widget is most useful as a *relative* indicator: comparing circle sizes across the four wheels makes weight transfer (braking, cornering, kerb hits) immediately obvious.

* **Wheel lock / ABS.** Multi-signal detector that combines `physics.brake`, `physics.wheelSlip[i]`, `physics.wheelAngularSpeed[i]`, the player's ABS assist setting (`physics.abs`), and the car's `SLIP_RATIO_LIMIT` from `electronics.ini`.
  * <span style="color:blue">blue</span> — ABS active (pulses at the car's `RATE_HZ`)
  * <span style="color:yellow">yellow</span>, blinking at 5 Hz — wheel locked (typically cars without ABS, or ABS overwhelmed)
  * <span style="color:white">white</span> — neutral

  **How it is detected (and what it deliberately *isn't*).** A common pitfall is to treat `info.physics.abs` as if it were a slip-ratio threshold — it isn't. `physics.abs` is the player's ABS-assist *level*, normalised 0…1 (0 = off, 1 = max). The actual slip threshold lives per-car in `electronics.ini → [ABS] → SLIP_RATIO_LIMIT`; the plugin reads it once at construction time (`ACD.get_abs_slip_limit()`), defaulting to `0.2` for cars that don't expose one or where parsing fails.

  Per frame, the detector evaluates two independent flags in `lib/lt_wheel_info.py:Data.update`:

  | Flag | Condition |
  | --- | --- |
  | `lock` | `brake > 0` AND `slip > 0` AND (`abs(wheelAngularSpeed) < 1.0` rad/s **OR** `slip > 0.5`) |
  | `abs_active` | `physics.abs > 0` AND `brake > 0` AND `slip > SLIP_RATIO_LIMIT` AND **not** `lock` |

  The `OR` branch in the lock condition is what catches AC physics cases where a locked wheel keeps a small residual angular velocity (~0.05–0.5 rad/s) instead of going to exact zero — the previous strict `== 0.0` check missed those. The `slip > 0` gate prevents false positives on stationary cars at idle. Lock takes precedence over ABS, so a fully locked wheel always reports as a lock, never as ABS pulsing.

  The blue ABS pulse rate is the car's actual `[ABS] → RATE_HZ` (read by `ACD.get_abs_hz()` and consumed in `Lock.draw`). The yellow lock blink rate is fixed at 5 Hz via `LOCK_BLINK_PERIOD_S = 0.1` in `lib/lt_components.py`. After the wheel re-grips, the lock indicator keeps blinking for `WARNING_TIME_S = 0.5` seconds so a brief lock is still visible at typical render rates.

---

## Resolutions

Each window has a button that scales every component to a target resolution. Pick the one that matches your screen — or whichever you prefer aesthetically.

| Preset | Pixels | Multiplier |
| --- | --- | --- |
| 240p | 352×240 | 0.16 |
| 360p | 480×360 | 0.25 |
| 480p | 640×480 | 0.33 |
| 576p | 768×576 | 0.40 |
| HD | 1280×720 | 0.50 |
| FHD | 1920×1080 | 0.75 |
| 1440p | 2560×1440 | 1.00 |
| UHD | 3840×2160 | 1.50 |
| 4K | 4096×2304 | 1.60 |
| 8K | 7680×4320 | 3.00 |

(Multipliers are defined in `BoxComponent.resolution_map`.)

---

## CSV Log

When `Logging` is enabled, every drawn frame is appended to in-memory buffers and flushed to `Documents/Assetto Corsa/logs/` on session shutdown:

* `LiveTelemetry_EN.csv` — engine
* `LiveTelemetry_FL.csv`, `LiveTelemetry_FR.csv`, `LiveTelemetry_RL.csv`, `LiveTelemetry_RR.csv` — per wheel

CSV uses `;` as separator, UTF-8 encoding, and one column per attribute of the per-window `Data` class. If `Logging` was off through the whole session, any pre-existing CSVs from previous runs are deleted on shutdown to avoid stale files.

---

## Installation

### Content Manager (recommended)

Drag the release `.7z` onto Content Manager and accept the install/update prompt. Settings are then editable from Content Manager → Settings → Live Telemetry:

![Live Telemetry Settings on Content Manager](https://raw.githubusercontent.com/albertowd/live-telemetry/master/resources/content-manager-app-settings.jpg)

### Manual install

Extract the `.7z` directly into your Assetto Corsa root (typically `C:/Program Files (x86)/steam/steamapps/common/assettocorsa`). In-game, enable the app under **Options → General → UI Modules → Live Telemetry**:

![Launcher Menu](https://raw.githubusercontent.com/albertowd/live-telemetry/master/resources/launcher-menu.jpg)

Then enter any session and pick the desired window from the right-hand app bar:

![Session Menu](https://raw.githubusercontent.com/albertowd/live-telemetry/master/resources/session-menu.jpg)

### Manual update

For 1.4.1+ just extract the new `.7z` over the AC folder. For older versions, delete `apps/python/LiveTelemetry/` first to avoid orphaned files.

---

## Developer Guide

### Prerequisites

* Assetto Corsa installed (the embedded Python 3.3 is the runtime — there is **no** local Python required to run the plugin).
* Optional: a regular Python 3 install + IDE (VS Code, PyCharm) for editing with autocomplete. AC's `ac` / `acsys` are stub-importable from `<AC>/apps/python/system/`.
* 7-Zip at `C:\Program Files\7-Zip\7z.exe` (used by `7z-maker.bat`).

### IDE setup

`.env` ships a `PYTHONPATH` pointing at the plugin folder and AC's stub system folder so editors can resolve `import ac` / `import acsys`. Adjust the AC path to match your install:

```
PYTHONPATH = D:/projects/live-telemetry/apps/python/LiveTelemetry;C:\Program Files (x86)\Steam\steamapps\common\assettocorsa\apps\python\system
```

### Iteration loop

1. Edit code under `apps/python/LiveTelemetry/`.
2. Symlink or copy the folder into `<AC>/apps/python/LiveTelemetry` (a junction works; AC reads the directory directly).
3. Restart the AC session — the plugin is loaded once per session.
4. Watch logs with `ac.console` output in-game and `ac.log` lines in `Documents/Assetto Corsa/logs/log.txt`. Both flow through `lt_util.log`.

### Linting

```bash
pylint apps/python/LiveTelemetry
```

`.pylintrc` keeps `max-line-length=180` and disables a handful of rules that don't fit the AC plugin model (the `ac`/`acsys` imports trigger `import-error`, the entry-point uses module-level globals, `__init__` legitimately stores many attributes, etc.).

### Packaging a release

```bat
7z-maker.bat 1.7.1
```

Produces `live-telemetry-1.7.1.7z` containing `apps/` and `content/`, excluding `*.psd` and `*.svg` source assets. The archive is the artefact you ship to Content Manager / RaceDepartment / GitHub Releases. Running `7z-maker.bat` with no argument defaults to the current `1.7.1` version.

### Adding a new option (worked example)

1. Add the default to `cfg/settings_defaults.ini` and to the `set_option` block in `Config.__init__` (`lt_config.py`).
2. Add an entry to the `__options` dicts in whichever info classes the option affects (`lt_engine_info.py`, `lt_wheel_info.py`, `lt_options_info.py`).
3. If the option toggles a widget, add the matching `Component` subclass in `lt_components.py` and append it to the `__components` list in the relevant info class — its `draw` is gated automatically because the dispatcher keys on `type(component).__name__`.
4. Add an `on_click_<name>` handler in `LiveTelemetry.py` and wire it with `ac.addOnClickedListener` inside `acMain`.
5. Mirror the option in `acShutdown` so it survives session restarts.
6. **Bump `LT_VERSION`** in `LiveTelemetry.py` *and* `cfg/settings_defaults.ini` so existing configs are reset rather than read with missing keys.

### Branches

`master` is the released line and matches the latest tag. `develop` and `release/x.y.z` track the in-flight version. `feature/*` and `hotfix/*` branches follow the gitflow naming convention.

---

## Changelog

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

---

## Known Bugs

Tracked on the GitHub issues page: <https://github.com/albertowd/live-telemetry/issues>.

---

## Acknowledgements

- [aluigi @ ZenHax](http://zenhax.com/viewtopic.php?f=9&t=90) — for patiently explaining how to open `.acd` files.
- `Please Stop This` (RaceDepartment) — for code contributions and review.
- `Jens Roos` (proTyres) — for reporting and helping fix integration issues.
- `giodelmare` — for testing suspension behaviour while my PC was dead.
