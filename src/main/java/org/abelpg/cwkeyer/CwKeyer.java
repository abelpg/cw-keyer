package org.abelpg.cwkeyer;

import java.util.Optional;

import net.codecrete.usb.Usb;
import net.codecrete.usb.UsbDevice;

public class CwKeyer {


  private static final int VID = 0x413d;
  private static final int PID = 0x2107;

  // https://github.com/manuelbl/JavaDoesUSB
  public static void main(String[] args) {
    System.out.println("Hello, CW Keyer!");
    for (var device : Usb.getDevices()) {
      System.out.println(device);
    }

    final Optional<UsbDevice> optionalDevice = Usb.findDevice(VID, PID);
    if (optionalDevice.isEmpty()) {
      System.out.printf("No USB device with VID=0x%04x and PID=0x%04x found.%n", VID, PID);
      return;
    }

    final UsbDevice device = optionalDevice.get();

    System.out.println("Found CW Keyer device interfaces: " + device.getInterfaces().getFirst().getNumber());





    try {
      device.detachStandardDrivers();
      device.open();
      device.claimInterface(1);

      byte [] arrayBytes = optionalDevice.get().transferIn(0x81, 64);

      System.out.println(arrayBytes);

    } catch (Exception e) {
      System.err.println("Failed to claim interface: " + e.getMessage());
      return;
    } finally {
      try {
        device.releaseInterface(1);
        device.close();
        device.attachStandardDrivers();
      } catch (Exception e) {
        System.err.println("Failed to release interface: " + e.getMessage());
      }
    }


  }
}
