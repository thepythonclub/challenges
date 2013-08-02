#!/usr/bin/env python

from twisted.web.server import Site, Session
from twisted.web.resource import Resource
from twisted.internet import reactor
import random
import base64
import json
import tempfile
import os


class ShortSession(Session):
    sessionTimeout = 5


class Challenge3(Resource):
    sessions = set()

    solution = ''
    question = ''
    userfilename = ''
    passfilename = ''
    session = None
    # Change this to a web accessible directory
    directory = '/var/www/tmp'

    noun = ['cat', 'dog', 'bird', 'fish', 'tree',
            'boat', 'pirate', 'ninja', 'beard', 'book']

    adje = ['big', 'little', 'tall', 'short', 'blue',
            'red', 'fast', 'slow', 'great', 'weak']

    street = ['Cherry', 'Plesant', 'Maple', 'Grove', 'Oak',
              'Main', 'Lake', 'Bakers', 'Merchant', 'Sunset']

    s_type = ['Street', 'Lane', 'Blvd', 'Circle', 'Road']

    names = open('names.txt').read().splitlines()

    def get_answer(self, challenge):
        answers = open('answers.json')
        data = json.load(answers)
        answers.close()
        return str(data[challenge])

    def make_userlist(self):
        userlist = tempfile.NamedTemporaryFile(prefix='user', suffix='.json', dir=self.directory, delete=False)
        passleak = tempfile.NamedTemporaryFile(prefix='pass', suffix='.json', dir=self.directory, delete=False)
        os.chmod(userlist.name, 350)
        os.chmod(passleak.name, 350)
        random.shuffle(self.names)
        users = {}
        passes = {}

        for x in range(30):
            password = random.choice(self.adje).upper() + \
                random.choice(self.noun) + str(random.randint(1, 9))
            address = str(random.randint(1, 30)) + ' ' + \
                random.choice(self.street) + ' ' + random.choice(self.s_type)

            uid = random.randint(10000, 40000)
            users[uid] = {'Name': self.names[x],
                          'Address': address}

            passes[uid] = base64.b64encode(password)

        # This will be the solution
        user = random.choice(users.keys())

        self.question = users[user]['Name']
        self.solution = base64.b64decode(passes[user])

        userlist.write(json.dumps(users, separators=(',', ': '), sort_keys=True))
        passleak.write(json.dumps(passes, separators=(',', ': '), sort_keys=True))

        self.userfilename = userlist.name
        self.passfilename = passleak.name

        userlink = userlist.name.split('/')[-1]
        passlink = passleak.name.split('/')[-1]

        passleak.close()
        userlist.close()

        return self.question, self.solution, userlink, passlink

    jokes = [
        'What is Tom Hanks\' wireless password? 1forrest1',
        'Horse: That\'s a battery staple. Cueball: Correct!',
        'Sorry, but your password must contain an uppercase letter,' +
            ' a number, a punctuation mark, a gang sign,' +
            ' an extinct mammal and a hieroglyph.',
        'The four most-used passwords are: love, sex, secret, and...',
        'Dark Helmet: It worked, sir. We have the combination.\n' +
            'President Skroob: Great. Now we can take every last breath' +
            ' of fresh air from Planet Druidia. What\'s the combination?\n' +
            'Colonel Sandurz: 1-2-3-4-5'
    ]

    def render_GET(self, request):
        if 'answer' in str(request):
            return 'You should have learned how to submit answers by now...'
        self.question, self.solution, userlink, passlink = self.make_userlist()
        self.session = request.getSession()
        if self.session.uid not in self.sessions:
            self.sessions.add(self.session.uid)
            self.session.notifyOnExpire(lambda: self._expired(self.session.uid))

        url = 'http://thepythonclub.org/tmp/'
        html = 'I am Jack\'s desired password for: "' + self.question + '"<p><p>' + \
            'Userlist: <a href="{}{}">User IDs</a><p>'.format(url, userlink) + '<p><p>' + \
            'Password list: <a href="{}{}">Password Leak</a><p>'.format(url, passlink)

        return html

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
            return self.get_answer('challenge3')
        else:
            return 'Try again, Here is a joke for your troubles:\n' + \
                self.jokes[random.randint(0, 4)]

    def _expired(self, uid):
        try:
            self.sessions.remove(uid)
            try:
                os.remove(self.userfilename)
                os.remove(self.passfilename)
            except OSError:
                pass

        except KeyError:
            pass


rootResource = Resource()
rootResource.putChild("challenge3", Challenge3())
factory = Site(rootResource)
factory.sessionFactory = ShortSession

reactor.listenTCP(8083, factory)
reactor.run()
