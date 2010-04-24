#!/usr/bin/env python
#
"""Tests for ceres.py
"""

__version__ = "$Id: test_ceres.py 2460 2008-08-16 21:48:37Z dhellmann $"

# Import system modules
import logging
import unittest

# Import local modules
from cursive.pymag.ceres import *

# Module

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    )


class ParagraphTest(unittest.TestCase):

    def testOneLine(self):
        p = Paragraph()
        p.append('foo')
        self.failUnlessEqual('foo', str(p))
        return

    def testTwoLines(self):
        p = Paragraph()
        p.append('foo')
        p.append('bar')
        self.failUnlessEqual('foo bar', str(p))
        return

    def testTrailingSpaces(self):
        p = Paragraph()
        p.append('foo ')
        p.append('bar ')
        self.failUnlessEqual('foo bar', str(p))
        return

    def testLineNumbersNotSet(self):
        p = Paragraph()
        p.append('foo ')
        p.append('bar ')
        self.failUnlessEqual((None, None), p.get_line_numbers())
        return

    def testLineNumbersSet(self):
        p = Paragraph()
        p.append('foo ', 1)
        p.append('bar ', 2)
        self.failUnlessEqual((1, 2), p.get_line_numbers())
        return

    def testLineNumbersPartiallySet(self):
        p = Paragraph()
        p.append('foo ', 1)
        p.append('bar ', None)
        self.failUnlessEqual((1, 2), p.get_line_numbers())
        return


class ParagraphStripMarkupTest(unittest.TestCase):

    def testBold(self):
        p = Paragraph()
        p.append('**foo**')
        self.failUnlessEqual('foo', p.as_string(include_markup=False))
        return

    def testItalics(self):
        p = Paragraph()
        p.append('//foo//')
        self.failUnlessEqual('foo', p.as_string(include_markup=False))
        return

    def testMonospace(self):
        p = Paragraph()
        p.append("''foo''")
        self.failUnlessEqual('foo', p.as_string(include_markup=False))
        return

    def testHeadingParagraph(self):
        p = HeadingParagraph()
        p.append("''foo'' ")
        p.append("**foo** ")
        p.append("//foo// ")
        self.failUnlessEqual('=h=foo foo foo=h=', p.as_string(include_markup=False))
        self.failUnlessEqual('=h=foo foo foo=h=', str(p))
        return

    def testTitleParagraph(self):
        p = TitleParagraph()
        p.append("''foo'' ")
        p.append("**foo** ")
        p.append("//foo// ")
        self.failUnlessEqual('=t=foo foo foo=t=', p.as_string(include_markup=False))
        self.failUnlessEqual('=t=foo foo foo=t=', str(p))
        return

    def testHeadingParagraphBody(self):
        p = HeadingParagraph()
        p.append("foo")
        self.failUnlessEqual('foo', p.get_string_body(include_markup=False))
        self.failUnlessEqual('=h=foo=h=', p.get_string_body(include_markup=True))
        return

    def testTitleParagraphBody(self):
        p = TitleParagraph()
        p.append("foo")
        self.failUnlessEqual('foo', p.get_string_body(include_markup=False))
        self.failUnlessEqual('=t=foo=t=', p.get_string_body(include_markup=True))
        return

class MarkupParagraphTest(unittest.TestCase):

    def testOneLine(self):
        p = TitleParagraph()
        p.append('=t=foo=t=')
        self.failUnlessEqual('=t=foo=t=', str(p))
        return

    def testWhitespace(self):
        p = TitleParagraph()
        p.append(' =t= foo =t= ')
        self.failUnlessEqual('=t=foo=t=', str(p))
        return

    def testTwoLines(self):
        p = TitleParagraph()
        p.append('foo')
        p.append('bar')
        self.failUnlessEqual('=t=foo bar=t=', str(p))
        return

class CodeParagraphTest(unittest.TestCase):

    def testOneLiner(self):
        p = CodeParagraph()
        p.append('<code>')
        p.append('  indented one line  ')
        p.append('</code>')
        self.failUnlessEqual('<code>\n  indented one line\n</code>', str(p))
        return

    def testParse(self):
        body = '''<code python>
(
    COLUMN_URL,
    COLUMN_ICON,
    COLUMN_NAME,
    COLUMN_DESC
) = range(4)
</code>
'''
        p = CodeParagraph()
        for line in body.splitlines():
            p.append(line)
        self.failUnlessEqual(body.strip(), str(p))
        return


