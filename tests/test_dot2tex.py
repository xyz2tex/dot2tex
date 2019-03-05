#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

import dot2tex
import re
from dot2tex.dot2tex import smart_float

testgraph = """
digraph G {
    a_1-> a_2 -> a_3 -> a_1;
}
"""


class InterfaceTest(unittest.TestCase):
    def test_default(self):
        source = dot2tex.dot2tex(testgraph)
        self.assertTrue(source.strip())

    def test_pgf(self):
        source = dot2tex.dot2tex(testgraph, format='pgf')
        self.assertTrue(source.strip())

    def test_pstricks(self):
        source = dot2tex.dot2tex(testgraph, format='pst')
        self.assertTrue(source.strip())

    def test_tikz(self):
        source = dot2tex.dot2tex(testgraph, format='tikz')
        self.assertTrue(source.strip())

    def test_positions(self):
        positions = dot2tex.dot2tex(testgraph, format='positions')
        self.assertEqual(type(positions), dict)
        self.assertTrue('a_1' in positions.keys())
        self.assertEqual(len(positions.keys()), 3)
        self.assertEqual(len(positions['a_1']), 2)


class UnicodeTest(unittest.TestCase):
    def test_russian(self):
        testgraph = """digraph {AAA [label="ЯЯЯ"];}"""
        source = dot2tex.dot2tex(testgraph, debug=True, format='tikz', codeonly=True)
        self.assertTrue(source.find("{ЯЯЯ}") > 0, "Found %s" % source)

    def test_russian2(self):
        testgraph = """digraph {AAA [label=aaЯЯЯ];}"""
        source = dot2tex.dot2tex(testgraph, debug=True, format='tikz', codeonly=True)
        self.assertTrue(source.find("{aaЯЯЯ}") > 0, "Found %s" % source)


class D2TOptionsTest(unittest.TestCase):
    def test_d2tcommented(self):
        testgraph = """
digraph SSA
{
        //d2toptions = "--graphstyle=insertedstyle";
 B
}
"""
        source = dot2tex.dot2tex(testgraph, debug=True)
        self.assertFalse(source.find("insertedstyle") >= 0)

    def test_d2toptions(self):
        testgraph = """
digraph SSA
{
        d2toptions = "--graphstyle=insertedstyle";
 B
}
"""
        source = dot2tex.dot2tex(testgraph, debug=True)
        self.assertTrue(source.find("insertedstyle") >= 0)


class PGF118CompatibilityTest(unittest.TestCase):
    def test_pgf118option(self):
        source = dot2tex.dot2tex(testgraph, debug=True, pgf118=True)
        self.assertTrue(source.find("\\usepackage{pgflibrarysnakes}") >= 0)
        self.assertFalse(source.find("\\usetikzlibrary") >= 0)
        self.assertFalse(source.find("line join=bevel") >= 0)

    def test_tikz118option(self):
        source = dot2tex.dot2tex(testgraph, debug=True, format='tikz', pgf118=True)
        self.assertTrue(source.find("\\usepackage{pgflibrarysnakes}") >= 0)
        self.assertFalse(source.find("\\usetikzlibrary") >= 0)
        self.assertFalse(source.find("line join=bevel") >= 0)

    def test_nopgf118option(self):
        source = dot2tex.dot2tex(testgraph, debug=True, pgf118=False)
        self.assertFalse(source.find("\\usepackage{pgflibrarysnakes}") >= 0)
        self.assertTrue(source.find("\\usetikzlibrary") >= 0)
        self.assertTrue(source.find("line join=bevel") >= 0)


class BuggyGraphTests(unittest.TestCase):
    def test_small_label(self):
        testgraph = """
        digraph {
            "objects" [label="sdfsdf", texlbl="$1$"];
        }
        """
        source = dot2tex.dot2tex(testgraph, debug=True, autosize=True,
                                 figonly=True, format='tikz')
        self.assertTrue('$1$' in source)

    # http://code.google.com/p/dot2tex/issues/detail?id=16
    def test_name_with_parantheses(self):
        testgraph = """
        digraph { { "F(K)/R-1"}}
        """
        source = dot2tex.dot2tex(testgraph, debug=True,
                                 figonly=True, format='tikz')
        self.assertTrue(r'\node (F{K}/R-1)' in source)


