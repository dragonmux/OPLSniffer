#!/usr/bin/env python3

from sys import argv, path, exit
from pathlib import Path

gatewarePath = Path(argv[0]).resolve()
if (gatewarePath.parent / 'sniffer').is_dir():
		path.insert(0, str(gatewarePath.parent))

from sniffer import main as oplSniffer
if __name__ == '__main__':
	exit(oplSniffer.cli())