class ParserTest(unittest.TestCase):

    def testBasicParsing(self):
        body = '''
=t=And Now For Something Completely Different=t=

=b=Doug Hellmann=b=

=d=Has your multi-threaded application grown GILs?  Take a look at these packages for easy-to-use process management and interprocess communication tools.=d=

There is no predefined theme for this column, so I plan to cover a different, likely unrelated, subject every month. The topics will range anywhere from open source packages in the Python Package Index (formerly The Cheese Shop, now PyPI) to new developments from around the Python community, and anything that looks interesting in between.  If there is something you would like for me to cover, send a note with the details to [[doug.hellmann@pythonmagazine.com]] and let me know, or add the link to your del.icio.us account with the tag "pymagdifferent".

<code=python>
import pp
job_server = pp.Server()
# Start tasks
f1 = job_server.submit(func1, args1, depfuncs1, 
    modules1)
f2 = job_server.submit(func1, args2, depfuncs1, 
    modules1)
f3 = job_server.submit(func2, args3, depfuncs2, 
    modules2)
# Retrieve the results
r1 = f1()
r2 = f2()
r3 = f3()  
</code>

When the pp worker starts, it detects the number of CPUs in the system and starts one process per CPU automatically, allowing me to take full advantage of the computing resources available.  Jobs are started asynchronously, and run in parallel on an available node.  The callable object returned when the job is submitted blocks until the response is ready, so response sets can be computed asynchronously, then merged synchronously.  Load distribution is transparent, making pp excellent for clustered environments.  
'''
        lines = body.splitlines()
        paras = list(parse(lines))

        expected_types = [ TitleParagraph,
                           ByLineParagraph,
                           DeckParagraph,
                           Paragraph,
                           CodeParagraph,
                           Paragraph,
                           ]

        for i, p, expected_type in zip(range(len(paras)), paras, expected_types):
            self.failUnless(isinstance(p, expected_type), 
                            '%s: Expected: %s Found: %s (%s)' % 
                            (i, expected_type, p.__class__.__name__, p))
        return

    def testMultiPartDeck(self):
        body = '''
=d=This is the start of the deck.  There is another paragraph below.

This is the end of the deck.=d=
'''
        lines = body.splitlines()
        paras = list(parse(lines))
        self.failUnlessEqual(1, len(paras))
        self.failUnlessEqual('=d=\nThis is the start of the deck.  There is another paragraph below.\n\nThis is the end of the deck.\n=d=', str(paras[0]))
        return

    def testMultiPartDeck2(self):
        body = '''
=d=
Object-orientation (OO) has been a well-established and accepted
technology for many years  now. Experienced practitioners of the
discipline know well, the real  benefits it provides, as well as
its costs -  as a famous economist once said,  "There is no free
lunch".

However, for relative  newcomers to OO, it's  not always obvious
when and where  to apply it. A technology -  any technology - is
not necessarily  relevant and applicable to  every situation. So
we need  to be able to  decide whether it's worth  applying to a
problem on hand.

    The goals of this article are:

    a) To  act as a  case study on  how to convert  a procedural
    Python application into an object-oriented (OO) one.

    b) To  explain what  OO concepts  have been  used in  the OO
    version, and why.

    c)  To  highlight  the  concrete benefits  achieved  by  the
    conversion.

    d) And finally, to show  that there can be applications that
    are  not-so-obvious candidates  for conversion  to OO,  with
    real cost and time benefits arising from the conversion.
=d=
'''
        lines = body.splitlines()
        paras = list(parse(lines))
        self.failUnlessEqual(1, len(paras))
        self.failUnlessEqual('''=d=
Object-orientation (OO) has been a well-established and accepted technology for many years  now. Experienced practitioners of the discipline know well, the real  benefits it provides, as well as its costs -  as a famous economist once said,  "There is no free lunch".

However, for relative  newcomers to OO, it\'s  not always obvious when and where  to apply it. A technology -  any technology - is not necessarily  relevant and applicable to  every situation. So we need  to be able to  decide whether it\'s worth  applying to a problem on hand.

    The goals of this article are:

    a) To  act as a  case study on  how to convert  a procedural     Python application into an object-oriented (OO) one.

    b) To  explain what  OO concepts  have been  used in  the OO     version, and why.

    c)  To  highlight  the  concrete benefits  achieved  by  the     conversion.

    d) And finally, to show  that there can be applications that     are  not-so-obvious candidates  for conversion  to OO,  with     real cost and time benefits arising from the conversion.
=d=''', str(paras[0]))
        return

    def testMultiLineParagraphs(self):
        body = '''
This is line one
and this is line two.
'''
        lines = body.splitlines()
        para = list(parse(lines))[0]
        self.failUnlessEqual('This is line one and this is line two.', str(para))
        return

    def testListParagraphs(self):
        body = '''

- one, one
- one, two

- two, one
- two, two
'''
        lines = body.splitlines()
        paras = list(parse(lines))
        self.failUnlessEqual(2, len(paras))
        self.failUnlessEqual('- one, one\n- one, two', str(paras[0]))
        self.failUnlessEqual('- two, one\n- two, two', str(paras[1]))
        return

    def testCalloutParagraphs(self):
        body = '''

{{callout
Line one
line two

another para
line 4
}}
'''
        lines = body.splitlines()
        para = list(parse(lines))[0]
        self.failUnlessEqual('{{callout\nLine one line two\n\nanother para line 4\n}}',
                             str(para))
        return

    def testCodeParagraph(self):
        body = '''<code python>
cat_iter = self.treestore.append(None)
self.treestore.set(cat_iter,
    self.COLUMN_CAT, "GNOME")

iter = self.treestore.append(cat_iter)
self.treestore.set(iter,
    self.COLUMN_URL, "http://www.gnome.org", 
    self.COLUMN_NAME, "GNOME", 
    self.COLUMN_DESC, "Official GNOME Website")

iter = self.treestore.append(cat_iter)
self.treestore.set(iter,
    self.COLUMN_URL, "http://www.gtk.org",
    self.COLUMN_NAME, "GTK+",
    self.COLUMN_DESC, "Official GTK+ Website")
</code>
'''
        lines = body.splitlines()
        paras = list(parse(lines))
        self.failUnlessEqual(1, len(paras))
        return


