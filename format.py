"""The Python Magazine formatting command."""

"""The `cursive` command-line program itself."""

import sys

from docutils.nodes import GenericNodeVisitor
from docutils import core
from docutils.writers import Writer

textual_nodes = set([ 'block_quote', 'paragraph',
                      'list_item', 'term', 'definition_list_item', ])

class MyVisitor(GenericNodeVisitor):
    """A Visitor class; see the docutils for more details.

    """
    def __init__(self, *args, **kw):
        self.fragments = []
        self.masthead = True
        self.related_links = []
        GenericNodeVisitor.__init__(self, *args, **kw)

    def append(self, s):
        self.fragments.append(s)

    # The following method gives us protection from an author using an
    # node type for which we have not prepared either a processor or a
    # more specific error message.

    def default_visit(self, node):
        print "No support for node type:", node.tagname
        sys.exit(1)

    def default_departure(self, node):
        pass

    def visit_document(self, node):
        c = node.children
        if (len(c) < 2
            or c[0].tagname != 'title'
            or c[1].tagname != 'block_quote'):
            print ("Error: your document must start with a title, then"
                   " have a blockquote to provide your 'deck'")

    def visit_title(self, node):
        self.append('=t=' if self.masthead else '=h=')

    def depart_title(self, node):
        self.append('=t=' if self.masthead else '=h=')
        self.append('\n\n')
        self.masthead = False

    def visit_block_quote(self, node):
        self.append('=d=')

    def depart_block_quote(self, node):
        self.append('=d=\n\n')
        self.visit_block_quote = self.no_more_block_quotes

    def no_more_block_quotes(self, node):
        print "You can only have one block quote, to provide your deck."
        sys.exit(1)

    def visit_Text(self, node):
        self.append(node.astext().replace('\n', ' '))

    def visit_paragraph(self, node): pass
    def depart_paragraph(self, node): self.append('\n\n')

    def visit_emphasis(self, node): self.append('//')
    def depart_emphasis(self, node): self.append('//')

    def visit_strong(self, node): self.append('**')
    def depart_strong(self, node): self.append('**')

    def visit_bullet_list(self, node): pass
    def visit_list_item(self, node): self.append('- ')

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

""" + '\n'.join("   %s - %s\n" % link for link in (self.related_links))

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