class NeedsQuotesTests(unittest.TestCase):
    # http://code.google.com/p/dot2tex/issues/detail?id=17    
    def test_numeral(self):
        from dot2tex import dotparsing

        self.assertTrue(dotparsing.needs_quotes('1.2.3.4'))
        self.assertFalse(dotparsing.needs_quotes('1.2'))
        self.assertFalse(dotparsing.needs_quotes('-1.2'))
        self.assertFalse(dotparsing.needs_quotes('-1'))
        self.assertTrue(dotparsing.needs_quotes('--1'))
        self.assertFalse(dotparsing.needs_quotes('.12'))
        self.assertFalse(dotparsing.needs_quotes('-.1'))

    # http://code.google.com/p/dot2tex/issues/detail?id=17    
    def test_not_numeral_in_label(self):
        testgraph = """
        digraph { a[label="1.2.3.4"] ; b }
        """
        source = dot2tex.dot2tex(testgraph, debug=True,
                                 figonly=True, format='tikz', autosize=True)
        self.assertTrue(r'{1.2.3.4}' in source)


class MultipleStatements(unittest.TestCase):
    # https://github.com/kjellmf/dot2tex/issues/5
    def test_semicolon(self):
        """Test for issue 5"""
        testgraph1 = """
        digraph example {
          a -> b
          a -> c
          {rank=same; b;c}
        }"""
        testgraph2 = """
        digraph example {
          a -> b;
          a -> c;
          {rank=same; b;c}
        }"""
        source1 = dot2tex.dot2tex(testgraph1,
                                  figonly=True, format='tikz', autosize=True)
        source2 = dot2tex.dot2tex(testgraph2,
                                  figonly=True, format='tikz', autosize=True)
        self.assertEqual(source1, source2)


class TestPositionsOutputFormat(unittest.TestCase):
    # http://code.google.com/p/dot2tex/issues/detail?id=20
    def test_floating_point_coordinates(self):
        testxdotgraph = r"""
        digraph G {
            node [label="\N"];
            graph [bb="0,0,127.21,49.639",
                    _draw_="c 9 -#ffffffff C 9 -#ffffffff P 4 0 -1 0 50 128 50 128 -1 ",
                    xdotversion="1.2"];
            a [pos="28,30.139", width="0.75", height="0.51389", _draw_="c 9 -#000000ff e 28 30 27 18 ", _ldraw_="F 14.000000 11 -Times-Roman c 9 -#000000ff T 28 25 0 9 1 -a "];
            b [pos="99.21,19.5", width="0.75", height="0.51389", _draw_="c 9 -#000000ff e 99 20 27 18 ", _ldraw_="F 14.000000 11 -Times-Roman c 9 -#000000ff T 99 15 0 9 1 -b "];
            a -> b [pos="e,72.434,23.5 54.516,26.177 57.076,25.795 59.704,25.402 62.341,25.008", _draw_="c 9 -#000000ff B 4 55 26 57 26 60 25 62 25 ", _hdraw_="S 5 -solid c 9 -#000000ff C 9 -#000000ff P 3 63 28 72 24 62 22 "];
        }
        """
        positions = dot2tex.dot2tex(testxdotgraph, format='positions')
        self.assertEqual(type(positions), dict)
        self.assertEqual(type(positions['a'][0]), float)
        self.assertEqual(type(positions['b'][0]), float)


class ErrorHandlingTest(unittest.TestCase):
    def test_parse_error(self):
        graph = "graph {a-b]"
        parser = dot2tex.dotparsing.DotDataParser()
        self.assertRaises(dot2tex.ParseException, parser.parse_dot_data, graph)

    def test_module_parse_error(self):
        graph = "graph {a-b]"
        self.assertRaises(dot2tex.ParseException, dot2tex.dot2tex, graph)

    def test_no_input_file(self):
        graph = r"\input{dymmy.dot}"
        self.assertRaises(IOError, dot2tex.dot2tex, graph)