class WrapTextTest(unittest.TestCase):

    def testParagraph(self):
        text = """When the pp worker starts, it detects the number of CPUs in the system and starts one process per CPU automatically, allowing me to take full advantage of the computing resources available.  Jobs are started asynchronously, and run in parallel on an available node.  The callable object returned when the job is submitted blocks until the response is ready, so response sets can be computed asynchronously, then merged synchronously.  Load distribution is transparent, making pp excellent for clustered environments.  """
        p = Paragraph()
        self.failUnless('\n' in p._wrap_lines(text))
        return

    def testCodeParagraph(self):
        text = """
<code=python>
import pp
job_server = pp.Server()
# Start tasks
f1 = job_server.submit(func1, args1, depfuncs1, 
    modules1)
f2 = job_server.submit(func1, args2, depfuncs1, 
    modules1)
f3 = job_server.submit(func2, args3, depfuncs2, 
    modules2)
# Retrieve the results
r1 = f1()
r2 = f2()
r3 = f3()  
</code>
"""
        p = CodeParagraph()
        self.failUnlessEqual(p._wrap_lines(text), text)
        return

    def testMarkupParagraphs(self):
        text = """When the pp worker starts, it detects the number of CPUs in the system and starts one process per CPU automatically, allowing me to take full advantage of the computing resources available.  Jobs are started asynchronously, and run in parallel on an available node.  The callable object returned when the job is submitted blocks until the response is ready, so response sets can be computed asynchronously, then merged synchronously.  Load distribution is transparent, making pp excellent for clustered environments.  """
        for p_type in [ TitleParagraph, ByLineParagraph, HeadingParagraph ]:
            p = p_type()
            self.failUnlessEqual(p._wrap_lines(text), text)
        return

    def testListParagraph(self):
        lines = [ '- item one',
                  '- item two',
                  '- item three is really long and might need to be wrapped except taht we do not wrap long list items',
                  '- item four',
                  ]
        p = ListParagraph()
        for line in lines:
            p.append(line)
        self.failUnlessEqual(p.as_string(include_markup=True, wrap_lines=True),
                             '\n'.join(lines))
        return

if __name__ == '__main__':
    unittest.main()
