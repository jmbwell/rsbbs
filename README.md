# Really Simple BBS

Really Simple BBS (rsbbs) implements a message board for packet radio, suitable for use with ax25d. It roughly adopts the command conventions established by popular packet radio BBSes, (`B`, `J`, `K`, `L`, `R`, `S`, `H`, etc.).

## Installation

1. Clone the repo to a reasonable location.
2. Run `pip install -r requirements.txt`
2. Copy config.yaml.sample to config.yaml and update it.

## Usage

### With ax25d

Assuming you have `ax25d` working on your system, add something like the following to your `ax25d.conf` file, pointing to the rsbbs binary:

```
[KI5QKX-10 via vhf0]
default   * * * * * *  *    root    /usr/local/bin/rsbbs rsbbs -s %S
```

### Directly

You can also run it directly:
```
cd /path/to/rsbbs
python3 rsbbs.py -s URCALL
```

### Options

```
usage: rsbbs.py [-h] [-d] -s CALLING_STATION [-f CONFIG_FILE] [-v]

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

Checkout the [sample transcript](sample_transcript.txt) for a look at how it works.

## License

GPLv3. 