class EdgeLabelsTests(unittest.TestCase):
    def test_edgetexlbl_nolabel_preproc(self):
        """Edge labels specified using 'texlbl' should be included when preprocessing the graph"""
        graph = r'digraph G {a -> b [texlbl="TestLabel"];}'
        code = dot2tex.dot2tex(graph, autosize=True)
        self.assertTrue("TestLabel" in code)

    def test_edgetexlbl_nolabel_nopreproc(self):
        """Edge labels specified using 'texlbl' only will not be generated by Graphviz"""
        graph = r'digraph G {a -> b [texlbl="TestLabel"];}'
        code = dot2tex.dot2tex(graph)
        self.assertTrue("TestLabel" not in code)


class GraphvizInterfaceTests(unittest.TestCase):
    def test_prog_options(self):
        from dot2tex.dot2tex import create_xdot

        xdot_data = create_xdot(testgraph)
        xdot_data2 = create_xdot(testgraph)
        self.assertEqual(xdot_data, xdot_data2)
        xdot_data2 = create_xdot(testgraph, options='-y')
        self.assertNotEqual(xdot_data, xdot_data2, 'No options were passed to dot')


    def test_invalid_program(self):
        """Invoking create_xdot with an invalid prog parameter should raise an exception"""
        from dot2tex.dot2tex import create_xdot
        # xdot_data = create_xdot(testgraph, prog="dummy")
        self.assertRaises(NameError, create_xdot, testgraph, prog="dummy")


class AutosizeTests(unittest.TestCase):
    def test__dim_extraction(self):
        """Failed to extract dimension data from logfile"""
        from dot2tex.dot2tex import dimext

        logdata = r"""
ABD: EveryShipout initializing macros
Preview: Fontsize 10pt
! Preview: Snippet 1 started.
<-><->
      
l.18 \begin{preview}
                    %
Not a real error.

! Preview: Snippet 1 ended.(817330+0x1077278).
<-><->
      
l.20 \end{preview}
                  %
Not a real error.

[1]
! Preview: Snippet 2 started.
<-><->
      
l.21 \begin{preview}
                    %
Not a real error.

! Preview: Snippet 2 ended.(817330+0x1077278).
<-><->
      
l.23 \end{preview}
                  %
Not a real error.

[2]
! Preview: Snippet 3 started.
<-><->
      
l.24 \begin{preview}
                    %
Not a real error.

! Preview: Snippet 3 ended.(817330+0x1077278).
<-><->
      
l.26 \end{preview}
                  %
Not a real error.

[3] ) 
Here is how much of TeX's memory you used:
"""
        dimext_re = re.compile(dimext, re.MULTILINE | re.VERBOSE)
        texdimdata = dimext_re.findall(logdata)
        self.assertNotEqual(len(texdimdata), 0)

    def test__dim_extraction_cygwin(self):
        """Failed to extract dimension data from logfile generated under Cygwin"""
        # issue [14] http://code.google.com/p/dot2tex/issues/detail?id=14
        from dot2tex.dot2tex import dimext

        logdata = r"""
Preview: Fontsize 10pt
/tmp/dot2texS8qrUI/dot2tex.tex:18: Preview: Snippet 1 started.
<-><->
      
l.18 \begin{preview}
                    %
Not a real error.

/tmp/dot2texS8qrUI/dot2tex.tex:20: Preview: Snippet 1 ended.(817330+0x1077278).

<-><->
      
l.20 \end{preview}
                  %
Not a real error.

[1]
/tmp/dot2texS8qrUI/dot2tex.tex:21: Preview: Snippet 2 started.
<-><->
      
l.21 \begin{preview}
                    %
Not a real error.

/tmp/dot2texS8qrUI/dot2tex.tex:23: Preview: Snippet 2 ended.(817330+0x1077278).

<-><->
      
l.23 \end{preview}
                  %
Not a real error.

[2]
/tmp/dot2texS8qrUI/dot2tex.tex:24: Preview: Snippet 3 started.
<-><->
      
l.24 \begin{preview}
                    %
Not a real error.

/tmp/dot2texS8qrUI/dot2tex.tex:26: Preview: Snippet 3 ended.(817330+0x1077278).

<-><->
      
l.26 \end{preview}
                  %
Not a real error.

[3] ) 
Here is how much of TeX's memory you used:
"""
        dimext_re = re.compile(dimext, re.MULTILINE | re.VERBOSE)
        texdimdata = dimext_re.findall(logdata)
        self.assertNotEqual(len(texdimdata), 0)


