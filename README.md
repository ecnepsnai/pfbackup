# pfbackup

A python script to download config backups from running pfSense instance.

## Requirements

- Python 3
- Requests

A Docker container is available with these requirements already installed.

# Usage

```
Usage: python3 download.py <options>

Note: All options can also be passed as environment variables with PFSENSE_<ARG NAME IN CAPS>

Required options:
 --host <value>                  IP Address or hostname of the PFSense device
 --username <value>              Username for the PFSense device
 --password <value>              Password for the user.

Optional options:
 --allow-untrusted-certificates  Disable TLS verification
 --encrypt-password <value>      Encrypt backups using this password
 --out-file <value>              Specify the path of the output file. Defaults to <host>_<date>.xml
```

# Docker

```
docker run \
 -v $(pwd):/backup \
 -e PFSENSE_HOST=192.168.1.1 \
 -e PFSENSE_USERNAME=admin \
 -e PFSENSE_PASSWORD=pfsense \
 --rm \
 pfbackup:latest
```