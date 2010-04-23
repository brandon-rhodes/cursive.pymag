"""Command-line routines for Restructured Text authors.

"""
__version__ = '0.3'
__testrunner__ = 'nose'
__requires__ = [ 'cursive.tools', 'docutils' ]
__author__ = 'Brandon Craig Rhodes <brandon@rhodesmill.org>'
__url__ = 'http://bitbucket.org/brandon/cursivepymag/'

from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)