class TikZTemplateTests(unittest.TestCase):
    def test_point_shape(self):
        """Nodes with the point shape should not have labels"""
        testgraph = r"""
        digraph G {
            {
                node[shape=point]
                a-> b-> c -> a;
            }
            e -> a;
            a [label="dummy"]
        }
        """
        code = dot2tex.dot2tex(testgraph, format="tikz")
        self.assertFalse("dummy" in code)


class TestBugs(unittest.TestCase):
    def test_styleonly_tikz_preproc(self):
        """Test for a bug in get_node_preproc_code. Used to raise a TypeError"""
        code = dot2tex.dot2tex(testgraph, format="tikz", preproc=True, styleonly=True)

    # https://github.com/kjellmf/dot2tex/issues/12
    def test_head_and_tail_labels(self):
        """Test for issue 12"""
        graph = "digraph { a -> b [headlabel=HEADLABEL,taillabel=TAILLABEL,label=LABEL] }"
        code = dot2tex.dot2tex(graph, format="pgf", autosize=True)
        self.assertTrue('HEADLABEL' in code)
        self.assertTrue('LABEL' in code)
        self.assertTrue('TAILLABEL' in code)


class TestNumberFormatting(unittest.TestCase):
    def test_numbers(self):
        self.assertEqual("2.0", smart_float(2))
        self.assertEqual("0.0001", smart_float(1e-4))

    def test_decimal_places(self):
        self.assertEqual("2.1", smart_float(2.1))
        self.assertEqual("2.11119", smart_float(2.11119))
        self.assertEqual("2.1", smart_float(2.100))
        self.assertEqual("10000000000000000.0000", smart_float(1e16))


class PGF210CompatibilityTest(unittest.TestCase):
    def test_pgf210option(self):
        source = dot2tex.dot2tex(testgraph, debug=True, pgf210=True)
        self.assertTrue(source.find("dot2tex template for PGF 2.10") >= 0)
        # self.assertFalse(source.find("\usetikzlibrary") >= 0)
        # self.assertFalse(source.find("line join=bevel") >= 0)

    def test_tikz210option(self):
        source = dot2tex.dot2tex(testgraph, debug=True, format='tikz', pgf210=True)
        self.assertTrue(source.find("dot2tex template for PGF 2.10") >= 0)
        # self.assertFalse(source.find("\usetikzlibrary") >= 0)
        # self.assertFalse(source.find("line join=bevel") >= 0)
        #
        # def test_nopgf210option(self):
        # source = dot2tex.dot2tex(testgraph, debug=True, pgf210=False)
        # self.assertFalse(source.find("\usepackage{pgflibrarysnakes}") >= 0)
        #     self.assertTrue(source.find("\usetikzlibrary") >= 0)
        #     self.assertTrue(source.find("line join=bevel") >= 0)


