# CW Keyer

A Morse code (CW) iambic keyer application for Windows, built with Python and PySide6. It supports keyboard and USB paddle input, real-time audio sidetone generation, serial/comm port output, and N1MM Logger integration.

---

## Features

- **Iambic keyer** state machine with Ultimatic, Iambic A, and Iambic B modes (default: Iambic B)
- **Keyboard input**: Use `;` (dit) and `=` (dah) keys as paddle input
- **USB HID input**: Connect a physical USB paddle (via Zadig/WinUSB driver)
- **Real-time audio sidetone**: Soft tone generation with attack/release envelope using PyAudio and NumPy
- **Comm emulator (no keyer)**: Pass-through serial port output for use with CWType (RTS = dah, DTR = dit)
- **Comm emulator (with keyer)**: Keyer-timed DTR pulses over serial port
- **Keyboard emulator**: Re-maps USB paddle to `Left Ctrl` (dit) / `Right Ctrl` (dah) for use with Morse Invaders or similar games
- **N1MM Logger integration**: Monitors DSR line on a serial port and forwards signals through the keyer
- **Graphical interface**: PySide6 GUI
- **High process priority**: Runs at `ABOVE_NORMAL_PRIORITY_CLASS` for better timing accuracy

---

## Requirements

- Python 3.10+
- [PySide6](https://pypi.org/project/PySide6/)
- [pyusb](https://pypi.org/project/pyusb/)
- [pynput](https://pypi.org/project/pynput/)
- [pyaudio](https://pypi.org/project/PyAudio/)
- [numpy](https://pypi.org/project/numpy/)
- [pyserial](https://pypi.org/project/pyserial/)
- [hid](https://pypi.org/project/hid/)
- `libusb-1.0.dll` (included in `libs/`)

Install dependencies:

```bash
pip install PySide6 pyusb pynput pyaudio numpy pyserial hid
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

## Configuration

Application settings are stored in `config.ini`. A `show_zadig` option (under the `AppGui` section) controls whether the USB-specific keyboard emulator button is shown in the GUI.

---

## Architecture

### `core/device/`

#### `Device` (Abstract Base Class)

Base class for all input devices. Manages a list of `DeviceObserver` instances and notifies them on dit/dah state changes.

| Method | Description |
|---|---|
| `attach_observer(observer)` | Register an observer to receive dit/dah events |
| `detach_observer(observer)` | Unregister an observer |
| `start()` *(abstract)* | Start the device |
| `stop()` *(abstract)* | Stop the device |

---

#### `KeyboardDevice`

Implements `Device` using the keyboard as paddle input via `pynput`.

| Virtual Key Code | Signal |
|---|---|
| `186` (`;` key) | **Dit** (dot) |
| `187` (`=` key) | **Dah** (dash) |

| Method | Description |
|---|---|
| `start()` | Starts the keyboard listener |
| `stop()` | Stops the keyboard listener |

---

#### `ZadigUsbDevice`

Implements `Device` for USB HID paddle devices using `pyusb` and the `libusb` backend (via Zadig WinUSB driver on Windows).

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

**Tested devices (marked as `DEVICE OK`):**

| Vendor ID | Product ID | Interface | Endpoint | Max Packet Size | Notes |
|---|---|---|---|---|---|
| `0x413d` | `0x2107` | `0` | `0x81` | `8` | Vail adapter |
| `0x413d` | `0x2107` | `1` | `0x82` | `4` | Left/Right click |

> **Note:** On Windows, you must install the WinUSB driver for your USB paddle using [Zadig](https://zadig.akeo.ie/) before the device can be detected.

---

#### `HidDeviceItem`

Represents a discovered USB HID device. Automatically marked as `(DEVICE OK)` if it matches a known tested configuration.

| Method | Description |
|---|---|
| `build_key()` | Returns a unique string key: `vendor_id:product_id:interface:endpoint:max_packet_size` |
| `build_vendor_product_id_from_key(key)` *(static)* | Parses a key string back into device parameters |

---

### `core/keyer/`

#### `Keyer`

Implements the iambic keyer state machine. Listens to a `Device` via the `DeviceObserver` interface and generates timed dit/dah sequences.

**Supported modes** (`Mode` enum):

| Mode | Description |
|---|---|
| `ULTIMATIC` | Repeats the last paddle pressed when both are held |
| `IAMBIC_A` | Alternates dit/dah while both paddles are squeezed |
| `IAMBIC_B` | Like Iambic A, but completes one extra element after release *(default)* |

**Timing** (PARIS standard — time base: `1200 ms` at 1 WPM):

| Formula | Description |
|---|---|
| Dit = `1200 ms / WPM` | Base timing unit |
| Dah = `3 × Dit` | Dash duration |
| Inter-element space = `1 × Dit` | Space between elements |

Example speeds:

| WPM | Dit | Dah |
|---|---|---|
| 15 | 80 ms | 240 ms |
| 20 | 60 ms | 180 ms |
| 24 | 50 ms | 150 ms |
| 30 | 40 ms | 120 ms |

| Method | Description |
|---|---|
| `start()` | Starts the tone generator |
| `stop()` | Stops the tone generator and serial output |
| `start_serial(port)` | Starts keyer-timed serial output on the given port |
| `stop_serial()` | Stops serial output |
| `proxy_n1mm(value)` | Enables/disables N1MM continuous tone forwarding |

---

#### `ToneGenerator`

Generates real-time CW sidetone audio using `pyaudio` and `numpy`. Tones use a soft attack/release envelope to avoid clicks. Audio data is cached for performance.

| Method | Description |
|---|---|
| `start()` | Opens the audio output stream |
| `stop()` | Closes the audio stream |
| `play_tone(tone_duration, silence_duration)` | Plays a tone followed by silence |
| `continuous_tone(sound)` | Starts or stops a continuous tone (used for N1MM PTT) |
| `get_available_output_devices()` *(static)* | Returns a sorted list of `AudioDevice` objects |

##### `AudioDevice`

Represents a system audio output device (index, name, default sample rate).

---

#### `CommEmulatorWithKeyer`

Sends keyer-timed DTR pulses over a serial port. Used to drive external CW interfaces that read DTR timing.

| Method | Description |
|---|---|
| `send_signal_background(duration)` | Sends a timed DTR pulse asynchronously |
| `turn_on()` | Sets DTR high |
| `turn_off()` | Sets DTR low |

---

#### `N1MMProxy`

Monitors the DSR line on a serial port and forwards high/low transitions to the `Keyer` via `proxy_n1mm()`. Enables N1MM Logger to trigger the keyer's continuous tone and PTT.

| Method | Description |
|---|---|
| `start()` | Starts serial monitoring |
| `stop()` | Stops serial monitoring |
| `is_running()` | Returns `True` if monitoring is active |

---

### `core/emulator/`

#### `CommEmulator`

A `DeviceObserver` that directly mirrors paddle state to serial port lines (no keyer timing). Useful for applications like CWType.

| Signal | Serial Line |
|---|---|
| Dit | DTR |
| Dah | RTS |

---

#### `KeyboardEmulator`

A `DeviceObserver` that maps paddle events to keyboard key presses. Useful for games or applications that accept `Ctrl` key input as paddle.

| Signal | Key |
|---|---|
| Dit | `Left Ctrl` |
| Dah | `Right Ctrl` |

---

#### `CommSerial`

Base class that manages a `pyserial` serial port connection.

| Method | Description |
|---|---|
| `start()` | Opens the serial port |
| `stop()` | Closes the serial port |
| `list_ports()` *(static)* | Returns available COM port names |

---

### `core/config/`

#### `Configuration`

Reads and writes application settings from `config.ini`.

---

### `gui/`

PySide6 GUI components:

| Component | Description |
|---|---|
| `AppGui` | Main application window |
| `DevicesForm` | Device selection (keyboard / USB HID) |
| `KeyerForm` | Keyer settings (WPM, frequency, amplitude, audio device, serial port) |
| `CommEmulatorNoKeyerForm` | Direct pass-through serial emulator panel (CWType) |
| `CommEmulatorKeyerForm` | Serial emulator with keyer timing panel |
| `N1MMForm` | N1MM Logger integration panel |

---

## Installing USB Driver (Windows)

1. Download and run [Zadig](https://zadig.akeo.ie/) (included in `doc/zadig-2.9.exe`)
2. Select your USB paddle device from the dropdown
3. Install the **WinUSB** driver
4. Launch the application and select the device from the **Devices** panel

---

## License

See [LICENSE](LICENSE).
