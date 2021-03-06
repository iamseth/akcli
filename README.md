# akcli
An Akamai command line client written in Python. So far only the DNS config API is supported since it's the only scratch I need itching. PRs welcome.

# What can it do?

Currently, the following items are supported for DNS services at Akami.
  - add_record
  - fetch_records
  - fetch_zone
  - list_records
  - remove_record

The --json flag will format output as JSON to be consumed by other tools such as [jq](https://stedolan.github.io/jq/).

# Installation

## PyPi
```bash
pip install akcli
```

## Manually

```bash
git clone https://github.com/iamseth/akcli.git
cd akcli
python setup.py build
sudo python setup.py install
```

# Configuration

By default, akcli looks for a config file at ~/.akamai.cfg. The file should look something like this.

```ini
[auth]
baseurl = https://abcd-yaddayadda.luna.akamaiapis.net/
client_token = abcd-yaddayadda
client_secret = randomstuffhere
access_token = abcd-randomstuffhere
```

# Usage
```bash
Usage: akcli [OPTIONS] COMMAND [ARGS]...

  An Akamai command line client.

  See https://github.com/iamseth/akcli for more information.

Options:
  --debug            Enables debug mode.
  --json             Output as JSON.
  --config FILENAME
  --version          Show the version and exit.
  --help             Show this message and exit.

Commands:
  dns
```