class HeadAndTailLabelTest(unittest.TestCase):
    """Tests for https://github.com/kjellmf/dot2tex/issues/12"""
    test_graph = r"digraph { a -> b [headlabel=HEADLABEL,taillabel=TAILLABEL,label=LABEL] }"

    def test_head_label_pgf(self):
        source = dot2tex.dot2tex(self.test_graph, autosize=True, format="pgf")
        self.assertTrue("HEADLABEL" in source)

    def test_head_label_tikz(self):
        source = dot2tex.dot2tex(self.test_graph, autosize=True, format="tikz")
        self.assertTrue("HEADLABEL" in source)

    def test_head_label_pstricks(self):
        source = dot2tex.dot2tex(self.test_graph, autosize=True, format="pstricks")
        self.assertTrue("HEADLABEL" in source)

    def test_tail_label_pgf(self):
        source = dot2tex.dot2tex(self.test_graph, autosize=True, format="pgf")
        self.assertTrue("TAILLABEL" in source)

    def test_tail_label_tikz(self):
        source = dot2tex.dot2tex(self.test_graph, autosize=True, format="tikz")
        self.assertTrue("TAILLABEL" in source)

    def test_tail_label_pstricks(self):
        source = dot2tex.dot2tex(self.test_graph, autosize=True, format="pstricks")
        self.assertTrue("TAILLABEL" in source)

    def test_head_label_pgf_duplicate(self):
        source = dot2tex.dot2tex(self.test_graph, autosize=True, format="pgf", duplicate=True)
        self.assertTrue("HEADLABEL" in source)

    def test_head_label_tikz_duplicate(self):
        source = dot2tex.dot2tex(self.test_graph, autosize=True, format="tikz", duplicate=True)
        self.assertTrue("HEADLABEL" in source)

    def test_head_label_pstricks_duplicate(self):
        source = dot2tex.dot2tex(self.test_graph, autosize=True, format="pstricks", duplicate=True)
        self.assertTrue("HEADLABEL" in source)

    def test_tail_label_pgf_duplicate(self):
        source = dot2tex.dot2tex(self.test_graph, autosize=True, format="pgf", duplicate=True)
        self.assertTrue("TAILLABEL" in source)

    def test_tail_label_tikz_duplicate(self):
        source = dot2tex.dot2tex(self.test_graph, autosize=True, format="tikz", duplicate=True)
        self.assertTrue("TAILLABEL" in source)

    def test_tail_label_pstricks_duplicate(self):
        source = dot2tex.dot2tex(self.test_graph, autosize=True, format="pstricks", duplicate=True)
        self.assertTrue("TAILLABEL" in source)


class IncludeTest(unittest.TestCase):
    """Tests for issue #28 https://github.com/kjellmf/dot2tex/issues/28"""

    def test_include_1(self):
        test_graph = r"""

    \input{dummyfilename.dot}

    """""
        self.assertRaises(IOError, dot2tex.dot2tex, test_graph)

    def test_include_2(self):
        test_graph = r"""

    \input{dummyfilename.dot} % comment

    """""
        self.assertRaises(IOError, dot2tex.dot2tex, test_graph)

    def test_include_3(self):
        test_graph = r"""


    \input{dummyfilename.dot} // comment

    """""
        self.assertRaises(IOError, dot2tex.dot2tex, test_graph)

    def test_include_4(self):
        test_graph = r"""


    digraph {
            "objects" [label="sdfsdf", texlbl="\input{dymmyfilename.dot}"];
        }

    """""
        try:
            code = dot2tex.dot2tex(test_graph)
        except IOError:
            self.fail("Tried to load external dot file")


class Issue23Tests(unittest.TestCase):
    # https://github.com/kjellmf/dot2tex/issues/23

    def test_multi_line_preamble(self):
        test_graph = r"""
        digraph
            {
              d2tdocpreamble = "
              % My preamble
              \usepackage{amssymb}";
              {
                A -> B -> C;
              }
            }
        """
        code = dot2tex.dot2tex(test_graph, format="tikz")
        self.assertTrue(r"% My preamble" in code)

    def test_single_line_preamble(self):
        test_graph = r"""
        digraph
            {
              d2tdocpreamble = "\usepackage{amssymb}  \usetikzlibrary{arrows, automata}";
              {
                A -> B -> C;
              }
            }
        """
        code = dot2tex.dot2tex(test_graph, format="tikz")
        self.assertTrue(r"\usetikzlibrary{arrows, automata}" in code)


if __name__ == '__main__':
    unittest.main()
