**This python package is unofficial and is not related in any way to Telekom. It was developed by reversed engineered http requests and can stop working at anytime!**
  
## Speedport-API
[![PyPI - Status](https://img.shields.io/pypi/status/speedport-api-expanded)](https://pypi.org/project/speedport-api-expanded/)
[![PyPI](https://img.shields.io/pypi/v/speedport-api-expanded?color=blue)](https://pypi.org/project/speedport-api-expanded/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/speedport-api-expanded)](https://www.python.org/)
[![PyPI - License](https://img.shields.io/pypi/l/speedport-api-expanded)](https://github.com/kplrm/speedport-api-expanded/blob/main/LICENSE)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/speedport-api-expanded)](https://pypistats.org/packages/speedport-api-expanded)

Control Telekom Speedport routers with Python!

### Installation
```commandline
pip install speedport-api-expanded
```

For this fork's changes, install from a checkout with `python -m pip install -e .`
or download a wheel from [GitHub releases](https://github.com/kplrm/speedport-api-expanded/releases).
The Python import remains `from speedport import Speedport`.
See [local development and adding features](docs/development.md),
[contribution guidelines](CONTRIBUTING.md), and [contributors](CONTRIBUTORS.md).
Store local router credentials in an
ignored `.env` copied from [.env.example](.env.example); see the guide for loading it.

### Supported Devices
* Speedport Smart 4

### Commandline tool
With this shipped commandline tool can a speedport in your network be controlled.

#### Turn wifi off
```commandline
$ speedport wifi off
Turn off wifi...
```

#### Turn guest wifi on
```commandline
$ speedport guest-wifi on
Turn on guest wifi...
```

#### Reconnect for new ip address
```commandline
$ speedport reconnect
123.45.67.89 / 5403:f3:35aa:12f:7287:41cf:fb1c:3c83
Reconnect with internet provider...
123.45.67.12 / 5403:f3:35fe:12f:7287:41cf:fb1c:3c83
```

#### Query IPv4 and IPv6 information
```commandline
speedport --host 192.168.2.1 ip-info
speedport --host 192.168.2.1 --batch ip-info
```
Prints addresses, gateways, primary/secondary DNS servers, and IPv6 prefixes.
Batch output uses tab-separated field/value pairs. A password is prompted for
unless `SPEEDPORT_PASSWORD` is set.

To print only the public IPv4 address, without a label or table:
```commandline
python -m speedport --host 192.168.2.1 ip-info --ipv4
93.218.250.118
```
If no public IPv4 address is available, the command exits with an error.

#### Enable wps connect
```commandline
$ speedport wps
Enable wps connect...
wps connect enabled for 113s...
```

#### Reboot device
```commandline
$ speedport reboot
Reboot speedport...
```

#### Print devices
```commandline
$ speedport devices
+-------------+---------------------+-------+-----------+
| ipv4        | name                | type  | connected |
+-------------+---------------------+-------+-----------+
| 10.5.12.32  | Google-Home-Mini-1  | wlan  | 1         |
| 10.5.12.157 | PC10-5-12-157       | lan   | 0         |
| 10.5.12.227 | andre-xps           | wlan5 | 1         |
```


#### Print calls
```commandline
$ speedport calls
+-------------+--------+----------+---------------------+
| number      | type   | duration | date                |
+-------------+--------+----------+---------------------+
| 01578212345 | missed | 0        | 2024-04-04 09:34:35 |
| 026361245   | taken  | 1337     | 2024-04-06 05:12:53 |
| 7866        | dialed | 20       | 2024-04-06 18:39:00 |
```

### Library

#### IP information example
```python
import asyncio
import os
from speedport import Speedport

async def ip_info():
    async with Speedport(
        os.environ.get("SPEEDPORT_HOST", "192.168.2.1"),
        os.environ["SPEEDPORT_PASSWORD"],
    ) as router:
        info = await router.ip_info
        print(info["public_ip_v4"], info["public_ip_v6"])
        print(info)  # All fields, including DNS servers and IPv6 prefixes.

asyncio.run(ip_info())
```

#### Reconnect example
```python
import asyncio
from speedport import Speedport

async def reconnect():
    speedport =  Speedport("192.168.1.1")
    await speedport.login("password123")
    await speedport.reconnect()

asyncio.run(reconnect())
```

#### Devices example
```python
import asyncio
from speedport import Speedport

devices = asyncio.run(Speedport().devices)
for device in devices:
    print(device.ipv4, device.connected)
```
