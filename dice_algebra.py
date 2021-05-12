import random
import copy
import re

from rply import LexerGenerator
from rply import ParserGenerator
from rply.token import BaseBox

DICE_NUM_LIMIT = 1000
EXPLODE_CAP = 100
lg = LexerGenerator()

EXPLODE_TOKEN = r"\!"
REROLL_TOKEN = r"r"
SUCCESS_TOKEN = r"\>"
FAILURE_TOKEN = r"\<"

lg.add('NUMBER', r'\d+')
lg.add('PLUS', r'\+')
lg.add('MINUS', r'-')
lg.add('MUL', r'\*')
lg.add('DIV', r'/')
lg.add('POW', r'\^')
lg.add('OPEN_PARENS', r'\(')
lg.add('CLOSE_PARENS', r'\)')
lg.add('ROLL', r'd')
lg.add('KEEP', r'k')
lg.add('LOW', r'l')
lg.add('HIGH', r'h')
lg.add('EXPLODE', EXPLODE_TOKEN)
lg.add('REROLL', REROLL_TOKEN)
lg.add('SUCCESS', SUCCESS_TOKEN)
lg.add('FAILURE', FAILURE_TOKEN)

pg = ParserGenerator(
    # A list of all token names, accepted by the parser.
    ['NUMBER', 'ROLL', 'LOW', 'HIGH', 'KEEP', 'EXPLODE', 'FAILURE', 'SUCCESS', 'REROLL',
     'OPEN_PARENS', 'CLOSE_PARENS',
     'PLUS', 'MINUS', 'MUL', 'DIV','POW'
    ],
    # A list of precedence rules with ascending precedence, to
    # disambiguate ambiguous production rules.
    precedence=[
        ('left', ['BOOLEAN', 'OPTION']),
        ('left', ['NEGATE']),
        ('left', ['AND','OR']),
        ('left', ['GREATER','LESSER','EQUAL']),
        ('left', ['PLUS', 'MINUS']),
        ('left', ['MUL', 'DIV']),
        ('left', ['POW']),
    	('left', ['NUMBER']),
        ('left', ['SUCCESS','FAILURE']),
        ('left', ['KEEP','LOW','HIGH','REROLL','EXPLODE']),
        ('left', ['ROLL']),
        ('left', ['OPEN_PARENS', 'CLOSE_PARENS']),
    ]
)

cross_out = lambda x : '~~{}~~'.format(x)
bold = lambda x : '**{}**'.format(x)

class DiceError(Exception):
    pass

class OutOfDiceBounds(Exception):
    pass

class BadArgument(Exception):
    pass

class Number(BaseBox):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "{}".format(self.value)

    def eval(self):
        return self.value

arithmetic={
        'PLUS':lambda x,y: x+y,
        'MINUS':lambda x,y: x-y,
        'MUL':lambda x,y: x*y,
        'DIV':lambda x,y: x//y,
        'POW':lambda x,y: x**y
        }
arithmetic_symbols={
        'PLUS':'+',
        'MINUS':'-',
        'MUL':'*',
        'DIV':'/',
        'POW':'^'
        }
class MathOp(BaseBox):
    def __init__(self, left, command, right):
        self.left = left
        self.symbol=arithmetic_symbols[command]
        self.right = right
        self.solution = arithmetic[command](self.left.eval(),self.right.eval())

    def __repr__(self):
        return "{} {} {}".format(self.left, self.symbol, self.right)

    def eval(self):
        return self.solution

