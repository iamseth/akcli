# akcli
An Akamai command line client written in Python. So far only the DNS config API is supported since it's the only scratch I need itching. PRs welcome.

# What can it do?

Currently, the following items are supported for DNS services at Akami.
  - add_record
  - fetch_record
  - fetch_zone
  - list_records
  - remove_record

The --json flag will format output as JSON to be consumed by other tools such as [jq](https://stedolan.github.io/jq/).

# Usage
```bash
Usage: akcli [OPTIONS] COMMAND [ARGS]...

Options:
  -v, --verbose      Enables verbose mode.
  --debug            Enables debug mode.
  --json             Output as JSON.
  --config FILENAME
  --version          Show the version and exit.
  --help             Show this message and exit.

Commands:
  dns
```
