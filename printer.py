from nodes import NodeJinja
import re

re_endspc = re.compile("([ \t]*\n)*$")
def addend(txt, end):
    return re_endspc.sub(lambda m: end + m.group(0), txt)

class NodeVisitor(object):
    def __init__(self, compact=True):
        self.compact = compact
        if compact:
            self.joiner = " "
        else:
            self.joiner = "\n"

    def visit(self, node):
        return getattr(self, node.__class__.__name__)(node)

    def str(self, s):
        return s

    def NoneType(self, value):
        return ""

    def NodeLine(self, line):
        res = map(lambda e: self.visit(e), line)
        return "".join(res)

    def NodeTag(self, tag):
        op = []
        if tag.classes:
            op.append('class="{0}"'.format(" ".join([t for t in tag.classes ])))
        if tag.id:
            op.append('id="{0}"'.format(tag.id))
        if tag.attribs:
            op.append(" ".join([ '{0}="{1}"'.format(key, self.visit(value)) for key, value in tag.attribs.items()] ))
        op = " ".join(op)
        if op: op = " " + op

        res = []
        res.append("<{0}{1}>".format(tag.name, op) + self.visit(tag.line))

        if tag.block:
            res.append(addend(self.visit(tag.block), "</{0}>".format(tag.name)))
        else:
            res[0] = addend(res[0], "</{0}>".format(tag.name))

        return (self.joiner if not self.compact else "").join(res)

    def NodeBlock(self, block):
        res = []

        for i, b in enumerate(block):
            res.append( "{0}{1}".format("" if self.compact else b[0], self.visit(b[1])) )

            if isinstance(b[1], NodeJinja):
                nxt = None
                if i < len(block) - 1:
                    nxt = block[i + 1][1]

                if b[1].name in ["if", "elif", "else"]:
                    if not isinstance(nxt, NodeJinja) or nxt.name not in ["elif", "else"]:
                        res[-1] = addend(res[-1], "{{% endif %}}".format(b[1].name))

                if b[1].name in ["for", "macro", "filter"]:
                    res[-1] = addend(res[-1], "{{% end{0} %}}".format(b[1].name))

            if b[2]:
                for l in b[2].split("\n")[:-1]:
                    res.append("")
        return self.joiner.join(res)

    def NodeJinja(self, j):
        return "{{% {0} {1} %}}".format(j.name, j.args.strip()) + ("" if not j.block else ("\n" if not self.compact else "") + self.visit(j.block))

