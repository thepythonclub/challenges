#!/usr/bin/env python
# Sean pySight
# Aug. 2013

#to install: keep this file as the same dir as the book text file
#case insensitive, puncuation and white space should be removed from every word

from twisted.web.server import Site, Session
from twisted.web.resource import Resource
from twisted.internet import reactor
import random
import json
import tempfile
import os


class ShortSession(Session):
    sessionTimeout = 5


class Challenge5(Resource):
    sessions = set()

    solution = 0
    challengeWord = ''
    session = None
    wordList = {}

    def get_answer(self, challenge):
        answers = open('answers.json')
        data = json.load(answers)
        answers.close()
        return str(data[challenge])

    def make_challenge(self):
        if len(self.wordList) is 0:
            fp = open('Alice_in_Wonderland.txt','r')
            lines = fp.readlines()
            fp.close()
            
            #generate word list
            for line in lines:
                words = line.strip().lower().split()
                for word in words:
                    word = word.translate(None,'~`?!@#$%^&*()_+-=[]{};\'\",.')
                    if word in self.wordList:
                        self.wordList[word] += 1
                    else:
                        self.wordList[word]  = 1
        
        randomNumber  = random.randint(0, len(self.wordList) -1)
        targetWord = self.wordList.keys()[randomNumber]
        return (self.wordList[targetWord], targetWord)
    
    def render_GET(self, request):
        if 'answer' in str(request):
            return 'You should have learned how to submit answers by now...'
        (self.solution, self.challengeWord) = self.make_challenge()
        #print("Challenge created: Target word = " + self.challengeWord + " solution is " + str(self.solution))
        
        self.session = request.getSession()
        if self.session.uid not in self.sessions:
            self.sessions.add(self.session.uid)
            self.session.notifyOnExpire(lambda: self._expired(self.session.uid))
        return 'Download <a href="book.txt">this book</a>. How many times does the word "' + self.challengeWord + '" appear? <br />(Hint: Be sure to remove all the punctuation and newlines)'

    def render_POST(self, request):
        if self.session.uid not in self.sessions:
            self.sessions.add(self.session.uid)
            self.session.notifyOnExpire(lambda: self._expired(self.session.uid))
            return 'Too slow...'

        try:
            answer = json.loads(request.content.getvalue())['answer']
        except ValueError:
            return 'You should be submitting as JSON'
        #print("Recieved: " + str(answer))
        if answer == self.solution:
            return self.get_answer('challenge6')
        else:
            return 'Try again'
            

    def _expired(self, uid):
        try:
            self.sessions.remove(uid)
        except KeyError:
            pass

class GetBook(Resource):
    def render_POST(self, request):
        return "You shouldn't be posting here"
    
    def render_GET(self, request):
        orginalFile = open('Alice_in_Wonderland.txt','r')
        data = orginalFile.read()
        orginalFile.close()
        return data

rootResource = Resource()
rootResource.putChild("challenge5", Challenge5())
rootResource.putChild("book.txt", GetBook())
factory = Site(rootResource)
factory.sessionFactory = ShortSession

reactor.listenTCP(8085, factory)
reactor.run()
