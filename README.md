# CW Keyer

A Morse code (CW) iambic keyer application for Windows, built with Python and PySide6. It supports both keyboard and USB paddle input devices, generates audio tones, and can emulate serial/comm output.

---

## Features

- **Iambic keyer** logic with configurable WPM (words per minute)
- **Keyboard input**: Use `Left Ctrl` (dit) and `Right Ctrl` (dah) as paddle keys
- **USB HID input**: Connect a physical USB paddle (via Zadig driver)
- **Audio tone generation**: Real-time CW sidetone
- **Comm emulator**: Virtual serial port / comm output
- **Graphical interface**: PySide6 GUI

---

## Requirements

- Python 3.10+
- [PySide6](https://pypi.org/project/PySide6/)
- [pyusb](https://pypi.org/project/pyusb/)
- [pynput](https://pypi.org/project/pynput/)
- `libusb-1.0.dll` (included in `libs/`)

Install dependencies:

```bash
pip install PySide6 pyusb pynput
```

---

## Usage

```bash
python app.py
```

Or run the pre-built executable:

```
build/app/app.exe
```

---

## Architecture

### `core/device/`

#### `Device` (Abstract Base Class)

Base class for all input devices. Manages a list of `DeviceObserver` instances and notifies them when dit or dah signals change state.

| Method | Description |
|---|---|
| `attach_observer(observer)` | Register an observer to receive dit/dah events |
| `detach_observer(observer)` | Unregister an observer |
| `start()` *(abstract)* | Start the device |
| `stop()` *(abstract)* | Stop the device |

---

#### `KeyboardDevice`

Implements `Device` using the keyboard as a paddle input via `pynput`.

| Key | Signal |
|---|---|
| `Left Ctrl` | **Dit** (dot) |
| `Right Ctrl` | **Dah** (dash) |

| Method | Description |
|---|---|
| `start()` | Starts the keyboard listener |
| `stop()` | Stops the keyboard listener |

---

#### `ZadigUsbDevice`

Implements `Device` for USB HID paddle devices using `pyusb` and the `libusb` backend (via Zadig driver on Windows).

Reads raw HID data from the USB endpoint and maps button states to dit/dah signals.

| Constant | Value | Meaning |
|---|---|---|
| `CLICK_LEFT` | `0x01` | Dit |
| `CLICK_RIGHT` | `0x02` | Dah |
| `CLICK_BOTH` | `0x03` | Dit + Dah |

| Method | Description |
|---|---|
| `start()` | Starts the USB polling thread |
| `stop()` | Stops the USB polling thread |
| `is_running()` | Returns `True` if polling is active |
| `get_hid_devices()` *(static)* | Scans and returns a list of available HID devices as `HidDeviceItem` objects |

**Tested devices:**

| Vendor ID | Product ID | Interface | Endpoint | Max Packet Size |
|---|---|---|---|---|
| `0x413d` | `0x2107` | `1` | `0x82` | `4` |

> **Note:** On Windows, you must install the WinUSB driver for your USB paddle using [Zadig](https://zadig.akeo.ie/) before the device can be detected.

---

#### `HidDeviceItem`

Represents a discovered USB HID device. Automatically marks devices as `(DEVICE OK)` if they match the tested device list.

| Method | Description |
|---|---|
| `build_key()` | Returns a unique string key for the device |
| `build_vendor_product_id_from_key(key)` *(static)* | Parses a key string back into device parameters |

---

### `core/keyer/Keyer`

Implements the iambic keyer state machine. Listens to a `Device` via the `DeviceObserver` interface and generates dit/dah timing sequences.

- Time base: `1200 ms` per dit at 1 WPM
- Thread-safe with locking to prevent concurrent state modification

---

### `core/sound/`

Handles audio tone generation for the CW sidetone.

---

### `core/emulator/`

Provides serial/comm port emulation, optionally integrated with the keyer.

---

### `gui/`

PySide6 GUI components:
- `AppGui` — Main application window
- `DevicesForm` — USB/keyboard device selection
- `KeyerForm` — Keyer settings (WPM, etc.)
- `SoundForm` — Audio settings
- `CommEmulatorNoKeyerForm` / `CommEmulatorKeyerForm` — Comm emulator panels

---

## Installing USB Driver (Windows)

1. Download and run [Zadig](https://zadig.akeo.ie/) (included in `doc/zadig-2.9.exe`)
2. Select your USB paddle device
3. Install the **WinUSB** driver
4. Launch the application and select the device from the GUI

---

## License

See [LICENSE](LICENSE).

