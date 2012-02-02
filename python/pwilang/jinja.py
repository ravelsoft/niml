import os.path

from jinja2 import  Environment, TemplateSyntaxError
from jinja2.ext import Extension

from pwpeg import Parser

from . import pwilang
from . import printer

class PwilangExtension(Extension):

    def __init__(self, environment):
        super(PwilangExtension, self).__init__(environment)

        environment.extend(
            pwilang_compact=False,
            pwilang_file_extensions=('.pwi',),
        )

        self.parser = Parser(pwilang.block(""))


    def preprocess(self, source, name, filename=None):
        if name is None or os.path.splitext(name)[1] not in \
            self.environment.pwilang_file_extensions:
            return source

        visitor = printer.NodeVisitor(self.environment.pwilang_compact)

        try:
            root = self.parser.parse(source)
            result = visitor.visit(root)
            return result
        except TemplateSyntaxError, e:
            print(result)
            raise TemplateSyntaxError(e.message, e.lineno, name=name, filename=filename)
