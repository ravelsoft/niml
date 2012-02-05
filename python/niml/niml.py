#!/usr/bin/env python
from pwpeg import *
from pwpeg.helpers import *


##############################################################
# Start of included code
import re

from nodes import *

try:
    u = unicode
except Exception as e:
    u = str

_is = [] # _is is short for "Indent Stack"
def checkindent(indent, start):
    sindent = len(start) - start.rfind('\n') - 1
    ci = len(_is) # Current indent index

    if indent == ci:
        # We're looking at a new indentation, to potentially push it
        # on the stack if we can.

        if ci == 0 or sindent > _is[-1]:
            _is.append(sindent)
            return True

        # It is not higher, so we just tell the parser that we
        # can't continue on that indentation level.
        return False

    if indent == ci - 1:
        # We're in the current block and want to check if this
        # line is correctly indented.

        # We're at the correct level, so we just return True
        if sindent == _is[-1]: return True

        # The indentation is superior, which is not logical !
        if sindent > _is[-1]: raise Exception("Incorrect indent")

        # We're looking at a deindent, so we pop the current indent
        # level from the stack.
        _is.pop()
        return False

# End of included code
##############################################################

# Forward declaration of Regular rules
EOL = Rule().set_name("EOL")
_space = Rule().set_name("_space")
access_or_funcall = Rule().set_name("access_or_funcall")
attrib = Rule().set_name("attrib")
attribute = Rule().set_name("attribute")
cls = Rule().set_name("cls")
comment = Rule().set_name("comment")
fullspace = Rule().set_name("fullspace")
id = Rule().set_name("id")
ident = Rule().set_name("ident")
single_prop = Rule().set_name("single_prop")
string = Rule().set_name("string")
tag = Rule().set_name("tag")
variable = Rule().set_name("variable")
variable_component = Rule().set_name("variable_component")
variable_dotted = Rule().set_name("variable_dotted")
vident = Rule().set_name("vident")


# Forward declaration of Function rules
block = FunctionRule().set_name("block")
blockstart = FunctionRule().set_name("blockstart")
delimited_line = FunctionRule().set_name("delimited_line")
line = FunctionRule().set_name("line")
lineelt = FunctionRule().set_name("lineelt")


# Function Rules implementation
def _block(indent):
    def action_2(lines):
        return NodeBlock(lines)

    return OneOrMore(Rule(
        fullspace,
        lambda start: ( checkindent(indent, start) ) ,
        blockstart.instanciate(indent)
    ).set_action(lambda start, block: ([start, block]) )).set_action(action_2)
block.set_fn(_block)

def _blockstart(indent):
    def action_0(t, _1, a, _3, i, _5, b):
        return t.set_attributes(a).set_block(b).set_line(i)

    def action_1(c, _1, _2):
        return c

    return Either(
        Rule(
            tag,
            Optional(_space),
            ZeroOrMore(attribute),
            Optional(_space),
            Optional(line),
            EOL,
            block.instanciate(indent + 1)
        ).set_action(action_0),
        Rule(
            OneOrMore(attribute),
            Optional(line),
            EOL,
            Optional(block.instanciate(indent + 1))
        ).set_action(lambda a, i, _2, b: (NodeTag("div").set_attributes(a).set_block(b).set_line(i)) ),
        Rule(
            "%",
            Optional(_space),
            ident,
            re.compile('[^\n]*'),
            EOL,
            Optional(block.instanciate(indent + 1))
        ).set_action(lambda _0, _1, j, c, _4, b: (NodeJinja(j, c, b)) ),
        Rule(
            line,
            Optional(_space),
            Optional(EOL)
        ).set_action(action_1)
    )
blockstart.set_fn(_blockstart)

def _delimited_line(delim):
    return Rule(
        delim,
        Optional(line.instanciate(delim)),
        delim
    ).set_action(lambda _0, l, _2: (l or "") )
delimited_line.set_fn(_delimited_line)

def _line(terminator=EOL):
    return OneOrMore(lineelt.instanciate(terminator)).set_action(lambda e: (NodeLine(e)) )
line.set_fn(_line)

def _lineelt(terminator):
    return Either(
        Rule(
            "@/",
            ident,
            ZeroOrMore(attribute)
        ).set_action(lambda _0, i, a: (NodeTag(i).set_selfclosing().set_attributes(a)) ),
        Rule(
            tag,
            Optional(_space),
            ZeroOrMore(attribute),
            Optional(_space),
            "[",
            Optional(line.instanciate("]")),
            "]"
        ).set_action(lambda t, _1, a, _3, _4, i, _6: (t.set_attributes(a).set_line(i or "")) ),
        Rule(
            tag,
            Optional(_space),
            ZeroOrMore(attribute),
            Optional(_space),
            Optional(line.instanciate(terminator))
        ).set_action(lambda t, _1, a, _3, i: (t.set_attributes(a).set_line(i)) ),
        variable,
        Rule(
            '\\',
            re.compile('.')
        ).set_action(lambda _0, t: (t) ),
        Rule(
            Not(terminator),
            re.compile('.')
        ).set_action(lambda c: (c) )
    )
lineelt.set_fn(_lineelt)



# Simple Rules implementation
EOL.set_productions("\n")

_space.set_productions(re.compile('[ \t]*'))

access_or_funcall.set_productions(Either(
    Balanced.instanciate("[", "]", "\\"),
    Balanced.instanciate("(", ")", "\\")
).set_action(lambda b: (b) ).set_name("Access or Funcall Either"))

attrib.set_productions(
    ident,
    "=",
    Either(
        string,
        line.instanciate(re.compile('\s'))
    )
).set_action(lambda key, _1, value: (NodeNamed(key, value)) )

attribute.set_productions(
    Optional(_space),
    Either(
        id,
        cls,
        single_prop,
        attrib
    )
).set_action(lambda _0, a: (a) )

cls.set_productions(
    ".",
    Either(
        variable,
        ident
    )
).set_action(lambda _0, i: (NodeClass(i)) )

comment.set_productions(re.compile('\s*#\s.*', re.M))

fullspace.set_productions(re.compile('([ \t]*\n)*[ \t]*'))

id.set_productions(
    '#',
    Either(
        variable,
        ident
    )
).set_action(lambda _0, i: (NodeId(i)) )

ident.set_productions(re.compile('[-$a-zA-Z0-9:_]+'))

single_prop.set_productions(
    "\\",
    Either(
        variable,
        ident
    )
).set_action(lambda _0, i: (NodeSingle(i)) )

string.set_productions(Either(
    delimited_line.instanciate("\""),
    delimited_line.instanciate("'")
))

tag.set_productions(
    "@",
    Not("/"),
    ident
).set_action(lambda _0, i: (NodeTag(i)) )

variable.set_productions(
    "$",
    OneOrMoreSeparated.instanciate(variable_dotted, "|")
).set_action(lambda _0, i: (u("{{{{ {0} }}}}").format(u("|").join(i))) )

variable_component.set_productions(
    vident,
    ZeroOrMore(access_or_funcall)
).set_action(lambda i, a: (i + "".join(a)) )

variable_dotted.set_productions(OneOrMoreSeparated.instanciate(variable_component, ".").set_action(lambda i: (u(".").join(i)) ))

vident.set_productions(re.compile('[a-zA-Z_][a-zA-Z0-9_]*'))


