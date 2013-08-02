#!/usr/bin/env python

from twisted.web.server import Site, Session
from twisted.web.resource import Resource
from twisted.internet import reactor
import random
import base64 
import json 

class LongSession (Session):
    sessionTimeout = 10


class Challenge1(Resource):
    sessions = set()

    encoded = ''
    solution = ''
    session = None

    def get_answer(self, challenge):
        answers = open('answers.json')
        data = json.load(answers)
        answers.close()
        return str(data[challenge])

    def generate_logic_equation(self):
	# returns a tuple with the logic equation as string and solution as int (0 or 1)

	logic_types = ['XOR', 'OR', 'NAND', 'AND']
	equation = []
	random.seed()
	
	num_operations = random.randint(3,7)

	# init var
	solution = 0

	for i in range(num_operations ) :
		if (i == 0):
			# generate a new left operand
			left = random.randint(0,1)
			equation.append(str(left))
		else:
			left = solution

		# generate a new right operand
		right = random.randint(0,1)

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

		equation.append( new_gate) 
		equation.append( str(right))

	# finally done
	equation = " ".join(equation)
	print "DBG: solution = " + str(solution) + " for " + equation 

        return equation, solution

    def render_GET(self, request):
	# setup session
        self.session = request.getSession() 
        if self.session.uid not in self.sessions:
            self.sessions.add(self.session.uid)
            self.session.notifyOnExpire(lambda: self._expired(self.session.uid))

# TODO store solution as binary string
	# add 2^i to current value in for loop and convert to binary?
	# bin( ord (char) ) ?
# loop 7 times to print equations
# TODO convert solution as ASCII byte, make sure it's printable by adding a constant if less than printable range

	msg = ""
	solution = ""
	for i in range (7):
		eq, sol = self.generate_logic_equation ()
		msg += eq + "\n"
		solution += str(sol)

	# TODO drop the solution into answers JSON table to check
	print "DBG: solution = " + solution

	# display challenge to user
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

        print "DBG Submission: |" + answer + "|" , self.transport.getPeer()
	
	# check submitted answer
        if answer == self.solution:
            return self.get_answer('challenge4')
        else:
            return 'nope'

    def _expired(self, uid):
        try:
            self.sessions.remove(uid)
	except:
	    print "session ended"

# if __name__ == __main__
print "LOG: starting challenge"
rootResource = Resource()
rootResource.putChild("challenge4", Challenge1())
factory = Site(rootResource)
factory.sessionFactory = LongSession

reactor.listenTCP(8084, factory)
reactor.run()
