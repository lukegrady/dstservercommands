#!/usr/bin/python3

import requests
import re
import sys

def main():
    url = 'http://dontstarve.wikia.com/wiki/Console/Prefab_List'
    outfile = 'prefabs.txt'

    r = requests.get(url)
    raw_text = r.text
    matches = re.findall(r'</td><td>(\w+)\n',raw_text)

    with open(outfile, 'w') as f:
        f.write('\n'.join(matches))

    print('file written successfully')

if __name__ == '__main__':
    main()


