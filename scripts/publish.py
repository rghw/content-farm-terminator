#!/usr/bin/env python3
"""Prepare and publish data

- Distribute blocklists into other filter formats.
"""
import sys
import os
import json
import re
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
        """Convert to ABP (uBO) rule

        https://help.eyeo.com/en/adblockplus/how-to-write-filters
        https://github.com/gorhill/uBlock/wiki/Static-filter-syntax
        """
        def extract_key_part_from_regex(regex):
            m = REGEX_KEY_PART.search(regex)
            if m:                
                return m.group(1)
            else:
                print(f"Warn: unable to parse {regex}", file=sys.stderr)
                return None

        REGEX_KEY_PART = re.compile(r"[?/](\w+)/?\(\?=")

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

                # special handling for several well known sites for better performance
                if r"\.xuite\." in url:
                    id = extract_key_part_from_regex(url)
                    if id:
                        print(f"{id}$document,domain=xuite.net")
                        continue

                if r"\.udn\." in url:
                    id = extract_key_part_from_regex(url)
                    if id:
                        print(f"{id}$document,domain=blog.udn.com|album.udn.com")
                        continue

                if r"?pchome\." in url:
                    id = extract_key_part_from_regex(url)
                    if id:
                        print(f"{id}$document,domain=pchome.com.tw")
                        continue

                # for unsupported sites or non-standardized formats, use original regex
                print(f"{url}$document")

            else:
                # General rule
                if "*" in url:
                    print(f"{url}$document")
                else:
                    print(f"||{url}")

def main():
    with open(os.path.join(os.path.dirname(__file__), CONFIG_FILE), "r") as f:
        tasks = json.load(f)

    converter = Converter()
    for task in tasks:
        Converter.run(task)

if __name__ == '__main__':
    main()
