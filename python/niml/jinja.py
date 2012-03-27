import os.path
import os
import getpass

from jinja2 import  Environment, TemplateSyntaxError
from jinja2.ext import Extension

from pwpeg import Parser

from . import niml
from . import printer

class NimlExtension(Extension):

    def __init__(self, environment, cache=True):
        super(NimlExtension, self).__init__(environment)

        environment.extend(
            niml_compact=False,
            niml_file_extensions=('.niml',),
        )

        self.parser = Parser(niml.block.instanciate(0))

        self.cache = cache
        if cache:
            try:
                dirname = '/tmp/{0}/niml-ext'.format(getpass.getuser())
                self.dirname = dirname
                os.makedirs(dirname)
            except Exception as e:
                if e.errno != 17: # file exists
                    self.dirname = None


    def preprocess(self, source, name, filename=None):
        if name is None or os.path.splitext(name)[1] not in \
            self.environment.niml_file_extensions:
            return source

        if self.dirname:
            try:
                f = file(os.path.join(self.dirname, '{0}{1}'.format(os.path.basename(name), hash(source))), 'r')
                str = f.read().decode('utf-8')
                f.close()
                return str
            except Exception as e:
                pass

        visitor = printer.NodeVisitor(self.environment.niml_compact)

        try:
            root = self.parser.parse(source)
            result = visitor.visit(root)

            if self.dirname:
                try:
                    f = file(os.path.join(self.dirname, '{0}{1}'.format(os.path.basename(name), hash(source))), 'w')
                    f.write(result.encode('utf-8'))
                    f.close()
                except Exception as e:
                    pass

            return result
        except TemplateSyntaxError as e:
            print(result)
            raise TemplateSyntaxError(e.message, e.lineno, name=name, filename=filename)
