#!/usr/bin/env python

from twisted.web.server import Site, Session
from twisted.web.resource import Resource
from twisted.internet import reactor
import random
import json


class ShortSession(Session):
    sessionTimeout = 2


class Challenge2(Resource):
    sessions = set()

    solution = ''
    equation = ''
    session = None

    num = {
        1: 'one',       16: 'sixteen',
        2: 'two',       17: 'seventeen',
        3: 'three',     18: 'eighteen',
        4: 'four',      19: 'nineteen',
        5: 'five',      20: 'twenty',
        6: 'six',       21: 'twenty-one',
        7: 'seven',     22: 'twenty-two',
        8: 'eight',     23: 'twenty-three',
        9: 'nine',      24: 'twenty-four',
        10: 'ten',      25: 'twenty-five',
        11: 'eleven',   26: 'twenty-six',
        12: 'twelve',   27: 'twenty-seven',
        13: 'thirteen', 28: 'twenty-eight',
        14: 'fourteen', 29: 'twenty-nine',
        15: 'fifteen',  30: 'thirty',
        0: 'zero'
    }

    sym = {
        -1: 'minus', 1: 'plus'
    }

    jokes = [
        'What do mathematicians eat on Halloween? Pumpkin Pi.',
        'Why did the math book look so sad? Because it had so many problems.',
        'A circle is just a round straight line with a hole in the middle.',
        'Decimals have a point.',
        'Why do plants hate math? Because it gives them square roots.',
        'Why did the boy eat his math homework? Because the teacher told him it was a piece of cake.',
        'Have you heard the latest statistics joke? Probably.',
        'What did the acorn say when it grew up? Geometry.',
        'What do you call an empty parrot cage? Polygon.',
        'Cakes are round but Pi are square.',
        'How can you make time fly? Throw a clock out the window!',
        'Without geometry, life is pointless.'
    ]

    def get_answer(self, challenge):
        answers = open('answers.json')
        data = json.load(answers)
        answers.close()
        return str(data[challenge])

    def get_symbol(self):
        x = random.getrandbits(1)
        if x == 0:
            return -1
        else:
            return 1

    def get_equation(self):
        x, y, z = 1, 1, 1
        a1, a2 = -1, -1
        while (x + a1 * y + a2 * z) < 0:
            x = random.randint(1, 10)
            y = random.randint(1, 10)
            z = random.randint(1, 10)

            a1 = self.get_symbol()
            a2 = self.get_symbol()

        return x, y, z, a1, a2

    def make_equation(self):
        x, y, z, a1, a2 = self.get_equation()

        solution = self.num[(x + a1 * y + a2 * z)]
        equation = self.num[x] + ' ' + self.sym[a1] + ' ' + self.num[y] + ' ' + \
            self.sym[a2] + ' ' + self.num[z] + ' equals ?'
        return equation, solution

    def render_GET(self, request):
        if 'answer' in str(request):
            return 'You should have learned how to submit answers by now...'
        self.equation, self.solution = self.make_equation()
        self.session = request.getSession()
        if self.session.uid not in self.sessions:
            self.sessions.add(self.session.uid)
            self.session.notifyOnExpire(lambda: self._expired(self.session.uid))
        return 'I am Jack\'s unsolved equation: "' + self.equation + '"'

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
            return self.get_answer('challenge2')
        else:
            return 'Try again, Here is a joke for your troubles:\n' + self.jokes[random.randint(0, 11)]

    def _expired(self, uid):
        try:
            self.sessions.remove(uid)
        except KeyError:
            pass


rootResource = Resource()
rootResource.putChild("challenge2", Challenge2())
factory = Site(rootResource)
factory.sessionFactory = ShortSession

reactor.listenTCP(8082, factory)
reactor.run()
