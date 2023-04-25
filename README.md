# Really Simple BBS

A message board for packet radio, suitable for use with ax25d. 

Really Simple BBS (`rsbbs`) implements a bulletin board system that enables
radio amateurs to read and store messages at your station. It is similar to the
PBBS function of popular Kantronics TNCs, and it uses similar commands (`B`,
`J`, `K`, `L`, `R`, `S`, `H`, etc.).

It is designed to run on a linux system when called by `ax25d`. That is, when a
user calls your station, `ax25d` answers the call and routes the connection to
`rsbbs` via standard input (`stdin`). `rsbbs` responds to the user through
`ax25d` via standard output (`stdout`).

## Requirements

In general, you need a linux system with ax25d configured and working. This is
a python 3 application, so you will need python 3 also.

## Installation

Until I publish this thing to PyPI, you can clone it and build it yourself:

1. Clone the repo to a reasonable location.
2. `cd` to the repo directory
3. Run `python3 -m pip build .`
4. Run `python3 -m pip install .`
5. Run `rsbbs -h` to test installation and create config and data files.

## Configuration

By default, the `config.yaml` file lives in your system's user config
directory, such as `~/.config/rsbbs/config.yaml`. 

To use a `config.yaml` file from a different location, use the `-f` option:
```
rsbbs -f ~/config.yaml -s KI5QKX
```

If this file is missing, `rsbbs` will create it.

The `config.yaml` file is pretty simple and self-explanatory for now.

## Usage

### With ax25d

Assuming you have `ax25d` working on your system, add something like the
following to your `ax25d.conf` file:

```
[KI5QKX-10 via vhf0]
default   * * * * * *  *    root    /usr/local/bin/rsbbs rsbbs -s %U
```

Notes:
- The installation path may vary on your system. 
- Be sure to specify the `-s %U` parameters; this passes the ax.25 caller's
  callsign to the `rsbbs` application.

See the ax25d man page for more details.

### Directly

You can also run it directly, for administration purposes or just to talk to
yourself. It will not accept calls when run without ax25d.

```
rsbbs -s URCALL
```

### Options

Run `sbbs -h` to see the following help:

```
usage: rsbbs [-h] [-d] -s CALLING_STATION [-f CONFIG_FILE] [-v]

options:
  -h, --help            show this help message and exit
  -d, --debug           Enable debugging output to stdout
  -s CALLING_STATION, --calling-station CALLING_STATION
                        The callsign of the calling station
  -f CONFIG_FILE, --config-file CONFIG_FILE
                        specify path to config.yaml file
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

## Contributing

1. Fork it (<https://git.b-wells.us/jmbwell/rsbbs>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new pull request

## License

GPLv3. 