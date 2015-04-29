# LaserQueue
A queue system for [NuVu](https://cambridge.nuvustudio.com/discover)’s laser cutter, with websockets.

## About

[NuVu Studio](https://cambridge.nuvustudio.com/discover) has a lasercutter, and *only* one of them. A lot of people want to use it, and managing it is a pain. This software aims to simplify that with a simple web-based frontend accessible locally and on a TV mounted in the wall.

## Dependencies

All dependencies should be met the first time you run the program. The program will detect your system and prompt to install them. However, you will definitely need Python >=3.4.x for WebSockets.

- [Python 3.4.x](https://www.python.org/downloads/)
- netifaces (`#~ pip3 install netifaces`)
- On Windows: pyautoit, pyserial (installing these manually on Windows is not recommended)

[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/yrsegal/laserqueue/trend.png)](https://bitdeli.com/free “Bitdeli Badge”)

