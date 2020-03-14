#!/usr/bin/env python3
"""Prepare and publish data

- Distribute blocklists into other filter formats.
"""
import sys
import os
import json
from datetime import datetime

CONFIG_FILE = "publish.config.json"

root = os.path.normpath(os.path.join(__file__, "..", ".."))

class Converter():
    def run(task):
        src_file = os.path.normpath(os.path.join(root, task['source']))
        dst_file = os.path.normpath(os.path.join(root, task['publish']))

        ih = open(src_file, 'r', encoding='UTF-8')
        oh = open(dst_file, 'w', encoding='UTF-8', newline='\n')

        # redirect sys.stdout to oh so that we can print to it
        # comment out this line to print to stdout instead
        sys.stdout = oh

        getattr(Converter, task['convert']['type'])(ih, task['convert'])
        ih.close()
        oh.close()

    def cft_abp(ih, info):
        lm = str(datetime.now().isoformat(timespec='seconds'))
        print(f"! Last modified: {lm}")

        for field in ('Title', 'Expires', 'Description', 'Homepage', 'Licence'):
            if info['data'].get(field):
                print(f"! {field}: {info['data'][field]}")

        while True:
            line = ih.readline()

            if not line:
                break

            if line.endswith("\n"):
                line = line[:-1]

            parts = line.split(" ", 1)
            url = parts[0]

            if not url:
                continue

            if url.startswith("/") and url.endswith("/"):
                # RegExp rule
                print(f"{url}$document")
            else:
                # General rule
                print(f"{url}$document")

def main():
    with open(os.path.join(os.path.dirname(__file__), CONFIG_FILE), "r") as f:
        tasks = json.load(f)

    converter = Converter()
    for task in tasks:
        Converter.run(task)

if __name__ == '__main__':
    main()
