package org.abelpg.cwkeyer;

import java.util.Optional;

import lombok.extern.slf4j.Slf4j;
import net.codecrete.usb.Usb;
import net.codecrete.usb.UsbDevice;

@Slf4j
public class CwKeyer {


  private static final int VID = 0x413d;
  private static final int PID = 0x2107;

  // https://github.com/manuelbl/JavaDoesUSB
  public static void main(String[] args) {
    log.debug("Starting CW Keyer application...");
    for (var device : Usb.getDevices()) {
      System.out.println(device);
    }

    final Optional<UsbDevice> optionalDevice = Usb.findDevice(VID, PID);
    if (optionalDevice.isEmpty()) {
      log.info("No USB device with VID={} and PID={} ", VID, PID);
      return;
    }

    final UsbDevice device = optionalDevice.get();

    log.info("Found CW Keyer device interfaces: {}" , device.getInterfaces().getFirst().getNumber());

    try {
      device.open();
      device.claimInterface(0);

      byte [] arrayBytes = optionalDevice.get().transferIn(0x81, 64);

      System.out.println(arrayBytes);

    } catch (Exception e) {
      log.error("Failed to claim interface: " ,e);
      return;
    } finally {
      try {
        device.releaseInterface(0);
        device.close();
      } catch (Exception e) {
        log.error("Failed to claim interface: " ,e);
      }
    }


  }
}