class DiceOp(BaseBox):
    def __init__(self, left, right):
        self.left = copy.deepcopy(left)
        self.right = copy.deepcopy(right)
        self.number_of_dice = left.eval()
        if self.number_of_dice > DICE_NUM_LIMIT:
            raise OutOfDiceBounds("Too many dice! No more than %d!" % DICE_NUM_LIMIT)
        self.size_of_dice = right.eval()
        if self.size_of_dice <= 0:
            raise BadArgument("Can't roll a 0 or negative-sided dice!")
        self.results = [random.randint(1,self.size_of_dice) for i in range(self.number_of_dice)]
        initial_roll = "{}d{}".format(self.left, self.right)
        initial_mod = ", ".join(map(str,self.results))
        self.modifications = [[initial_roll, initial_mod]]

    def __repr__(self):
        repr_roll = ""
        final_results = self.modifications[-1]
        if any(SUCCESS_TOKEN in i[0] or FAILURE_TOKEN in i[0] for i in self.modifications):
            repr_results = "{} -> {} hits".format(final_results[1], self.eval())
        else:
            repr_results = "{} -> {}".format(final_results[1], self.eval())
        return "({}{})".format(repr_roll, repr_results)

    def keep(self, limit):
        sorted_roll = sorted(self.results,reverse=True)
        keep = sorted_roll[0:limit]
        toss = sorted_roll[limit:len(sorted_roll)]
        self.results = keep
        repr_result = list(map(str,keep))+list(map(cross_out,toss))
        repr_result = ", ".join(map(str,repr_result))
        self.modifications.append(['k{}'.format(limit),repr_result])

    def low(self, limit):
        sorted_roll = sorted(self.results)
        keep = sorted_roll[0:limit]
        toss = sorted_roll[limit:len(sorted_roll)]
        self.results = keep
        repr_result = list(map(str,keep))+list(map(cross_out,toss))
        repr_result = ", ".join(map(str,repr_result))
        self.modifications.append(['l{}'.format(limit),repr_result])

    def reroll(self, limit):
        repr_result = self.results[:]
        for i in range(0,len(self.results)):
            if self.results[i] <= limit:
                self.results[i] = random.randint(1,self.size_of_dice)
                repr_result[i] = bold(self.results[i])
        repr_result = ", ".join(map(str,repr_result))
        self.modifications.append(['{}{}'.format(REROLL_TOKEN, limit),repr_result])

    def explode(self,limit):
        if limit < 2:
            raise BadArgument("Cannot explode on 1 or higher! (For bot safety)")
        repr_result = self.results[:]
        for i in range(0,len(self.results)):
            if self.results[i] >= limit:
                 new_roll = random.randint(1,self.size_of_dice)
                 repr_result.append(bold(new_roll))
                 self.results.append(new_roll)
                 explosions = 1
                 while new_roll >= limit:
                     #prevent dangerous looping
                     if explosions > EXPLODE_CAP:
                         break
                     explosions += 1
                     new_roll = random.randint(1,self.size_of_dice)
                     self.results.append(new_roll)
                     repr_result.append(bold(new_roll))
        repr_result = ", ".join(map(str,repr_result))
        self.modifications.append(['{}{}'.format(EXPLODE_TOKEN, limit),repr_result])

    def success(self, limit):
        prev_cmd, prev_repr_result = self.modifications[-1]
        repr_result = [i if int(re.search('\d+', i).group()) > limit else cross_out(i) for i in prev_repr_result.split(", ")]
        self.results = [1 for x in self.results if x > limit]
        repr_result = ", ".join(map(str,repr_result))
        self.modifications.append(['{}{}'.format(SUCCESS_TOKEN, limit),repr_result])

    def failure(self, limit):
        keep = [x for x in self.results if x < limit]
        repr_result = [str(i) if i in keep else cross_out(str(i)) for i in self.results]
        self.results = [1] * len(keep)
        repr_result = ", ".join(map(str,repr_result))
        self.modifications.append(['{}{}'.format(FAILURE_TOKEN, limit), repr_result])

    def modify(self,command,limit):
        modifications={
                'KEEP': self.keep,
                'HIGH': self.keep,
                'LOW': self.low,
                'REROLL': self.reroll,
                'EXPLODE': self.explode,
                'SUCCESS': self.success,
                'FAILURE': self.failure,
                }
        modifications[command](limit)

    def eval(self):
        return sum(self.results)

class ParensOp(BaseBox):
    def __init__(self, operation):
        self.operation = operation

    def __repr__(self):
        return "({})".format(self.operation)

    def eval(self):
        return self.operation.eval()

@pg.production('expression : NUMBER')
def expression_number(p):
    return Number(int(p[0].getstr()))


@pg.production('expression : OPEN_PARENS expression CLOSE_PARENS')
def expression_parens(p):
    return ParensOp(p[1])

@pg.production('expression : expression ROLL expression')
def expression_diceop(p):
    left = p[0]
    right = p[2]
    return DiceOp(left,right)

@pg.production('expression : expression KEEP expression')
@pg.production('expression : expression LOW expression')
@pg.production('expression : expression HIGH expression')
@pg.production('expression : expression REROLL expression')
@pg.production('expression : expression EXPLODE expression')
@pg.production('expression : expression SUCCESS expression')
@pg.production('expression : expression FAILURE expression')
def expression_modify_diceop(p):
    left = p[0]
    command = p[1].gettokentype()
    right = int(p[2].eval())
    left.modify(command, right)
    return left

@pg.production('expression : expression PLUS expression')
@pg.production('expression : expression MINUS expression')
@pg.production('expression : expression MUL expression')
@pg.production('expression : expression DIV expression')
@pg.production('expression : expression POW expression')
def expression_mathop(p):
    left = p[0]
    command = p[1].gettokentype()
    right = p[2]
    return MathOp(left,command,right)

@pg.error
def error_handler(token):
    raise DiceError("Incorrect dice algebra")

lexer = lg.build()
parser = pg.build()
