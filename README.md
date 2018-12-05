# Beep_Inn
Code for a wildlife tracking receiver for use with RTL-SDR.

Prerequisites:
 - Python3
 - Configured RTL-SDR system (see notes)
 - Linux (maybe, haven't tried others)
 
 Pip3 Prerequisites:
  - pyrtlsdr


**Installing RTL_SDR Prerequisites:**
```
sudo apt update
sudo apt install git cmake build-essential libusb-1.0.-0-dev sox
git clone git://git.osmocom.org/rtl-sdr.git
cd rtl-sdr/
mkdir build
cd build
cmake ../ -DINSTALL_UDEV_RULES=ON
make
sudo make install
sudo ldconfig
sudo cp ../rtl-sdr.rules /etc/udev/rules.d
```
This is all quite humdrum, but we need to allow our machine to use this device.  To do this, we want to add a kernel module.
```
sudo nano /etc/modprobe.d/blacklist-rtl.conf
```
If this file doesn't exist, use ``touch`` to make it.  Within the blacklist file add a line:
```
blacklist dvb_usb_rtl28xxu
```

We now have the following programs available to us:
```
rtl_adsb    rtl_eeprom  rtl_fm      rtl_power   rtl_sdr     rtl_tcp     rtl_test
```
Running ``rtl_test`` can tell us if the device is working.  If we want to listen to the SDR device, we need to use ``rtl_fm``.  But just running that program doesn't do much.  We have to tell it to play through our audio device.  To do that, we pipe the output from ``rtl_fm`` to  ``sox`` via the command ``play``.  Observe:

For standard FM radio channels:
```
rtl_fm -M wbfm -f 89.1M | play -r 32k -t raw -e s -b 16 -c 1 -V1 -
```

For the police scanner frequency:
```
rtl_fm -M fm -f 154.42M -f 154.75M -f 154.82M -f 154.89M -s 12k -g 50 -l 70 | play -r 12k ...
```

Civil aviation bandwidths:
```
rtl_fm -M am -f 118M:137M:25k -s 12k -g 50 -l 280 | play -r 12k ...
```
