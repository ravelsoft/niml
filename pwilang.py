import re

from pwpeg import *
from pwpeg.helpers import *

import re

from nodes import *

def indent(init=""):
    return MemoRule(re.compile("{0}[ \t]+".format(init if not isinstance(init, MemoRule) else init.memorized)))

bck = re.compile("\\\\(.)")


lineelt = ForwardRule()

delimited_line = ForwardRule()

delim = ForwardRule()

terminator = ForwardRule()

line = ForwardRule()

block = ForwardRule()


comment = Rule(re.compile('\s*#\s.*', re.M), name='comment')

_space = Rule(re.compile('[ \t]*'), name='_space')

EOL = Rule("\n", name='EOL')

ident = Rule(re.compile('[-$a-zA-Z0-9:]+'), name='ident')

access_or_funcall = Rule((Either(
    Balanced("[", "]"),
    Balanced("(", ")")
), Action(lambda b:b[0] + b[1] + b[2])), name='access_or_funcall')

variable_component = Rule((ident, ZeroOrMore(access_or_funcall), Action(lambda i, a:i + "".join(a))), name='variable_component')

variable = Rule(("$", OneOrMoreSeparated(variable_component, "."), Action(lambda _0, i:"{{{{ {0} }}}}".format(".".join(i)))), name='variable')

@rule()
def delimited_line(delim):
    return (delim, Optional(line(delim)), delim, Action(lambda _0, l, _2:l or ""))

string = Rule(Either(
    delimited_line("\""),
    delimited_line("'")
), name='string')

tag = Rule(Either(
    ("@", ident, Action(lambda _0, i:NodeTag(i))),
    ("@/", ident, Action(lambda _0, i:NodeTag(i).set_selfclosing()))
), name='tag')

id = Rule(('#', ident, Action(lambda _0, i:NodeId(i))), name='id')

cls = Rule((".", ident, Action(lambda _0, i:NodeClass(i))), name='cls')

attrib = Rule((ident, "=", Either(
    string,
    re.compile('[^ \t]+')
), Action(lambda key, _1, value:NodeNamed(key, value))), name='attrib')

attribute = Rule(Either(
    id,
    cls,
    attrib
), name='attribute')

@rule()
def lineelt(terminator):
    return Either(
        (tag, Optional(_space), ZeroOrMore(attribute), Optional(_space), "[", Optional(line("]")), "]", Action(lambda t, _1, a, _3, _4, i, _6:t.set_attributes(a).set_line(i or ""))),
        (tag, Optional(_space), ZeroOrMore(attribute), Optional(_space), Optional(line(terminator)), Action(lambda t, _1, a, _3, i:t.set_attributes(a).set_line(i))),
        ('\\', terminator, Action(lambda _0, t:t)),
        variable,
        (Not(terminator), re.compile('[^@\$\n]+'), Action(lambda c:c))
    )

@rule(skip=_space)
def __line(terminator=EOL):
    return (OneOrMore(lineelt(terminator)), Action(lambda e:NodeLine(e)))
line.set_rule(__line)

@rule()
def blockstart(ls):
    def action_0(t, _1, a, _3, i, _5, b):
        return t.set_attributes(a).set_block(b).set_line(i)
    

    def action_1(c, _1, _2):
        return c
    
    return Either(
        (tag, Optional(_space), ZeroOrMore(attribute), Optional(_space), Optional(line), EOL, block(indent(ls)), Action(action_0)),
        (OneOrMore(attribute), Optional(line), EOL, Optional(block(indent(ls))), Action(lambda a, i, _2, b:NodeTag("div").set_attributes(a).set_block(b).set_line(i))),
        ("%", Optional(_space), ident, re.compile('[^\n]*'), EOL, Optional(block(indent(ls))), Action(lambda _0, _1, j, c, _4, b:NodeJinja(j, c, b))),
        (line, Optional(_space), EOL, Action(action_1))
    )

@rule()
def __block(ls):
    return (IndentedBlock(blockstart(ls), ls), Action(lambda i:NodeBlock(i)))
block.set_rule(__block)
