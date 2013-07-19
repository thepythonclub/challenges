#!/usr/bin/env python

from time import sleep
import requests
import base64
import json

main = 'http://thepythonclub.org:8080/'


def challenge1():
    url = main + 'challenge1'

    r = requests.get(url)
    print r.text
    word = r.text.split('"')[1]
    answer = base64.b64decode(word)
    print answer
    payload = {'answer': answer}
    s = requests.post(url, data=json.dumps(payload))

    print s.url
    print s.text

if __name__ == "__main__":
    challenge1()
