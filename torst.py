#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2010 Doug Hellmann.  All rights reserved.
#
"""Convert Ceres documents to reStructuredText.
"""

# Import system modules
from optparse import OptionParser

# Import third-party modules


# Import local modules
from cursive.pymag import ceres

def command(argv):
    """Convert a Ceres document to reStructuredText
    """
    parser = OptionParser(
        usage='cursive ceres2rst [options] <input_file>',
        conflict_handler='resolve',
        description=command.__doc__,
        )
    (options, args) = parser.parse_args(argv)
    print args
    raise NotImplementedError()
    return

