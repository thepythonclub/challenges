#!/usr/bin/env python

from twisted.web.server import Site, Session
from twisted.web.resource import Resource
from twisted.internet import reactor
import random
import json


class ShortSession(Session):
    sessionTimeout = 4


class Challenge5(Resource):
    sessions = set()

    sentence = ''
    solution = ''
    session = None

    def get_answer(self, challenge):
        answers = open('answers.json')
        data = json.load(answers)
        answers.close()
        return str(data[challenge])

    def pick_language(self):
        sentence = ''
        f = open('verses.json','r')
        text = json.loads(f.read())
        f.close()

        language = random.choice(text.keys())
        sentence = text[language]

        print language, sentence

        return sentence, language

    def render_GET(self, request):
        if 'answer' in str(request):
            return 'Maybe you should try POST ;-)'
        self.sentence, self.solution = self.pick_language()
        self.session = request.getSession()
        if self.session.uid not in self.sessions:
            self.sessions.add(self.session.uid)
            self.session.notifyOnExpire(lambda: self._expired(self.session.uid))

        data = (self.sentence).encode('UTF-8')
        string = '<html><meta http-equiv="Content-Type" content="text/html;charset=UTF-8">' + \
                'I am Jack\'s random language: "' + data + '"</html>'
        return string

    def render_POST(self, request):
        if self.session.uid not in self.sessions:
            self.sessions.add(self.session.uid)
            self.session.notifyOnExpire(lambda: self._expired(self.session.uid))
            return 'Too slow...'

        try:
            answer = json.loads(request.content.getvalue())['answer']
        except ValueError:
            return 'You should be submitting as JSON'
        if answer == self.solution:
            return self.get_answer('challenge5')
        else:
            return 'If at first you don\'t succeed... try, try again.'

    def _expired(self, uid):
        try:
            self.sessions.remove(uid)
        except KeyError:
            pass


rootResource = Resource()
rootResource.putChild("challenge5", Challenge5())
factory = Site(rootResource)
factory.sessionFactory = ShortSession

reactor.listenTCP(8085, factory)
reactor.run()
