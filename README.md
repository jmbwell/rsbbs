# Really Simple BBS

[![Maintainability](https://api.codeclimate.com/v1/badges/d21cbff7e4708d58d91b/maintainability)](https://codeclimate.com/github/jmbwell/rsbbs/maintainability)

A message board for packet radio, suitable for use with ax25d. 

Really Simple BBS (`rsbbs`) implements a bulletin board system that enables
radio amateurs to read and store messages at your station. It generally adopts
conventions common to other popular BBS systems, (`B`, `J`, `K`, `L`, `R`, `S`,
`H`, etc.)

It is designed to run on a linux system when called by `ax25d`. That is, when a
user calls your station, `ax25d` answers the call and routes the connection to
`rsbbs` via standard input (`stdin`). `rsbbs` responds to the user through
`ax25d` via standard output (`stdout`).

## Features

- **Send and receive messages:** Send a message to another user by callsign, or read messages sent to you.
- **Private messages:** Send a private message readable only by the user.
- **Simple setup:** Install it, add it to your ax25d.conf, done!
- **Plugin architecture:** Add your own commands with simple plugin modules
- **Access logging:** Keep an eye on your BBS's activity

## Requirements

- **AX.25:** It is assumed that you have a radio connected to your host, that
  you have configured your axports, and that ax25d can answer calls.
- **Python 3:** As this is a python 3 application, you will need python 3 and
  pip. 
- **Hardware:** A system capable of running Direwolf and ax25d should be more
  than sufficient.

## Installation

Clone this repository and install it with pip:

```
git clone https://git.b-wells.us/jmbwell/rsbbs.git
cd rsbbs
python3 -m virtualenv .venv
source .venv/bin/activate
pip install .
rsbbs -h
```

The config file will be created at first launch. 

## Configuration

By default, the `config.yaml` file lives in your system's user config
directory, such as `~/.config/rsbbs/config.yaml`, as determined by the
`platformdirs` module.

To use a `config.yaml` file from a different location, use the `-f` option:
```
rsbbs -f ~/config.yaml -s <calling station's callsign>
```

Either way, if the file is missing, `rsbbs` will create it.

The `config.yaml` file is pretty simple and self-explanatory for now:
```
bbs_name: John's Really Simple BBS
callsign: HOSTCALL
banner_message: Leave a message!
command_prompt: ENTER COMMAND >
```

> Tip:
> To show the location of the current config file (among other configuration
> options), run:
> ```
> rsbbs --show-config
> ```

## Usage

### With ax25d

Assuming you have `ax25d` working on your system, add something like the
following to your `ax25d.conf` file:

```
[KI5QKX-10 via vhf0]
default   * * * * * *  *    root    /usr/local/bin/rsbbs rsbbs -s %U
```

> Notes:
>  - Specify the full path to the `rsbbs` application.
>  - The installation path may vary on your system. 
>  - If you install it in a virtualenv, specify the path to `rsbbs` in that
>    virtualenv's `/bin` directory.
>  - Be sure to specify the `-s %U` parameter; this passes the ax.25 caller's
>    callsign to the `rsbbs` application.


See `man ax25d.conf` for more details.

### Directly

You can launch it from the command line on your packet station's host, and you
can interact with it just as you would over the air.

This might be useful for administration purposes or just to talk to yourself.
It does not have a standalone mode for taking calls, however -- that's what
ax25d is for.

```
rsbbs -s URCALL
```

### Options

Run `rsbbs -h` to see the following help:

```
usage: rsbbs [-h] [-d] -s CALLING_STATION [-f CONFIG_FILE] [-v]

options:
  -h, --help            show this help message and exit
  -d, --debug           Enable debugging output to stdout
  -s CALLING_STATION, --calling-station CALLING_STATION
                        The callsign of the calling station
  -f CONFIG_FILE, --config-file CONFIG_FILE
                        specify path to config.yaml file
  --show-config         show the current configuration and exit
  -v, --version         show program's version number and exit
```

## Operation

Check out the [sample transcript](sample_transcript.txt) for a look at how it
works.

## Development

In general, on a macOS or linux system: 
1. Clone the repository
2. `cd` to the working directory
3. Create a venv
4. Install it in "editable" mode with `pip install -e .`

For example:
```
git clone https://git.b-wells.us/jmbwell/rsbbs.git
cd rsbbs
python3 -m virtualenv .venv
source .venv/bin/activate
pip install -e .
rsbbs -h
```

## Contributing

Pull requests welcome. If you're not sure where to start:

1. Fork it (<https://git.b-wells.us/jmbwell/rsbbs>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new pull request

## License

GPLv3. 