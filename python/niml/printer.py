import re
from subprocess import Popen, PIPE

from .nodes import NodeJinja, NodeBlock, NodeLine
from .niml import getindent

re_endspc = re.compile("([ \t]*\n)*$")
def addend(txt, end):
    return re_endspc.sub(lambda m: end + m.group(0), txt)

def adjuststarts(indent, linelists):
    lowest = None

    for l in linelists:
        i = getindent(l[0])
        if lowest is None or i < lowest:
            lowest = i

    if indent is None:
        result = [[l[0][:-lowest], l[1]] for l in linelists]
        result[0][0] = "\n" + result[0][0]
        return result
    else:
        finalindent = lowest - indent

        result = [[l[0][:-finalindent], l[1]] for l in linelists]
        # First line has a strange indent.
        result[0][0] = "\n" + result[0][0]# [:-indent]
        return result

def run(cmd, stdin=None):
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    res = p.communicate(stdin) if stdin else p.communicate()
    if res[1]:
        raise Exception(res[1])
    return res[0]

def compile_coco(txt):
    return run(["coco", "-bpce", txt])

def compile_coffee(txt):
    return run(["coffee", "-bce", txt])

def compile_sass(txt):
    return run(["sass", "-s"], txt)

def compile_scss(txt):
    return run(["sass", "-s", "--scss"], txt)

# Python 3 compatibility gimmick to avoid unicode errors.
try:
    unicode = unicode
except:
    unicode = str

class NodeVisitor(object):
    def __init__(self, compact=False):
        self.compact = compact
        if compact:
            self.joiner = unicode(" ")
        else:
            self.joiner = unicode("\n")

    def visit(self, node):
        return getattr(self, node.__class__.__name__)(node)

    def str(self, s):
        return s.decode("utf-8")

    def unicode(self, u):
        return u

    def NoneType(self, value):
        return ""

    def NodeLine(self, line):
        res = map(lambda e: self.visit(e), line)
        return unicode("").join(res)

    def NodeTag(self, tag):
        op = []
        if tag.classes:
            op.append(unicode('class="{0}"').format(" ".join([t for t in tag.classes ])))
        if tag.id:
            op.append(unicode('id="{0}"').format(tag.id))
        if tag.attribs:
            op.append(unicode(" ").join([ unicode('{0}="{1}"').format(key, self.visit(value)) for key, value in tag.attribs.items()] ))
        if tag.singles:
            op.append(unicode(" ").join(tag.singles))
        op = unicode(" ").join(op)
        if op: op = unicode(" ") + op

        selfclosing = "/" if tag.selfclosing else ""

        res = []
        res.append(unicode("<{0}{1}{2}>").format(tag.name, op, selfclosing) + self.visit(tag.line))

        if not selfclosing:
            if tag.block:
                res.append(addend(self.visit(tag.block), unicode("</{0}>").format(tag.name)))
            else:
                res[0] = addend(res[0], unicode("</{0}>").format(tag.name))

        return (self.joiner if not self.compact else unicode("")).join(res)

    def NodeBlock(self, block):
        res = []

        for i, b in enumerate(block):
            res.append( unicode("{0}{1}").format("" if self.compact else b[0], self.visit(b[1])) )

            if isinstance(b[1], NodeJinja):
                nxt = None
                if i < len(block) - 1:
                    nxt = block[i + 1][1]

                if b[1].name in ["if", "elif", "else"]:
                    if not isinstance(nxt, NodeJinja) or nxt.name not in ["elif", "else"]:
                        res[-1] = addend(res[-1], "{{% endif %}}".format(b[1].name))

                if b[1].name in ["for", "macro", "filter", "block"]:
                    res[-1] = addend(res[-1], unicode("{{% end{0} %}}").format(b[1].name))

            #if b[2]:
            #    for l in b[2].split("\n")[:-1]:
            #        res.append("")
        return self.joiner.join(res)

    def NodeExtern(self, node):
        if not node.block:
            return ""

        res = []
        indent, lines = node.block

        if node.name == "plain":
            lines = adjuststarts(indent, lines)
            txt = "".join([b[0] + b[1] for b in lines])
            res.append(txt)

        # We're going to format code, so we eat all the useless indent.
        else:
            lines = adjuststarts(None, lines)
            txt = "".join([b[0] + b[1] for b in lines])

            if node.extern_name == "coco":
                txt = compile_coco(txt)
            if node.extern_name in ["coffeescript", "coffee"]:
                txt = compile_coffee(txt)
            if node.extern_name == "scss":
                txt = compile_scss(txt)
            if node.extern_name == "sass":
                txt = compile_sass(txt)

            node.block = None
            node.set_line(NodeLine([ txt ]))
            res.append(self.NodeTag(node))

        return self.joiner.join(res)

    def NodeJinja(self, j):
        return unicode("{{% {0} {1} %}}").format(j.name, j.args.strip()) + ("" if not j.block else ("\n" if not self.compact else "") + self.visit(j.block))

