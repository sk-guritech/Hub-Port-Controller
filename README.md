# Hub-Port-Controller
You can controller USB hub port power feature and view port status by this script.

## Usage
```
usage: hub-port-controller.py [-h] [-s HUB_SERIAL_NUMBER] [-v USB_VERSION]
                              [-p PORT_NUMBERS] [-d]
                              hub_id_vendor hub_id_product
```

## Examples
```
# Restart USB Devices
sudo python3 0x2109 0x3431 -p [1,2,3,4]
```

```
# Display Port Statuses
sudo python3 0x2109 0x3431 -d
```


## Requirements
```
pyusb
```

## License
Copyright (c) 2020 S.K. Technology Firm, @GuriTech  
Released under the MIT License