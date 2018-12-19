#!/bin/bash

# This is a simple bash script to install the dependencies for Beep_Inn
#
# Instructions:
# sudo chmod +x INSTALL.sh
# ./INSTALL.sh
#
# Script written by Wesley T. Honeycutt

# Check for Sudo
if [[ $UID != 0 ]]; then
    echo "Please run this script with sudo:"
    echo "sudo $0 $*"
    exit 1
fi

CURR=$(pwd)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

before_reboot() {
	logger BEEPINNINSTALL - Init
	echo ""
	echo "********************************************************"
	echo "*                                                      *"
	echo "*                                                      *"
	echo "* This script may require rebooting your Raspberry Pi. *"
	echo "*   Please be patient.  Have a coffee or something.    *"
	echo "*                                                      *"
	echo "* If something goes really wrong, and you start crying *"
	echo "*  First, Google with the error to look for solutions  *"
	echo "*    Then if that fails, contact us at our OU email    *"
	echo "*                                                      *"
	echo "*                                                      *"
	echo "*                                   With <3,           *"
	echo "*                                     Beep_Inn Devs    *"
	echo "*                                                      *"
	echo "********************************************************"
	sleep 3

	echo "Checking for and installing dependencies for Beep_Inn"
	# Always update your package manager
	sudo apt update

	# Get Up-to-date packages
	sudo apt -y upgrade

	# First things first, make sure Raspbian didn't come packaged with numpy.  That always breaks things.
	logger BEEPINNINSTALL - Attempting to remove default python3-numpy from apt.
	sudo apt remove -y python3-numpy

	if ! [ -x "$(command -v git)" ]; then
		echo 'Installing git (how did you get this file?)' >&2
		sudo apt -y install git
		logger BEEPINNINSTALL - Installing git
	else
		echo "git already installed..."
		logger BEEPINNINSTALL - git already installed
	fi

	if ! [ -x "$(command -v python3)" ]; then
		echo 'Installing python3' >&2
		sudo apt -y install python3
		logger BEEPINNINSTALL - Installing Python3
	else
		echo "python3 already installed..."
		logger BEEPINNINSTALL - Python3 already installed
	fi

	if ! [ -x "$(command -v pip3)" ]; then
		echo 'Installing pip3' >&2
		sudo apt -y install python3-pip
		logger BEEPINNINSTALL - Installing Pip3
	else
		echo "pip3 already installed..."
		logger BEEPINNINSTALL - Pip3 already installed
	fi

	if ! [ -x "$(command -v rtl_fm)" ]; then
		echo "Installing rtl_sdr tools...." >&2
		logger BEEPINNINSTALL - Installing rtl_sdr tools
		echo "Installing cmake, sox, and usb tools for rtl_sdr" >&2
		sudo apt -y install git cmake build-essential libusb-1.0-0-dev sox
		logger BEEPINNINSTALL - Installing cmake things and sox
		echo "Git\'ing files for rtl_sdr"
		cd "/home/$SUDO_USER/" || exit
		git clone git://git.osmocom.org/rtl-sdr.git
		cd rtl-sdr/ || exit
		echo "Building rtl_sdr"
		logger BEEPINNINSTALL - Begin Build
		mkdir build
		cd build || exit
		logger BEEPINNINSTALL - Build success
		echo "Making built rtl_sdr"
		cmake ../ -DINSTALL_UDEV_RULES=ON
		logger BEEPINNINSTALL - Cmake success
		make
		echo "Completing rtl_sdr install"
		sudo make install
		logger BEEPINNINSTALL - Instal success
		sudo ldconfig
		echo "Copying common rtl_sdr rules to system"
		sudo cp ../rtl-sdr.rules /etc/udev/rules.d
		echo "Creating 28xxu rules"
		echo "blacklist dvb_usb_rtl28xxu" | sudo tee -a /etc/modprobe.d/blacklist-rtl.conf
		cd "$CURR" || exit
		logger BEEPINNINSTALL - ldconfig and blacklist for rtlsdr success
	else
		echo "rtl_sdr already installed..."
		logger BEEPINNINSTALL - rtl_sdr is already on this system
	fi

	# We need to get rid of conflicting numpy version of default pi from apt.
 	#sudo apt -y remove python3-numpy
	# Instead, we need to have the wheel-maker set up for pip3
	sudo apt -y install libatlas3-base
	# We also need scipy installed, but the previous lines tend to mess with that
	sudo apt -y install python3-scipy
 	#logger BEEPINNINSTALL - removed apt numpy version and added libatlas3-base
 	logger BEEPINNINSTALL - added libatlas3-base, scipy

	# Now that everything apt is set up, we begin checking the pip packages.
	# Numpy is required for much of the array math
	# Tested with 1.15.4
	python3 -c 'import numpy'
	if [ $? != '0' ]; then
		pip3 install numpy --user
		logger BEEPINNINSTALL - Installing numpy
	fi
	echo "numpy version $(python3 -c 'import numpy; print(numpy.__version__)') is installed for python3"
	logger BEEPINNINSTALL - numpy $(python3 -c 'import numpy; print(numpy.__version__)')

	# Install matplotlib for more math things
	# Tested with 3.0.2
	python3 -c 'import matplotlib'
	if [ $? != '0' ]; then
		pip3 install matplotlib --user
		logger BEEPINNINSTALL - Installing matplotlib
	fi
	echo "matplotlib version $(python3 -c 'import matplotlib; print(matplotlib.__version__)') installed for python3"
	logger BEEPINNINSTALL - matplotlib $(python3 -c 'import matplotlib; print(matplotlib.__version__)')


	# Peakutils is used to find our peaks
	# Tested with 1.3.0
	python3 -c 'import peakutils'
	if [ $? != '0' ]; then
		pip3 install --user peakutils
		logger BEEPINNINSTALL - Installing peakutils
	fi
	echo "peakutils version $(python3 -c 'import peakutils; print(peakutils.__version__)') is installed for python3"
	logger BEEPINNINSTALL - peakutils $(python3 -c 'import peakutils; print(peakutils.__version__)')


	# Pyrtlsdr is what runs the sdr from python.
	# Tested with 0.2.9
	python3 -c 'import rtlsdr'
	if [ $? != '0' ]; then
		pip3 install --user pyrtlsdr
		logger BEEPINNINSTALL - Installing pyrtlsdr
	fi
	echo "rtlsdr version $(python3 -c 'import rtlsdr; print(rtlsdr.__version__)') is installed for python3"
	logger BEEPINNINSTALL - pyrtlsdr $(python3 -c 'import rtlsdr; print(rtlsdr.__version__)')

	# We have to configure raspi-config to allow UART.
	# This event requires restart
	if grep -q -x enable_uart=1 /boot/config.txt; then
		logger BEEPINNINSTALL - UART already enabled in /boot/config.txt
	else
		echo "enable_uart=1" | sudo tee -a /boot/config.txt
		logger BEEPINNINSTALL - UART now enabled in /boot/config.txt
	fi

	# Desktop shortcut
	touch /home/$USER/Beep_Inn
	tee /home/$USER/Beep_Inn << EOF
[Desktop Entry]
Name=Beep_Inn
Comment=Activates the Beep_Inn script
Icon=/usr/share/pixmaps/python3.xpm
EOF
	ESTRING="Exec=python3 $DIR/beep_inn_main.py -f $DIR/input_frequency_example.txt"
	echo $ESTRING >> /home/$USER/Beep_Inn
	tee /home/$USER/Beep_Inn << EOF
Type=Application
Encoding=UTF-8
Terminal=true
Categories=None;
EOF

	# Force reboot
	logger BEEPINNINSTALL - Time to reboot
	sudo reboot
}

