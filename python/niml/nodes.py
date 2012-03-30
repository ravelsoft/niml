"""
"""

class NodeAttribute(object):
    def __init__(self, value): self.value = value
class NodeClass(NodeAttribute): pass
class NodeId(NodeAttribute): pass
class NodeSingle(NodeAttribute): pass

class NodeNamed(NodeAttribute):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class NodeBlock(list): pass
class NodeLine(list): pass

class NodeJinja(object):
    def __init__(self, name, args, block=None):
        self.name = name
        self.args = args
        self.block = block

class NodeTag(object):
    def __init__(self, name):
        self.name = name
        self.classes = set()
        self.id = None
        self.attribs = dict()
        self.singles = set()
        self.block = None
        self.line = None
        self.selfclosing = False

    def add_attribute(self, a):
        if isinstance(a, NodeId):
            self.id = a.value
        if isinstance(a, NodeClass):
            self.classes.add(a.value)
        if isinstance(a, NodeNamed):
            self.attribs[a.name] = a.value
        if isinstance(a, NodeSingle):
            self.singles.add(a.value)
        return self

    def set_attributes(self, attrs=[]):
        for a in attrs: self.add_attribute(a)
        return self

    def set_block(self, block):
        self.block = block
        return self

    def set_line(self, line):
        self.line = line
        return self

    def set_selfclosing(self, selfclosing=True):
        self.selfclosing = selfclosing
        return self

class NodeExtern(NodeTag):
    def __init__(self, name):
        self.extern_name = name

        if name in ["css", "sass", "scss", "stylus"]:
            super(NodeExtern, self).__init__("style")
            self.set_attributes([
                NodeNamed("rel", "stylesheet"),
                NodeNamed("type", "text/css")
            ])
        elif name in ["javascript", "coffeescript", "coco", "coffee"]:
            super(NodeExtern, self).__init__("script")
            self.set_attributes([
                NodeNamed("type", "text/javascript")
            ])
        else:
            super(NodeExtern, self).__init__(name)

    def set_block(self, block):
        self.block = block
        return self
