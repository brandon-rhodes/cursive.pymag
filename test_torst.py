#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2010 Doug Hellmann.  All rights reserved.
#
"""Tests for torst.py
"""

from cStringIO import StringIO

from cursive.pymag import ceres, torst

def test_convert_title():
    buffer = StringIO()
    p = ceres.TitleParagraph()
    p.append('=t=title=t=')
    c = torst.Converter('.')
    c.convert([p], buffer)
    text = buffer.getvalue()
    assert '=====\ntitle\n=====\n\n' == text, repr(text)
    return

def test_convert_heading():
    buffer = StringIO()
    p = ceres.HeadingParagraph()
    p.append('=h=heading=h=')
    c = torst.Converter('.')
    c.convert([p], buffer)
    text = buffer.getvalue()
    assert 'heading\n=======\n\n' == text, repr(text)
    return

def test_convert_deck():
    buffer = StringIO()
    p = ceres.DeckParagraph()
    p.append('=d=This is the deck.=d=')
    c = torst.Converter('.')
    c.convert([p], buffer)
    text = buffer.getvalue()
    assert '.. cssclass:: deck\n\n   This is the deck.\n\n' == text, repr(text)
    return

def test_fix_markup_italics():
    c = torst.Converter('.')
    text = c.fix_markup('word //markup// word')
    assert 'word *markup* word' == text, repr(text)
    return

def test_fix_markup_bold():
    c = torst.Converter('.')
    text = c.fix_markup('word **markup** word')
    assert 'word **markup** word' == text, repr(text)
    return

def test_fix_markup_literal():
    c = torst.Converter('.')
    text = c.fix_markup("word ''markup'' word")
    assert "word ``markup`` word" == text, repr(text)
    return

def test_fix_markup_url():
    c = torst.Converter('.')
    text = c.fix_markup("word [[markup]] word")
    assert "word markup word" == text, repr(text)
    return