# Run program
logger BEEPINNINSTALL - Executing INSTALL.sh
before_reboot





# # Raspberry Pi 3 Only
# # Set Up WiFi Access Point on Raspberry Pi
# # First, download the required packages.
# sudo apt -y install hostapd dnsmasq
# # Ignore the wireless interface
# sudo cat >> /etc/dhcpcd.conf << EOF
# denyinterfaces wlan0
# EOF
# # Next, we set up a static IP for wlan0
# sudo cat >> /etc/network/interfaces << EOF
# auto lo
# iface lo inet loopback
# 
# auto eth0
# iface eth0 inet dhcp
# 
# allow-hotplug wlan0
# iface wlan0 inet static
#     address 192.168.42.1
#     netmask 255.255.255.0
#     network 192.168.42.0
#     broadcast 192.168.42.255
# EOF
# # Now we set up hostapd to act like an access point
# sudo cat >> /etc/hostapd/hostapd.conf << EOF
# interface=wlan0
# driver=nl80211
# ssid=RPiAccessPoint
# hw_mode=g
# channel=5
# ieee80211n=1
# wmm_enabled=1
# ht_capab=[HT40][SHORT-GI-20][DSSS_CCK-40]
# macaddr_acl=0
# auth_algs=1
# ignore_broadcast_ssid=0
# wpa=2
# wpa_key_mgmt=WPA-PSK
# wpa_passphrase=raspberryBridge
# rsn_pairwise=CCMP
# EOF
# # Note here that the password needs to be changed. I used wifi channel=5 for a reason.
# # We tell hostapd to use the config we set up by uncommenting the DAEMON_CONF line and adding the path
# sudo sed -i -e 's/\#DAEMON_CONF\=\"\"/DAEMON_CONF\=\"\/etc\/hostapd\/hostapd.conf\"/g' /etc/default/hostapd
# # Let's now configure the dnsmasq program using:
# sudo cat >> /etc/dnsmasq.conf << EOF
# interface=wlan0 
# listen-address=192.168.42.1
# bind-interfaces 
# server=8.8.8.8
# domain-needed
# bogus-priv
# dhcp-range=192.168.42.100,192.168.42.200,24h
# EOF
# 
# 
# # Set up TMPFS options to enable RAM recording that doesn't wreck SD cards
# sudo mkdir /var/tmp/LunAero
# echo "" | sudo tee -a /etc/fstab
# echo "#LunAero Temp folder" | sudo tee -a /etc/fstab
# echo "tmpfs   /var/tmp/LunAero    tmpfs    defaults,noatime,nosuid,mode=0755,size=100m    0 0" | sudo tee -a /etc/fstab
# 
# # Set up the server program to run automatically on startup.
# BASEDIR=$(dirname "$0")
# sudo cp $(echo $BASEDIR"/LunAeroServer/Lserver.py") /etc/Lserver.py
# sudo sed -i -e '$i \sudo python3 /etc/Lserver.py &\n' /etc/rc.local

# Finish and reboot
# sudo reboot
