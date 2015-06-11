# LaserQueue
A queue system for NuVu’s laser cutter, with websockets. [NuVu Studio](https://cambridge.nuvustudio.com/discover) has a lasercutter, and *only* one of them. A lot of people want to use it, and managing it is a pain. This software aims to simplify that with a simple web-based frontend accessible locally and on a TV mounted in the wall. It is developed primarily by [@sdaitzman](https://github.com/sdaitzman) and [@yrsegal](https://github.com/yrsegal).

## Getting the software
Download the latest stable version from [github.com/yrsegal/LaserQueue/releases](https://github.com/yrsegal/LaserQueue/releases) and decompress it.

## Running the software

Get the latest version by `git clone`ing the repo or downloading a zip. If there's a new update, the program will prompt you on run.  

To start the server, run `start.sh` or `start.py`. You'll need Python 3.4.x or greater.

To change the admin login password, create a plaintext file `password` under backend. This will be hashed upon script run.

### Flags:

- `-h`, `--help`: Display a list of these flags. Does not start the backend.
- `-p`, `--port`: Set the port for the website to be hosted.
- `-l`, `--local`: Start the backend in local mode. You'll connect with localhost.
- `-q`, `--quiet`: Start without output. Only applies to start.sh. Equivalent to >/dev/null.
- `-b`, `--queue-backup`: Enable queue backups. The queue will load from the cache on start, and cache every 20 seconds.
- `-r`, `--regen-config`: Regenerate the config. This is the default option if no config.json file is found in WWW
- `-n`, `--regen-host`: Regenerate the host in the config. Does not affect any other config values. 
- `-s`, `--skip-install`: Does not install dependencies that are not met. Otherwise, you will be prompted unless you use `--install-all`.
- `-nu`, `--no-update`: Does not install or prompt for updates.
- `--install-all`: No short option. Installs all dependencies without prompting.
- `--install-update`: No short option. Installs updates without prompting.

## Dependencies

All dependencies should be met the first time you run the program. The program will detect your system and prompt to install them. However, you will definitely need Python >=3.4.x for WebSockets. If (for some reason) you would like to install these by hand, feel free:

- [Python 3.4.x](https://www.python.org/downloads/)
- websockets (`#~ pip3 install websockets`)
- netifaces (`#~ pip3 install netifaces`)
- GitPython (`#~ pip3 install GitPython`)

[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/yrsegal/laserqueue/trend.png)](https://bitdeli.com/free “Bitdeli Badge”)

