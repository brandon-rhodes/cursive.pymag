# -*- encoding: utf-8 -*-

"""The Python Magazine formatting command."""

import re, sys

from docutils.nodes import GenericNodeVisitor, Text, paragraph
from docutils import core
from docutils.writers import Writer

textual_nodes = set([ 'block_quote', 'paragraph',
                      'list_item', 'term', 'definition_list_item', ])

mode_editor = False

listing_re_match = re.compile(ur'Listing *(\d+):*$').match

def die(message):
    print message
    sys.exit(1)

def get_text_within(node):
    """Returns, as plain text, the contents of the node.

    Raises an exception if the node contains children which are not
    simple text nodes.

    """
    t = u''
    for child in node.children:
        if isinstance(child, Text):
            t += child.astext()
        elif isinstance(child, paragraph):
            t += get_text_within(child) + '\n\n'
        else:
            die('I expected your %s node to contain only text,'
                'but instead it contains a %s node as a child.'
                % (node.__class__.__name__, child.__class__.__name__))
    del node.children[:]
    return t

class MyVisitor(GenericNodeVisitor):
    """A Visitor class; see the docutils for more details.

    """
    def __init__(self, *args, **kw):
        self.fragments = []
        self.masthead = True
        self.in_literal = False
        self.in_code = False
        self.external_listing = None
        self.related_links = []
        self.requires = None
        self.hide_paragraph = False
        GenericNodeVisitor.__init__(self, *args, **kw)

    def append(self, s):
        self.fragments.append(s)

    # The following method gives us protection from an author using an
    # node type for which we have not prepared either a processor or a
    # more specific error message.

    def default_visit(self, node):
        line = node.line
        if line is None:
            children = node.parent.children
            i = children.index(node)
            while i and (line is None):
                i -= 1
                line = children[i].line
                #import pdb;pdb.set_trace()
        print 'line %s: No support for node type "%s"' % (line, node.tagname)
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

    def visit_docinfo(self, node): pass

    def visit_author(self, node): self.append('=b=')
    def depart_author(self, node): self.append('=b=\n\n')

    def visit_field(self, node): pass

    def visit_field_name(self, node):
        text = get_text_within(node)
        self.field_name = text

    def visit_field_body(self, node):
        if self.field_name == 'Deck':
            self.append('=d=')
            self.in_special = True
        elif self.field_name == 'Requires':
            text = get_text_within(node)
            self.requires = text
        else:
            die('pymag does not support a field named "%s"'
                % (self.field_name,))

    def depart_field_body(self, node):
        if self.field_name == 'Deck':
            self.append('=d=\n\n')
            self.in_special = False

        del self.field_name

    def visit_Text(self, node):
        t = node.astext()
        if not self.in_literal:
            t = (t
                 .replace(u'\n',u' ')
                 .replace(u'//',ur'\//')
                 .replace(u'**',ur'\**')
                 .replace(u"''",ur"\''")
                 )

            # Make methods and functions automatically code
            t = re.sub(ur'(^| )([A-Za-z_.]+\(\))', ur"\1''\2''", t)

            # Insert a non-breakable space between "Listing", "Figure",
            # or "Python" and the number that follows.
            t = re.sub(ur'\bFigure (\d+)', ur'Figure \1', t)
            t = re.sub(ur'\bListing (\d+)', ur'Listing \1', t)
            t = re.sub(ur'\bPython (\d+)', ur'Python \1', t)

        if not self.in_code:
            t = (t
                 .replace(u'"',ur'\"')
                 .replace(u'“',ur'\"')
                 .replace(u'”',ur'\"')
                 )
        self.append(t)

    def visit_comment(self, node):
        """Throw out the text inside of comments."""
        del node.children[:]

    def visit_paragraph(self, node):
        if len(node.children) == 1:
            child = node.children[0]
            if isinstance(child, Text):
                text = child.astext()
                match = listing_re_match(text)
                if match:
                    self.hide_paragraph = True
                    self.external_listing = int(match.group(1))
                    del node.children[:]

    def depart_paragraph(self, node):
        if self.hide_paragraph:
            self.hide_paragraph = False
        else:
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

    def visit_bullet_list(self, node): self.bullet = '-'
    def visit_enumerated_list(self, node): self.bullet = '1.'
    def visit_list_item(self, node):
        b = self.bullet
        self.append(b + ' ')
        if b[0].isdigit():
            self.bullet = '%d.' % (int(b.strip('.')) + 1)

    def visit_literal_block(self, node):
        if self.external_listing:
            f = open('Listing%d.txt' % self.external_listing, 'w')
            listing = u''.join( n.astext() for n in node.children )
            f.write(listing.encode('utf-8'))
            f.close()
            del node.children[:]
        else:
            self.append_style('<code>\n')
            self.in_literal = True
            self.in_code = True

    def depart_literal_block(self, node):
        if self.external_listing:
            self.external_listing = None
        else:
            self.append('\n</code>\n\n')
            self.in_literal = False
            self.in_code = False

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
        page = ""
        if self.requires:
            page += ("Requirements:\n"
                     "\n"
                     "   %s"
                     % self.requires)
        if self.related_links:
            page += ("Useful/related URLs:\n"
                     "\n"
                     + '\n'.join("   %s - [[%s]]\n" % link
                                 for link in (self.related_links)))

        f.write(page.encode('utf-8'))
        f.close()

class MyWriter(Writer):
    """Boilerplate attaching our Visitor to a docutils document."""
    def translate(self):
        visitor = MyVisitor(self.document)
        self.document.walkabout(visitor)
        visitor.write()
        self.output = 'Done\n'

def command(argv=sys.argv[2:]):
    """Convert an RST document to Python Magazine Ceres markup.

    Creates a ``page.src.py`` file from an article.

    """
    core.publish_cmdline(writer=MyWriter(), argv=argv)
