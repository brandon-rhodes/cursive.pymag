#!/usr/bin/env python
#
"""Parser utilities for working with ceres files.
"""

__version__ = "$Id: ceres.py 3368 2009-03-11 15:19:38Z brandon $"

# Import system modules
import logging
import re
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
import textwrap

# Import local modules


# Module

logger = logging.getLogger('ceres')

class Paragraph:
    """Base class for paragraphs."""
    STR_JOIN = ' '
    MARKUP_PATTERNS = [ re.compile(m + '(.+?)' + m, re.DOTALL)
                        for m in [ r'\*\*', "''", '//' ]
                        ]

    COMMENT_PREFIX = '{{{{'
    COMMENT_PREFIX_STRIP = '{'
    COMMENT_SUFFIX = '}}}}'
    COMMENT_SUFFIX_STRIP = '}'
    COMMENT_PATTERN = re.compile('({{{{.*?}}}})', re.DOTALL)
    ENUMERATED_PATTERN = re.compile('\w*\(\d+\)\w*(.*)')

    def __init__(self):
        self.first_line = None
        self.last_line = None
        self.lines = []
        return

    def append(self, line, num=None):
        """Add a line of text to the paragraph"""
        if self.first_line is None:
            # first line number
            self.first_line = num
        elif self.last_line is None and num is not None:
            # 2nd call with a line number
            self.last_line = num
        elif self.last_line is not None and num is not None and num > self.last_line:
            # incrementing line number from outside
            self.last_line = num
        elif num is None:
            # incrementing line number inside
            if self.last_line is None:
                self.last_line = self.first_line + 1
            else:
                self.last_line += 1
        self.lines.append(line.rstrip())
        return

    def get_line_numbers(self):
        return (self.first_line, self.last_line)
    def allows_blank_lines(self):
        """Does the paragraph allow embedded blank lines?"""
        return False
    def is_closed(self):
        """Have we encountered the end of the paragraph?"""
        return False

    def enumerate_comments(self, start):
        """Find inline comments in the paragraph, 
        and enumerate them starting from 'start'.
        """
        logging.debug('%s.enumerate_comments(%d)', self.__class__.__name__, start)

        body = self.as_string(include_markup=True, wrap_lines=False)
        logging.debug('body="%s"', body)

        split_parts = self.COMMENT_PATTERN.split(body)
        converted_parts = []
        counter = start
        comments = []

        for part in split_parts:
            logging.debug('Part: "%s"', part)
            if part.startswith(self.COMMENT_PREFIX):
                part = part.lstrip(self.COMMENT_PREFIX_STRIP)
                part = part.rstrip(self.COMMENT_SUFFIX_STRIP)
                part = part.strip()

                counter += 1
                already_enumerated = self.ENUMERATED_PATTERN.match(part)
                if already_enumerated is not None:
                    logging.debug('this comment is already enumerated')
                    comment = already_enumerated.groups(0)[0]
                else:
                    logging.debug('this comment is not already enumerated')
                    comment = part
                comment = comment.strip()
                logging.debug("comment = '%s'", comment)

                converted_parts.append('{{{{ (%d) %s }}}}' % (counter, comment))
                comments.append('%d. %s' % (counter, comment))
                
            else:
                converted_parts.append(part)

        # Reset our text content
        self.lines = []
        for part in converted_parts:
            self.append(part)
        return comments

    def get_string_body(self):
        """Return a basic string representation, joining the input lines."""
        return self.STR_JOIN.join(self.lines)
    def _strip_markup(self, text):
        """Return a new version of the text without any embedded markup."""
        for pattern in self.MARKUP_PATTERNS:
            text = pattern.sub(r'\1', text)
        return text
    def _wrap_lines(self, text):
        """Wrap the input text according to paragraph-specific rules."""
        return textwrap.fill(text, 72, break_long_words=False)

    def as_string(self, include_markup=True, wrap_lines=False):
        """Return a string representation of the paragraph.

        Arguments:
          include_markup=True - leave markup embedded in the text
          wrap_lines=False - wrap the text to 80 columns wide
        """
        body = self.get_string_body()
        if not include_markup:
            body = self._strip_markup(body)
        if wrap_lines:
            body = self._wrap_lines(body)
        return body
    def __str__(self):
        """Return a string representation of the paragraph text"""
        return self.as_string()

    WORDS_NOT_COUNTED = [
        re.compile(r'\[\[.*?\]\]', re.DOTALL), # embedded URLs
        re.compile(r'[(][)][.]?', re.DOTALL), # empty parens
        ]
    def get_word_count(self):
        """Return the number of words in this paragraph."""
        text = self.as_string(include_markup=False, wrap_lines=False)
        # Remove some text that should not be counted
        for pattern in self.WORDS_NOT_COUNTED:
            text = pattern.sub('', text)
        # Remove comments
        text = self.COMMENT_PATTERN.sub('', text)
        logger.debug('Counting words in "%s"', text)
        return len(text.split())

