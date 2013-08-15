#!/usr/bin/env python
# Sean pySight
# Aug. 2013

#to install: keep this file as the same dir as the book text file
#case insensitive, this is a copy of the first hackthissite.org programming

from twisted.web.server import Site, Session
from twisted.web.resource import Resource
from twisted.internet import reactor
import random
from random import shuffle
import json
import tempfile
import os


class ShortSession(Session):
    sessionTimeout = 10


class Challenge6(Resource):
    sessions = set()

    solution = 0
    challengeWord = ''

    session = None
    wordList = {}
    wordListFile = 'wordlist.txt'
    scrambledWordsCount = 10


    def get_answer(self, challenge):
        answers = open('answers.json')
        data = json.load(answers)
        answers.close()
        return str(data[challenge])

        
    def make_challenge(self):
        if len(self.wordList) is 0:
            fp = open(self.wordListFile,'r')
            self.wordList = fp.readlines()
            fp.close()
            
        #generate scrambled word list
        random.seed()
        self.words = []
        for i in range(1,self.scrambledWordsCount +1):
            randomNumber  = random.randint(0, len(self.wordList) -1)
            self.words.append(self.wordList[randomNumber].strip())
        
        #scramble each of those words
        self.scrambledWords = []
        for word in self.words:
            charList = list(word)
            shuffle(charList)
            word = ''.join(charList)
            self.scrambledWords.append(word)
        
        return (self.words , self.scrambledWords)
    
    def buildList(self):
        # I know there's a better way to do this
        sumString = "<ul>"
        for word in self.scrambledWords:
            sumString += '<li>"'+ word +'"</li>'
        sumString += "</ul>"
        return sumString
    
    
    def render_GET(self, request):
        if 'answer' in str(request):
            return 'You should have learned how to submit answers by now...'
        (self.words , self.scrambledWords) = self.make_challenge()
        
        self.session = request.getSession()
        if self.session.uid not in self.sessions:
            self.sessions.add(self.session.uid)
            self.session.notifyOnExpire(lambda: self._expired(self.session.uid))
        
        return 'Download <a href=\'wordlist.txt\'>this wordlist</a>. Unscramble these words (Hint: bruteforce is not the answer)<!-- Better phrasing might be: make any possible word found on the word list --><br />' + self.buildList()

    def render_POST(self, request):
        if self.session.uid not in self.sessions:
            self.sessions.add(self.session.uid)
            self.session.notifyOnExpire(lambda: self._expired(self.session.uid))
            return 'Too slow...'
        remember = " Remember: You should be submitting as JSON in the form of: {'scramnulbed':'unscrambled','doog':'good',...}"
        try:
            answer = json.loads(request.content.getvalue())
        except ValueError:
            return remember
        #print("Recieved: " + str(answer))
        if len(answer) is not self.scrambledWordsCount:
            return "That's not even the correct number of words. " + remember
        elif len(answer) is self.scrambledWordsCount:
            answers = answer.values()
            for word in self.words:
                if word not in answers:
                    return word + " was not found among the words you returned. Please Try again"
            return self.get_answer('challenge6')
        else:
            return 'Try again'
            
    def _expired(self, uid):
        try:
            self.sessions.remove(uid)
        except KeyError:
            pass

class GetWordlist(Resource):
    wordListFile = 'wordlist.txt'
    
    def render_POST(self, request):
        return "You shouldn't be posting here"
    
    def render_GET(self, request):
        orginalFile = open(self.wordListFile,'r')
        data = orginalFile.read()
        orginalFile.close()
        return data
        
    

rootResource = Resource()
rootResource.putChild("challenge6", Challenge6())
rootResource.putChild("wordlist.txt", GetWordlist())
factory = Site(rootResource)
factory.sessionFactory = ShortSession

reactor.listenTCP(8086, factory)
reactor.run()
