import os.path

from jinja2 import  Environment, TemplateSyntaxError
from jinja2.ext import Extension

from pwpeg import Parser

from . import niml
from . import printer

class NimlExtension(Extension):

    def __init__(self, environment):
        super(NimlExtension, self).__init__(environment)

        environment.extend(
            niml_compact=False,
            niml_file_extensions=('.niml',),
        )

        self.parser = Parser(niml.block.instanciate(0))


    def preprocess(self, source, name, filename=None):
        if name is None or os.path.splitext(name)[1] not in \
            self.environment.niml_file_extensions:
            return source

        visitor = printer.NodeVisitor(self.environment.niml_compact)

        try:
            root = self.parser.parse(source)
            result = visitor.visit(root)
            return result
        except TemplateSyntaxError, e:
            print(result)
            raise TemplateSyntaxError(e.message, e.lineno, name=name, filename=filename)
