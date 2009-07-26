# -*- encoding: utf-8 -*-

"""The Python Magazine formatting command."""

import re, sys

from docutils.nodes import GenericNodeVisitor, Text
from docutils import core
from docutils.writers import Writer

textual_nodes = set([ 'block_quote', 'paragraph',
                      'list_item', 'term', 'definition_list_item', ])

mode_editor = False

listing_re_match = re.compile(r'Listing *(\d+)').match

class MyVisitor(GenericNodeVisitor):
    """A Visitor class; see the docutils for more details.

    """
    def __init__(self, *args, **kw):
        self.fragments = []
        self.masthead = True
        self.in_literal = False
        self.external_listing = None
        self.related_links = []
        GenericNodeVisitor.__init__(self, *args, **kw)

    def append(self, s):
        self.fragments.append(s)

    # The following method gives us protection from an author using an
    # node type for which we have not prepared either a processor or a
    # more specific error message.

    def default_visit(self, node):
        print repr(node)
        print dir(node)
        print 'line %s: No support for node type "%s"' % (
            node.line, node.tagname)
        sys.exit(1)

    def default_departure(self, node):
        pass

    def visit_document(self, node):
        c = node.children
        if (mode_editor and (
                len(c) < 2
                or c[0].tagname != 'title'
                or c[1].tagname != 'block_quote'
                )):
            print ("Error: your document must start with a title, then"
                   " have a blockquote to provide your 'deck'")

    def visit_section(self, node):
        pass

    def visit_title(self, node):
        self.append('=t=' if self.masthead else '=h=')
        self.in_special = True

    def depart_title(self, node):
        self.append('=t=' if self.masthead else '=h=')
        self.append('\n\n')
        self.masthead = False
        self.in_special = False

    def visit_block_quote(self, node):
        self.append('=d=')
        self.in_special = True

    def depart_block_quote(self, node):
        self.append('=d=\n\n')
        self.in_special = False
        self.visit_block_quote = self.no_more_block_quotes

    def no_more_block_quotes(self, node):
        print "You can only have one block quote, to provide your deck."
        sys.exit(1)

    def visit_Text(self, node):
        t = node.astext()
        if not self.in_literal:
            t = (t.replace(u'\n',u' ')
                 .replace(u'//',ur'\//')
                 .replace(u'**',ur'\**')
                 .replace(u"''",ur"\''"))
            # Make methods and functions automatically code
            t = re.sub(ur'(^| )([A-Za-z_.]+\(\))', ur"\1''\2''", t)
        self.append(t
                    .replace(u'"',ur'\"')
                    .replace(u'“',ur'\"')
                    .replace(u'”',ur'\"'))

    def visit_paragraph(self, node):
        if len(node.children) == 1:
            child = node.children[0]
            if isinstance(child, Text):
                text = child.astext()
                match = listing_re_match(text)
                if match:
                    self.external_listing = int(match.group(1))
                    del node.children[:]

    def depart_paragraph(self, node):
        self.append('\n\n')

    def append_style(self, s):
        """Append the given style tag, if not inside a title or dock."""
        if not self.in_special:
            self.append(s)

    def visit_emphasis(self, node): self.append_style('//')
    def depart_emphasis(self, node): self.append_style('//')

    def visit_strong(self, node): self.append_style('**')
    def depart_strong(self, node): self.append_style('**')

    def visit_literal(self, node):
        self.append_style("''")
        self.in_literal = True

    def depart_literal(self, node):
        self.append_style("''")
        self.in_literal = False

    def visit_title_reference(self, node): self.append_style("''")
    def depart_title_reference(self, node): self.append_style("''")

    def visit_bullet_list(self, node): pass
    def visit_list_item(self, node): self.append('- ')

    def visit_literal_block(self, node):
        if self.external_listing:
            f = open('Listing%d.txt' % self.external_listing, 'w')
            f.write(''.join( n.astext() for n in node.children ))
            f.close()
            del node.children[:]
        else:
            self.append_style('<code>\n')
            self.in_literal = True

    def depart_literal_block(self, node):
        if self.external_listing:
            self.external_listing = None
        else:
            self.append('\n</code>\n\n')
            self.in_literal = False

    def visit_target(self, node):
        """Targets get put inside the references file."""
        title = node.rawsource.split('_', 1)[1].split(':')[0]
        url = node.attributes['refuri']
        self.related_links.append((title, url))

    def visit_reference(self, node): pass

    def write(self):
        f = open('page.src.txt', 'w')
        page = ''.join(self.fragments)
        f.write(page.encode('utf-8'))
        f.close()

        f = open('requirements.txt', 'w')
        page = """Requirements:

   Python 2.? or 3.?

"""
        if self.related_links:
            page += """Related links:

""" + '\n'.join("   %s - [[%s]]\n" % link for link in (self.related_links))

        f.write(page.encode('utf-8'))
        f.close()

class MyWriter(Writer):
    """Boilerplate attaching our Visitor to a docutils document."""
    def translate(self):
        visitor = MyVisitor(self.document)
        self.document.walkabout(visitor)
        visitor.write()
        self.output = 'Done\n'

def console_script_cursive_pymag():
    """Command-line script converting an RST document to Ceres markup."""
    core.publish_cmdline(writer=MyWriter())
