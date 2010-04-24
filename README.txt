
Author tools for Python Magazine
================================

Python Magazine uses a special markup language, called Ceres, for
formatting articles that are submitted by authors and then worked on by
our editorial crew.  So that we can support Python folks who want to
write their documents in `reStructured Text`_ instead, this package adds
a ``pymag`` sub-command to the ``cursive`` command-line tool that
converts an article to Ceres, and while doing so reports any problems
with the article that might interfere with the magazine's layout.

To use the command, just type something like this::

    $ cursive pymag my_article.rst

Thanks to Doug Hellmann, there is also now a tool to go the other
direction, from Ceres to RST: the ``ceres2rst`` sub-command will take a
typical ``page.src.txt`` file and produce an RST equivalent.  Invoke it
like this::

    $ cursive ceres2rst page.src.txt

Report any bugs to the `project page`_ on Bitbucket.  This package builds
on the features of `cursive.tools`_.

.. _reStructured Text: http://docutils.sourceforge.net/rst.html
.. _project page: http://pypi.python.org/pypi/cursive.pymag/
.. _cursive.tools: http://pypi.python.org/pypi/cursive.tools/