class MultiPartParagraph(Paragraph):
    START_TAG = None
    END_TAG = None
    STR_JOIN = '\n'
    def allows_blank_lines(self):
        return True
    def is_closed(self):
        if not self.lines:
            return False
        if len(self.lines) == 1 and (self.START_TAG == self.END_TAG):
            # Does the first line start and end with the tag?
            line = self.lines[0].strip()
            if line == self.START_TAG:
                return False
            logger.debug('closing on first line')
            return (line.startswith(self.START_TAG) and line.endswith(self.END_TAG))
        return self.lines[-1].endswith(self.END_TAG)

class CodeParagraph(MultiPartParagraph):
    """Formatted code."""
    MAX_NUM_LINES = 6
    MAX_LINE_LEN = 52
    START_TAG = '<code'
    END_TAG = 'code>'
    STR_JOIN = '\n'

    def allows_blank_lines(self):
        return True

    def _strip_markup(self, text):
        """No-op"""
        return text
    def _wrap_lines(self, text):
        """No-op"""
        return text
    def get_string_body(self):
        """Return a basic string representation, joining the input lines."""
        lines_to_join = [ ]
        for line in self.lines:
            dedented = line.lstrip()
            difference = line[:-len(dedented)]
            no_tabs = difference.replace('\t', '    ')
            replacement = no_tabs + dedented
            lines_to_join.append(replacement)
        return self.STR_JOIN.join(lines_to_join)

    def is_closed(self):
        return len(self.lines) > 1 and self.lines[-1].endswith(self.END_TAG)
    def get_word_count(self):
        return 0
    def enumerate_comments(self, start):
        "Don't mess with code paragraphs."
        return []

    def get_block_type(self):
        """Return the type of content in the block.
        """
        if '=' in self.lines[0]:
            split_on = '='
        else:
            split_on = ' '
        line_parts = self.lines[0][1:-1].split(split_on)
        if len(line_parts) > 1:
            block_type = line_parts[-1]
        else:
            block_type = 'txt'
        return block_type

class NoteParagraph(CodeParagraph):
    START_TAG = '<note'
    END_TAG = 'note>'

class NestedParagraph(MultiPartParagraph):

    TAG_SEPARATOR = '\n'

    def as_string(self, include_markup=True, wrap_lines=False):
        # Might have nested paragraphs, so cope by parsing recursively.
        lines_to_parse = []
        for line in self.lines:
            if line.startswith(self.START_TAG):
                line = line[len(self.START_TAG):]
            if line.endswith(self.END_TAG):
                line = line[:-1 * len(self.END_TAG)]
            lines_to_parse.append(line)
        nested_body = '\n\n'.join([ p.as_string(include_markup=include_markup, wrap_lines=wrap_lines)
                                    for p in parse(lines_to_parse)
                                    ])
        return self.START_TAG + self.TAG_SEPARATOR + nested_body + self.TAG_SEPARATOR + self.END_TAG

class CalloutParagraph(NestedParagraph):
    """Callout"""
    START_TAG = '{{callout'
    END_TAG = '}}'
    MARKUP_PATTERNS = [ START_TAG, END_TAG ]
    STR_JOIN = '\n'
    def get_word_count(self):
        return 0


class DeckParagraph(NestedParagraph):
    """Description of article"""
    START_TAG = '=d='
    END_TAG = '=d='
    STR_JOIN = '\n'
    def get_word_count(self):
        return 0

MULTI_PART_PARAGRAPH_TYPES = [ CodeParagraph,
                               NoteParagraph,
                               CalloutParagraph,
                               DeckParagraph,
                               ]

