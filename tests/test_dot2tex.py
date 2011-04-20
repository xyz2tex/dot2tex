# -*- coding: utf-8 -*-
import unittest

import dot2tex

testgraph = """
digraph G {
    a_1-> a_2 -> a_3 -> a_1;
}
"""

class InterfaceTest(unittest.TestCase):
    def test_default(self):
        source = dot2tex.dot2tex(testgraph)
        self.failUnless(source.strip())
        
    def test_pgf(self):
        source = dot2tex.dot2tex(testgraph,format='pgf')
        self.failUnless(source.strip())
        
    def test_pstricks(self):
        source = dot2tex.dot2tex(testgraph,format='pst')
        self.failUnless(source.strip())
        
    def test_tikz(self):
        source = dot2tex.dot2tex(testgraph,format='tikz')
        self.failUnless(source.strip())
        
    def test_positions(self):
        positions = dot2tex.dot2tex(testgraph, format='positions')
        self.failUnless(type(positions)==dict)
        self.failUnless('a_1' in positions.keys())
        self.failUnless(len(positions.keys())==3)
        self.failUnless(len(positions['a_1'])==2)
                                      
    def test_debug(self):
        """Is StringIO logging working?"""
        source = dot2tex.dot2tex(testgraph,debug=True)
        self.failUnless(dot2tex.get_logstream().getvalue().strip())



class UnicodeTest(unittest.TestCase):
    def test_russian(self):
        testgraph = """digraph {AAA [label="ЯЯЯ"];}"""
        source = dot2tex.dot2tex(testgraph,debug=True,format='tikz',codeonly=True)
        self.failUnless(source.find("{ЯЯЯ}") > 0,"Found %s" % source)
    def test_russian2(self):
        testgraph = """digraph {AAA [label=aaЯЯЯ];}"""
        source = dot2tex.dot2tex(testgraph,debug=True,format='tikz',codeonly=True)
        self.failUnless(source.find("{aaЯЯЯ}") > 0,"Found %s" % source)
    

class D2TOptionsTest(unittest.TestCase):
    def test_d2tcommented(self):
        testgraph = """
digraph SSA
{
        //d2toptions = "--graphstyle=insertedstyle";
 B
}
"""
        source = dot2tex.dot2tex(testgraph,debug=True)
        self.failIf(source.find("insertedstyle") >= 0)

    def test_d2toptions(self):
        testgraph = """
digraph SSA
{
        d2toptions = "--graphstyle=insertedstyle";
 B
}
"""
        source = dot2tex.dot2tex(testgraph,debug=True)
        self.failUnless(source.find("insertedstyle") >= 0)

class PGF118CompatabilityTest(unittest.TestCase):
    
    def test_pgf118option(self):
        source = dot2tex.dot2tex(testgraph,debug=True, pgf118=True)
        self.failUnless(source.find("\usepackage{pgflibrarysnakes}") >= 0)
        self.failIf(source.find("\usetikzlibrary") >= 0)
        self.failIf(source.find("line join=bevel") >= 0)

    def test_tikz118option(self):
        source = dot2tex.dot2tex(testgraph,debug=True, format='tikz', pgf118=True)
        self.failUnless(source.find("\usepackage{pgflibrarysnakes}") >= 0)
        self.failIf(source.find("\usetikzlibrary") >= 0)
        self.failIf(source.find("line join=bevel") >= 0)
        
    def test_nopgf118option(self):
        source = dot2tex.dot2tex(testgraph,debug=True, pgf118=False)
        self.failIf(source.find("\usepackage{pgflibrarysnakes}") >= 0)
        self.failUnless(source.find("\usetikzlibrary") >= 0)
        self.failUnless(source.find("line join=bevel") >= 0)

class BuggyGraphTests(unittest.TestCase):
    
    def test_small_label(self):
        testgraph = """
        digraph {
            "objects" [label="sdfsdf", texlbl="$1$"];
        }
        """
        source = dot2tex.dot2tex(testgraph, debug=True, autosize=True,
                                 figonly=True, format='tikz')
        self.failUnless('$1$' in source)
    
    #http://code.google.com/p/dot2tex/issues/detail?id=16
    def test_name_with_parantheses(self):
        testgraph = """
        digraph { { "F(K)/R-1"}}
        """
        source = dot2tex.dot2tex(testgraph, debug=True,
                                 figonly=True, format='tikz')
        self.failUnless(r'\node (F{K}/R-1)' in source)
    
class NeedsQuotesTests(unittest.TestCase):
    # http://code.google.com/p/dot2tex/issues/detail?id=17    
    def test_numeral(self):
        from dot2tex import dotparsing
        self.failUnless(dotparsing.needs_quotes('1.2.3.4') == True)
        self.failUnless(dotparsing.needs_quotes('1.2') == False)
        self.failUnless(dotparsing.needs_quotes('-1.2') == False)
        self.failUnless(dotparsing.needs_quotes('-1') == False)
        self.failUnless(dotparsing.needs_quotes('--1') == True)
        self.failUnless(dotparsing.needs_quotes('.12') == False)
        self.failUnless(dotparsing.needs_quotes('-.1') == False)
    
    # http://code.google.com/p/dot2tex/issues/detail?id=17    
    def test_not_numeral_in_label(self):
        testgraph = """
        digraph { a[label="1.2.3.4"] ; b }
        """
        source = dot2tex.dot2tex(testgraph, debug=True,
                                 figonly=True, format='tikz', autosize=True)
        self.failUnless(r'{1.2.3.4}' in source)
    

if __name__ == '__main__':
    unittest.main()
    #import unicodedata
    #dd = u'Я'
    #print dd
    #print unicodedata.numeric(dd[0])

    #print ord(u'Я')