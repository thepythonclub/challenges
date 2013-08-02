#!/usr/bin/env python

from twisted.web.server import Site, Session
from twisted.web.resource import Resource
from twisted.internet import reactor
import random
import json


class LongSession (Session):
    sessionTimeout = 10


class Challenge4(Resource):
    sessions = set()

    solution = ''
    session = None

    def get_answer(self, challenge):
	# must drop answer in JSON file 
        answers = open('answers.json')
        data = json.load(answers)
        answers.close()
        return str(data[challenge])

    def generate_logic_equation(self):
        # returns a tuple with the logic equation as string and solution as int (0 or 1)

        logic_types = ['XOR', 'OR', 'NAND', 'AND']
        equation = []
        random.seed()

        num_operations = random.randint(3, 7)

        solution = 0

        for i in range(num_operations):
                if (i == 0):
                        # generate a new left operand
                        left = random.randint(0, 1)
                        equation.append(str(left))
                else:
                        left = solution

                # generate a new right operand
                right = random.randint(0, 1)

                # choose a logic operator, skip if last
                if (i < num_operations):
                        new_gate = random.choice (logic_types)
                else:
                        new_gate = ""

                # keep track of solution
                gate = logic_types.index(new_gate)
                if (gate == 0):
                        solution = left ^ right
                elif (gate == 1):
                        solution = left | right
                elif (gate == 2):
                        solution = int (not (left & right))
                elif (gate == 3):
                        solution = left & right

                equation.append(new_gate)
                equation.append(str(right))

        equation = " ".join(equation)
        #print "DBG: solution = " + str(solution) + " for " + equation

        return equation, solution

    def render_GET(self, request):
        # setup session
        self.session = request.getSession()
        if self.session.uid not in self.sessions:
            self.sessions.add(self.session.uid)
            self.session.notifyOnExpire(lambda: self._expired(self.session.uid))

	# generate equations
        msg = ""
        result = 0
        for i in range (7):
                eq, sol = self.generate_logic_equation ()
		# update accumulator with binary result
		result += (2 ** i ) * sol

        #	print "DBG: result = " + str(result)
                msg += eq + "\n"

	# handle corner cases, resulting byte should be within printable ascii range
	if (result < 32):
		result += 32
	elif (result > 126):
		result -= 1

	# cast global solution as string
	self.solution = str(chr(result))
        #print "DBG: end solution as binary = " + str(bin(result))
        #print "DBG: end solution as asciichar = " + str(chr(result))
        return msg

    def render_POST(self, request):

        # check for session expiry
        if self.session.uid not in self.sessions:
            self.sessions.add(self.session.uid)
            self.session.notifyOnExpire(lambda: self._expired(self.session.uid))
            return 'Session timed out'

        try:
            answer = json.loads(request.content.getvalue())['answer']
        except ValueError:
            return 'You should be submitting as JSON'

        print "DBG Submission: |" + answer + "|" 
        print "DBG Answer was: |" + self.solution + "|" 

        # check submitted answer
        if answer == self.solution:
	    print "DBG: challenge solved"
            return self.get_answer('challenge4')
        else:
            return 'wrong answer\n'

    def _expired(self, uid):
        try:
            self.sessions.remove(uid)
        except:
            pass

# if __name__ == __main__
print "LOG: starting bit twiddling slash logic gate challenge"
rootResource = Resource()
rootResource.putChild("challenge4", Challenge4())
factory = Site(rootResource)
factory.sessionFactory = LongSession

reactor.listenTCP(8084, factory)
reactor.run()
