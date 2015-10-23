# LaserQueue
A queue system for NuVu’s laser cutter and other CNC hardware. [NuVu Studio](https://cambridge.nuvustudio.com/discover) has a lasercutter, and *only* one of them. A lot of people want to use it, and managing it is a giant pain. This software aims to simplify that with a simple web-based software accessible locally. It is developed primarily by [@sdaitzman](https://github.com/sdaitzman) and [@yrsegal](https://github.com/yrsegal). You can use it to control access to a 3D printer, lasercutter, printer... whatever you want!

This file is an overview. Full API docs are in [api.md](./API.md) and config docs are in [config.md](./www/config.md). Info about plugins is in [plugins.md](./plugins/plugins.md).

## Getting the software
Download the latest stable version from [github.com/yrsegal/LaserQueue/releases](https://github.com/yrsegal/LaserQueue/releases) and decompress it.

## Running the software

Get the latest version by `git clone`ing the repo or downloading a zip. If there's a new update, the program will prompt you on run automatically.  

To start the server, run `start.sh` or `start.py` or `start.bat` if you're on Windows. You'll need Python 3.4.x or greater.

To change the admin login password, run the script with `--new-password`.

### Flags:

- `-h`, `--help`: Display a list of these flags. Does not start the backend.
- `-p`, `--port`: Set the port for the website to be hosted.
- `-l`, `--local`: Start the backend in local mode. You'll connect with localhost.
- `-v`, `--verbose`: Extra and more informative output from the backend. Doesn't apply if `-q` is used.
- `-q`, `--quiet`: Start without output. Only applies to start.sh. Equivalent to `>/dev/null`.
- `-b`, `--queue-backup`: Enable queue backups. The queue will load from the cache on start, and cache every 20 seconds.
- `-r`, `--regen-config`: Regenerate the config. Accepts positional arguments in the form `-r key key2 key3 ...`. If it recieves positionals, it will only regenerate those config values.
- `-S`, `--no-install`: Does not install dependencies that are not met. Otherwise, you will be prompted unless you use `--install-all`.
- `-U`, `--no-update`: Does not install or prompt for updates.
- `-P`, `--no-plugins`: Does not load plugins.
- `-H`, `--no-regen-host`: Do not regenerate the host in the config. Does not affect any other config values.
- `--new-password`: No short option. Allows you to reset the admin password from within the program.
- `--backend`: No short option. Only runs the backend.
- `--frontend`: No short option. Only runs the frontend.
- `--init-only`: No short option. Runs neither the frontend nor the backend.
- `--no-init`: No short option. Doesn't run the setup.
- `--install-all`: No short option. Installs all dependencies without prompting.
- `--install-update`: No short option. Installs updates without prompting.

### Backend API
Want to access the backend? Send it signals? Control your list with a custom frontend? Make changes to the backend or frontend? See [API.md](API.md)!

## Dependencies

All dependencies should be met the first time you run the program. The program will detect your system and prompt to install them. However, you will definitely need Python at ≥ 3.4.x for WebSockets. If (for some reason) you would like to install these by hand, feel free:

###Required to start:  
- [Python 3.4.x](https://www.python.org/downloads/)
- pip (`#~ curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | sudo python3`)

###Other dependencies (installed on runtime):  
- websockets (`#~ pip3 install websockets`)
- netifaces (`#~ pip3 install netifaces`)
- GitPython (`#~ pip3 install GitPython`)

[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/yrsegal/laserqueue/trend.png)](https://bitdeli.com/free “Bitdeli Badge”)
