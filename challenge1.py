#!/usr/bin/env python

from twisted.web.server import Site, Session
from twisted.web.resource import Resource
from twisted.internet import reactor
import random
import base64
import json


class ShortSession(Session):
    sessionTimeout = 2


class Challenge1(Resource):
    sessions = set()

    encoded = ''
    decoded = ''
    session = None

    def get_answer(self, challenge):
        answers = open('answers.json')
        data = json.load(answers)
        answers.close()
        return str(data[challenge])

    def make_string(self):
        decoded = ''
        alpha = 'abcdefghijklmnopqrstuvwxyz'
        for x in range(32):
            decoded += random.choice(alpha)
        encoded = base64.b64encode(decoded)
        return encoded, decoded

    def render_GET(self, request):
        if 'answer' in str(request):
            return 'Maybe you should try POST ;-)'
        self.encoded, self.decoded = self.make_string()
        self.session = request.getSession()
        if self.session.uid not in self.sessions:
            self.sessions.add(self.session.uid)
            self.session.notifyOnExpire(lambda: self._expired(self.session.uid))
        return 'I am Jack\'s base64 encoded string: "' + self.encoded + '"'

    def render_POST(self, request):
        if self.session.uid not in self.sessions:
            self.sessions.add(self.session.uid)
            self.session.notifyOnExpire(lambda: self._expired(self.session.uid))
            return 'Too slow...'

        response = json.loads(request.content.getvalue())['answer']

        if response == self.decoded:
            return self.get_answer('challenge1')
        else:
            return 'If at first you don\'t succeed... try, try again.'

    def _expired(self, uid):
        try:
            self.sessions.remove(uid)
        except KeyError:
            pass


rootResource = Resource()
rootResource.putChild("challenge1", Challenge1())
factory = Site(rootResource)
factory.sessionFactory = ShortSession

reactor.listenTCP(8080, factory)
reactor.run()