class MarkupParagraph(Paragraph):
    MARKUP = None
    def __init__(self):
        Paragraph.__init__(self)
        self._found_close = False
        return
    def is_closed(self):
        return self._found_close
    def append(self, line, num=0):
        if line.lstrip().startswith(self.MARKUP):
            line = line.lstrip()[len(self.MARKUP):].lstrip()
        if line.rstrip().endswith(self.MARKUP):
            line = line.rstrip()[:-1 * len(self.MARKUP)].rstrip()
            self._found_close = True
        Paragraph.append(self, line, num=num)
        return
    def get_string_body(self, include_markup=True):
        base = Paragraph.get_string_body(self)
        if include_markup:
            text = self.MARKUP + base + self.MARKUP
        else:
            text = base
        return text
    def _wrap_lines(self, text):
        return text

class TitleParagraph(MarkupParagraph):
    """Title of article."""
    MARKUP = '=t='
    def get_word_count(self):
        return 0
    def as_string(self, include_markup=False, wrap_lines=False):
        """Titles cannot contain markup, so always strip it by default."""
        return MarkupParagraph.as_string(self, 
                                         include_markup=False, 
                                         wrap_lines=wrap_lines,
                                         )

class ByLineParagraph(MarkupParagraph):
    """Author's name"""
    MARKUP = '=b='
    def get_word_count(self):
        return 0

class HeadingParagraph(MarkupParagraph):
    """Section heading"""
    MARKUP = '=h='
    def get_word_count(self):
        return 0
    def as_string(self, include_markup=False, wrap_lines=False):
        """Headers cannot contain markup, so always strip it by default."""
        return MarkupParagraph.as_string(self, 
                                         include_markup=False, 
                                         wrap_lines=wrap_lines,
                                         )

class ListParagraph(MarkupParagraph):
    MARKUP = '- '
    STR_JOIN = '\n- '
    def _wrap_lines(self, text):
        return text
    def get_string_body(self):
        base = MarkupParagraph.get_string_body(self)
        return base[:-2] # strip trailing '- '

MARKUP_PARAGRAPH_TYPES = [ TitleParagraph,
                           ByLineParagraph,
                           HeadingParagraph,
                           ListParagraph,
                           ]

def parse(input):
    """Generate a stream of Paragraph objects from the input lines.

    The input argument must be an iterable which returns individual
    lines of text.
    """
    current_para = None
    line_num = 0
    for line in input:
        line_num += 1

        # Weirdly, this "parse" routine seems to be called over again on
        # the output it has already produced; so, to make sure we only
        # decode each line from UTF-8 once, we make sure the line is not
        # yet Unicode before calling "decode()".

        if not isinstance(line, unicode):
            try:
                line = line.decode('utf8')
            except UnicodeEncodeError:
                print ("Error: cannot decode article line %d as UTF-8: %r"
                       % (line_num, line))
                raise

        logger.debug('new line %d: "%s"', line_num, line.rstrip())

        stripped_line = line.strip()
        if not stripped_line:
            if current_para:
                if not current_para.allows_blank_lines():
                    # End of paragraph
                    logger.debug('blank line yielding: %s', repr(current_para))
                    yield current_para
                    current_para = None
                    continue
                else:
                    # Part of a multi-part paragraph
                    current_para.append(line, line_num)
                    continue
            else:
                # Otherwise just ignore the blank line
                logger.debug('ignoring blank line outside of paragraphs')
                continue

        if current_para is None:
            for p_type in MARKUP_PARAGRAPH_TYPES:
                if line.startswith(p_type.MARKUP):
                    logger.debug('Creating %s' % p_type.__name__)
                    current_para = p_type()
            if current_para is None:
                for p_type in MULTI_PART_PARAGRAPH_TYPES:
                    if line.startswith(p_type.START_TAG):
                        logger.debug('Creating %s' % p_type.__name__)
                        current_para = p_type()
            if current_para is None:
                logger.debug('Creating Paragraph')
                current_para = Paragraph()

        current_para.append(line, line_num)
        
        # Did that line end our multi-part paragraph?
        if current_para.is_closed():
            logger.debug('para closed, yielding: %s', repr(current_para))
            yield current_para
            current_para = None

    # Make sure we give up the last paragraph
    if current_para:
        yield current_para

    raise StopIteration

