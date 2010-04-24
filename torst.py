#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2010 Doug Hellmann.  All rights reserved.
#
"""Convert Ceres documents to reStructuredText.
"""

import codecs
import glob
from optparse import OptionParser
import os
import re
import sys
import textwrap

from cursive.pymag import ceres


class Converter(object):
    """Converts Ceres to RST
    """

    def __init__(self, input_directory):
        self.input_directory = input_directory
        self.seen_listings = set()
        return
    
    def convert(self, paras, output):
        for para in paras:
            try:
                handler = getattr(self, 'handle_{0}'.format(para.__class__.__name__))
            except AttributeError:
                raise ValueError('Unhandled paragraph type {0}'.format(para.__class__.__name__))
            converted = handler(para)
            if converted is not None:
                output.write(converted)
                output.write('\n\n')
        return

    def handle_TitleParagraph(self, para):
        title = para.get_string_body(include_markup=False)
        overline = '=' * len(title)
        return '\n'.join([overline, title, overline])

    def handle_ByLineParagraph(self, para):
        # Ignore the by-line
        return None

    def handle_DeckParagraph(self, para):
        deck = para.as_string(include_markup=False, wrap_lines=True)
        deck = deck.replace(para.START_TAG, '').replace(para.END_TAG, '').strip()
        deck = textwrap.fill(deck, initial_indent='   ', subsequent_indent='   ')
        return '\n'.join(['.. cssclass:: deck', '', deck])

    def handle_HeadingParagraph(self, para):
        heading = para.get_string_body(include_markup=False)
        underline = '=' * len(heading)
        return '\n'.join([heading, underline])

    def fix_markup(self, text):
        for pattern, subst in [
            (re.compile('//(.*?)//', re.DOTALL), r"*\1*"), # italics
            (re.compile("''(.*?)''", re.DOTALL), r"``\1``"), # literal
            (re.compile(r'\[\[(.*?)\]\]', re.DOTALL), r'\1'), # URLs
            ]:
            text = pattern.sub(subst, text)
        return text

    LISTING_PATTERN = re.compile(r'[lL]isting[\s ]+(\d+)')
    def add_listings(self, text):
        # Look for listings
        listings = self.LISTING_PATTERN.findall(text)
        results = [ text ]
        for listing in listings:
            if listing in self.seen_listings:
                continue
            self.seen_listings.add(listing)
            print '  new listing', listing
            matches = glob.glob(os.path.join(self.input_directory,
                                             '[lL]isting{0}.*'.format(listing),
                                             ))
            for m in matches:
                if m not in self.seen_listings:
                    print '    file', m
                    results.append('Listing {0}\n{1}\n\n.. literalinclude:: {2}\n   :linenos:'.format(listing, '-' * (8+len(listing)), m))
                    self.seen_listings.add(m)
        return '\n\n'.join(results)

    def handle_Paragraph(self, para):
        text = textwrap.fill(self.fix_markup(unicode(para)))
        text = self.add_listings(text)
        return text

    def handle_ListParagraph(self, para):
        text = self.fix_markup(unicode(para))
        text = self.add_listings(text)
        return text

def command(argv=sys.argv[2:]):
    """Convert a Ceres document to reStructuredText
    """
    parser = OptionParser(
        usage='cursive ceres2rst [options] <input_directory>',
        conflict_handler='resolve',
        description=command.__doc__,
        )
    parser.add_option('-o', '--output',
                      action='store',
                      dest='output_filename',
                      default='index.rst',
                      help='name of the output file, including path.',
                      )
    parser.add_option('-e', '--encoding',
                      action='store',
                      dest='encoding',
                      default='utf8',
                      help='encoding name for Unicode files. Defaults to "utf8".',
                      )
    parser.add_option('--debug',
                      action='store_true',
                      default=False,
                      dest='debug',
                      help='debug mode',
                      )
    (options, args) = parser.parse_args(argv)
    if not args:
        parser.error('Please specify the directory containing the Ceres article file(s)')
    input_directory = args[0]
    c = Converter(input_directory)
    try:
        print 'Looking for article in {0}'.format(input_directory)
        page_filename = os.path.join(input_directory, 'page.src.txt')
        if not os.path.exists(page_filename):
            raise ValueError('Did not find "{0}"'.format(page_filename))
        with codecs.open(page_filename, 'r', encoding=options.encoding) as input:
            print 'Reading {0}'.format(page_filename)
            with codecs.open(options.output_filename, 'w', encoding=options.encoding) as output:
                print 'Writing to {0}'.format(options.output_filename)
                c.convert(ceres.parse(input), output)
    except Exception, err:
        if options.debug:
            raise
        parser.error(str(err))
    return

