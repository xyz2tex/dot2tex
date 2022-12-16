#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from pyparsing import ParseException

import dot2tex
import re
from dot2tex.utils import smart_float, is_multiline_label

testgraph = """
digraph G {
    a_1-> a_2 -> a_3 -> a_1;
}
"""


class mobj(object):
    def __init__(self, d):
        self.__dict__ = d


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
        from dot2tex.base import create_xdot

        xdot_data = create_xdot(testgraph)
        xdot_data2 = create_xdot(testgraph)
        self.assertEqual(xdot_data, xdot_data2)
        xdot_data2 = create_xdot(testgraph, options='-y')
        self.assertNotEqual(xdot_data, xdot_data2, 'No options were passed to dot')

    def test_invalid_program(self):
        """Invoking create_xdot with an invalid prog parameter should raise an exception"""
        from dot2tex.base import create_xdot
        # xdot_data = create_xdot(testgraph, prog="dummy")
        self.assertRaises(NameError, create_xdot, testgraph, prog="dummy")


class AutosizeTests(unittest.TestCase):
    def test__dim_extraction(self):
        """Failed to extract dimension data from logfile"""
        from dot2tex.base import dimext

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
        from dot2tex.base import dimext

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
    
    # https://github.com/kjellmf/dot2tex/issues/92
    def test_newline_in_num_list(self):
        """Test for issue 92, newlines in number lists cause `ValueError`s in smart_float"""        
        graph = 'strict digraph "" {\n\tgraph [bb="0,0,945,1116"];\n\tnode [label="\\N"];\n\t0\t[height=0.5,\n\t\tpos="99,1026",\n\t\twidth=0.75];\n\t16\t[height=0.5,\n\t\tpos="94,954",\n\t\twidth=0.75];\n\t0 -> 16\t[pos="e,95.222,972.1 97.764,1007.7 97.213,999.98 96.551,990.71 95.937,982.11"];\n\t1\t[height=0.5,\n\t\tpos="144,882",\n\t\twidth=0.75];\n\t16 -> 1\t[pos="e,132.93,898.49 105.1,937.46 111.51,928.49 119.7,917.02 126.92,906.92"];\n\t17\t[height=0.5,\n\t\tpos="144,810",\n\t\twidth=0.75];\n\t1 -> 17\t[pos="e,144,828.1 144,863.7 144,855.98 144,846.71 144,838.11"];\n\t3\t[height=0.5,\n\t\tpos="369,738",\n\t\twidth=0.75];\n\t17 -> 3\t[pos="e,345.09,746.44 168.08,801.51 208.34,788.98 289.42,763.76 335.32,749.48"];\n\t18\t[height=0.5,\n\t\tpos="551,666",\n\t\twidth=0.75];\n\t3 -> 18\t[pos="e,528.14,675.79 392.05,728.13 424.05,715.83 482.1,693.5 518.49,679.51"];\n\t29\t[height=0.5,\n\t\tpos="550,522",\n\t\twidth=0.75];\n\t3 -> 29\t[pos="e,537.29,538.03 381.73,721.95 412.95,685.04 493.48,589.82 530.66,545.86"];\n\t55\t[height=0.5,\n\t\tpos="292,522",\n\t\twidth=0.75];\n\t3 -> 55\t[pos="e,298.01,539.71 362.96,720.21 349.6,683.09 317.5,593.86 301.45,549.27"];\n\t2\t[height=0.5,\n\t\tpos="204,378",\n\t\twidth=0.75];\n\t2 -> 16\t[pos="e,93.012,935.96 184.49,390.77 151.68,412.22 89,461.04 89,521 89,811 89,811 89,811 89,851.03 91.009,897.37 92.48,925.93"];\n\t5\t[height=0.5,\n\t\tpos="551,594",\n\t\twidth=0.75];\n\t18 -> 5\t[pos="e,551,612.1 551,647.7 551,639.98 551,630.71 551,622.11"];\n\t28\t[height=0.5,\n\t\tpos="808,450",\n\t\twidth=0.75];\n\t29 -> 28\t[pos="e,783.34,457.69 574.74,514.29 620.97,501.74 720.57,474.72 773.42,460.38"];\n\t57\t[height=0.5,\n\t\tpos="550,450",\n\t\twidth=0.75];\n\t29 -> 57\t[pos="e,550,468.1 550,503.7 550,495.98 550,486.71 550,478.11"];\n\t25\t[height=0.5,\n\t\tpos="264,450",\n\t\twidth=0.75];\n\t55 -> 25\t[pos="e,270.59,467.47 285.36,504.41 282.09,496.22 278.06,486.14 274.38,476.95"];\n\t26\t[height=0.5,\n\t\tpos="350,450",\n\t\twidth=0.75];\n\t55 -> 26\t[pos="e,337.44,466.16 304.59,505.81 312.26,496.55 322.23,484.52 330.86,474.09"];\n\t5 -> 29\t[pos="e,550.24,540.1 550.75,575.7 550.64,567.98 550.51,558.71 550.39,550.11"];\n\t19\t[height=0.5,\n\t\tpos="660,522",\n\t\twidth=0.75];\n\t5 -> 19\t[pos="e,641.23,535.05 569.99,580.81 587.34,569.67 613.19,553.06 632.74,540.5"];\n\t21\t[height=0.5,\n\t\tpos="660,378",\n\t\twidth=0.75];\n\t5 -> 21\t[pos="e,647.84,394.57 562.79,577.38 570.15,567.13 579.43,553.23 586,540 608.63,494.43 601.07,477.42 624,432 629.04,422.02 635.67,411.71 \\\r\n\\\n641.86,402.86"];\n\t56\t[height=0.5,\n\t\tpos="364,522",\n\t\twidth=0.75];\n\t5 -> 56\t[pos="e,387.12,531.65 528.07,584.42 495.12,572.08 434.23,549.29 396.61,535.21"];\n\t49\t[height=0.5,\n\t\tpos="808,378",\n\t\twidth=0.75];\n\t28 -> 49\t[pos="e,802.12,395.96 802.16,432.41 801.3,424.51 801.05,414.85 801.41,405.94"];\n\t25 -> 2\t[pos="e,216.99,394.16 250.98,433.81 242.96,424.45 232.53,412.28 223.53,401.79"];\n\t12\t[height=0.5,\n\t\tpos="350,378",\n\t\twidth=0.75];\n\t26 -> 12\t[pos="e,350,396.1 350,431.7 350,423.98 350,414.71 350,406.11"];\n\t4\t[height=0.5,\n\t\tpos="564,738",\n\t\twidth=0.75];\n\t4 -> 18\t[pos="e,554.21,684.28 560.85,720.05 559.42,712.35 557.69,703.03 556.08,694.36"];\n\t4 -> 28\t[pos="e,795.84,466.57 585.84,727.23 606.21,717.63 636.98,701.86 661,684 697.57,656.81 709.59,650.48 734,612 761.26,569.03 749.07,549.42 \\\r\n\\\n772,504 777.04,494.02 783.67,483.71 789.86,474.86"];\n\t49 -> 28\t[pos="e,813.84,432.41 813.88,395.96 814.71,403.83 814.95,413.37 814.58,422.19"];\n\t6\t[height=0.5,\n\t\tpos="660,450",\n\t\twidth=0.75];\n\t19 -> 6\t[pos="e,660,468.1 660,503.7 660,495.98 660,486.71 660,478.11"];\n\t7\t[height=0.5,\n\t\tpos="715,306",\n\t\twidth=0.75];\n\t21 -> 7\t[pos="e,698.8,320.65 667.19,360.41 673.67,350.84 683.06,338.7 691.9,328.42"];\n\t56 -> 25\t[pos="e,282.06,463.64 346.12,508.49 330.72,497.7 308.26,481.98 290.72,469.7"];\n\t56 -> 26\t[pos="e,353.46,468.28 360.61,504.05 359.07,496.35 357.21,487.03 355.47,478.36"];\n\t6 -> 21\t[pos="e,660,396.1 660,431.7 660,423.98 660,414.71 660,406.11"];\n\t20\t[height=0.5,\n\t\tpos="605,234",\n\t\twidth=0.75];\n\t6 -> 20\t[pos="e,604.4,252.07 646.81,433.88 638.83,423.83 629.21,409.97 624,396 607.3,351.22 604.39,295.01 604.33,262.24"];\n\t7 -> 19\t[pos="e,673.19,505.88 715.6,324.07 716.09,354.16 714.59,418.16 696,468 692.09,478.47 685.7,488.89 679.39,497.68"];\n\t7 -> 21\t[pos="e,676.06,363.5 707.93,323.41 701.36,333.14 691.75,345.55 682.75,355.99"];\n\t7 -> 20\t[pos="e,623.94,247.05 695.84,292.81 678.33,281.67 652.24,265.06 632.51,252.5"];\n\t39\t[height=0.5,\n\t\tpos="715,90",\n\t\twidth=0.75];\n\t7 -> 39\t[pos="e,711.14,107.94 711.12,287.85 707.58,250.74 707.31,162.75 710.33,118.05"];\n\t40\t[height=0.5,\n\t\tpos="779,234",\n\t\twidth=0.75];\n\t7 -> 40\t[pos="e,765.45,249.82 728.57,290.15 737.31,280.6 748.83,267.99 758.66,257.25"];\n\t9\t[height=0.5,\n\t\tpos="647,162",\n\t\twidth=0.75];\n\t20 -> 9\t[pos="e,637.22,179.31 614.53,217.12 619.67,208.56 626.12,197.8 631.92,188.13"];\n\t9 -> 21\t[pos="e,658.96,359.85 648.05,180.23 650.3,217.32 655.63,304.98 658.34,349.71"];\n\t9 -> 39\t[pos="e,700.93,105.49 661.09,146.5 670.57,136.73 683.24,123.69 693.92,112.7"];\n\t34\t[height=0.5,\n\t\tpos="643,90",\n\t\twidth=0.75];\n\t9 -> 34\t[pos="e,643.98,108.1 646.01,143.7 645.57,135.98 645.04,126.71 644.55,118.11"];\n\t39 -> 7\t[pos="e,718.88,287.85 718.86,107.94 722.41,144.85 722.69,232.83 719.69,277.69"];\n\t8\t[height=0.5,\n\t\tpos="27,1026",\n\t\twidth=0.75];\n\t8 -> 16\t[pos="e,80.135,969.49 40.882,1010.5 50.135,1000.8 62.471,987.94 72.926,977.02"];\n\t35\t[height=0.5,\n\t\tpos="535,18",\n\t\twidth=0.75];\n\t34 -> 35\t[pos="e,553.6,31.053 624.19,76.807 607,65.665 581.38,49.062 562.01,36.504"];\n\t36\t[height=0.5,\n\t\tpos="607,18",\n\t\twidth=0.75];\n\t34 -> 36\t[pos="e,615.3,35.147 634.65,72.765 630.29,64.283 624.85,53.714 619.96,44.197"];\n\t37\t[height=0.5,\n\t\tpos="679,18",\n\t\twidth=0.75];\n\t34 -> 37\t[pos="e,670.7,35.147 651.35,72.765 655.71,64.283 661.15,53.714 666.04,44.197"];\n\t38\t[height=0.5,\n\t\tpos="751,18",\n\t\twidth=0.75];\n\t34 -> 38\t[pos="e,732.4,31.053 661.81,76.807 679,65.665 704.62,49.062 723.99,36.504"];\n\t10\t[height=0.5,\n\t\tpos="560,882",\n\t\twidth=0.75];\n\t22\t[height=0.5,\n\t\tpos="488,810",\n\t\twidth=0.75];\n\t10 -> 22\t[pos="e,502.8,825.38 545.43,866.83 535.25,856.94 521.48,843.55 509.97,832.36"];\n\t41\t[height=0.5,\n\t\tpos="560,810",\n\t\twidth=0.75];\n\t10 -> 41\t[pos="e,560,828.1 560,863.7 560,855.98 560,846.71 560,838.11"];\n\t22 -> 4\t[pos="e,548.64,753.14 503.38,794.83 514.2,784.87 528.86,771.37 541.05,760.14"];\n\t11\t[height=0.5,\n\t\tpos="488,882",\n\t\twidth=0.75];\n\t11 -> 22\t[pos="e,488,828.1 488,863.7 488,855.98 488,846.71 488,838.11"];\n\t12 -> 17\t[pos="e,145.78,791.97 324.65,384.61 271.44,398.03 153,437.31 153,521 153,667 153,667 153,667 153,707.08 149.38,753.41 146.74,781.95"];\n\t13\t[height=0.5,\n\t\tpos="626,594",\n\t\twidth=0.75];\n\t13 -> 19\t[pos="e,651.92,539.63 633.89,576.76 637.9,568.49 642.89,558.23 647.42,548.9"];\n\t14\t[height=0.5,\n\t\tpos="523,306",\n\t\twidth=0.75];\n\t14 -> 20\t[pos="e,589.11,248.56 539.2,291.17 551.18,280.94 567.69,266.85 581.18,255.34"];\n\t15\t[height=0.5,\n\t\tpos="698,594",\n\t\twidth=0.75];\n\t15 -> 21\t[pos="e,673.69,393.95 700.92,576.05 705.38,546.14 711.84,482.4 696,432 692.65,421.34 686.38,410.88 680,402.1"];\n\t23\t[height=0.5,\n\t\tpos="397,954",\n\t\twidth=0.75];\n\t33\t[height=0.5,\n\t\tpos="389,810",\n\t\twidth=0.75];\n\t23 -> 33\t[pos="e,384.75,827.8 390.11,936.14 386.3,925.88 381.94,912.41 380,900 376.76,879.29 379.44,855.67 382.7,837.98"];\n\t42\t[height=0.5,\n\t\tpos="416,882",\n\t\twidth=0.75];\n\t23 -> 42\t[pos="e,411.44,899.79 401.6,936.05 403.75,928.14 406.35,918.54 408.76,909.69"];\n\t30\t[height=0.5,\n\t\tpos="625,666",\n\t\twidth=0.75];\n\t33 -> 30\t[pos="e,604.33,677.76 407.63,796.49 434.06,778.87 484.12,746 528,720 550.28,706.8 576.02,692.8 595.38,682.5"];\n\t42 -> 22\t[pos="e,473.2,825.38 430.57,866.83 440.75,856.94 454.52,843.55 466.03,832.36"];\n\t42 -> 33\t[pos="e,395.54,827.96 409.6,864.41 406.49,856.34 402.67,846.43 399.17,837.35"];\n\t30 -> 26\t[pos="e,366.09,465.02 603.56,654.62 598.22,652.26 592.46,649.89 587,648 524.65,626.45 492.66,655.42 443,612 404.1,577.99 427.78,547.56 \\\r\n\\\n400,504 392.67,492.5 382.64,481.29 373.5,472.16"];\n\t30 -> 12\t[pos="e,361.18,394.47 603.45,654.94 598.11,652.56 592.38,650.11 587,648 540.69,629.82 518.85,644.29 481,612 463.8,597.32 397.65,451.38 \\\r\n\\\n386,432 380.16,422.28 373.25,411.89 367.06,402.91"];\n\t30 -> 13\t[pos="e,625.76,612.1 625.25,647.7 625.36,639.98 625.49,630.71 625.61,622.11"];\n\t30 -> 14\t[pos="e,517.47,323.84 603.23,655.1 572.03,640.83 517.99,615.77 515,612 489.78,580.26 495,563.54 495,523 495,523 495,523 495,449 495,408.23 \\\r\n\\\n506.25,362.09 514.49,333.77"];\n\t30 -> 15\t[pos="e,683.25,609.14 639.77,650.83 650.16,640.87 664.24,627.37 675.96,616.14"];\n\t24\t[height=0.5,\n\t\tpos="253,1026",\n\t\twidth=0.75];\n\t24 -> 25\t[pos="e,258.67,467.85 249.84,1008 245.18,981.45 237,928.4 237,883 237,883 237,883 237,593 237,552.28 247.85,506.13 255.79,477.79"];\n\t32\t[height=0.5,\n\t\tpos="632,954",\n\t\twidth=0.75];\n\t24 -> 32\t[pos="e,611.47,965.94 279.83,1023.5 338.4,1019.6 481.64,1007 596,972 597.93,971.41 599.89,970.73 601.85,969.99"];\n\t46\t[height=0.5,\n\t\tpos="182,954",\n\t\twidth=0.75];\n\t24 -> 46\t[pos="e,196.69,969.49 238.29,1010.5 228.39,1000.7 215.16,987.69 204.01,976.7"];\n\t51\t[height=0.5,\n\t\tpos="918,738",\n\t\twidth=0.75];\n\t24 -> 51\t[pos="e,912,755.86 280.36,1024.7 347.76,1023.1 526.59,1015 668,972 736.46,951.17 755.04,943.31 812,900 846.32,873.91 853.27,863.99 877,\\\r\n\\\n828 890.04,808.23 901.02,783.64 908.33,765.32"];\n\t31\t[height=0.5,\n\t\tpos="632,882",\n\t\twidth=0.75];\n\t32 -> 31\t[pos="e,632,900.1 632,935.7 632,927.98 632,918.71 632,910.11"];\n\t46 -> 26\t[pos="e,327.07,459.95 185.36,936.03 190.31,909.48 199,856.44 199,811 199,811 199,811 199,593 199,528.29 273.49,484.43 317.83,464.05"];\n\t51 -> 28\t[pos="e,820.3,466.5 914.38,719.98 905.63,680.61 881.27,580.74 844,504 839.12,493.94 832.52,483.62 826.31,474.78"];\n\t31 -> 30\t[pos="e,625.56,684.23 631.44,863.85 630.23,826.83 627.36,739.18 625.9,694.39"];\n\t27\t[height=0.5,\n\t\tpos="693,810",\n\t\twidth=0.75];\n\t31 -> 27\t[pos="e,680.08,825.82 644.94,866.15 653.19,856.69 664.04,844.24 673.34,833.56"];\n\t27 -> 4\t[pos="e,584.34,750.04 672.56,797.91 651.24,786.34 617.6,768.09 593.42,754.97"];\n\t43\t[height=0.5,\n\t\tpos="252,1098",\n\t\twidth=0.75];\n\t43 -> 24\t[pos="e,252.76,1044.1 252.25,1079.7 252.36,1072 252.49,1062.7 252.61,1054.1"];\n\t44\t[height=0.5,\n\t\tpos="180,1098",\n\t\twidth=0.75];\n\t44 -> 24\t[pos="e,238.25,1041.1 194.77,1082.8 205.16,1072.9 219.24,1059.4 230.96,1048.1"];\n\t45\t[height=0.5,\n\t\tpos="324,1098",\n\t\twidth=0.75];\n\t45 -> 33\t[pos="e,383.85,828.11 327.27,1080 334.75,1041.3 354.04,944.3 374,864 376.13,855.42 378.68,846.13 381.06,837.76"];\n\t45 -> 24\t[pos="e,267.69,1041.5 309.29,1082.5 299.39,1072.7 286.16,1059.7 275.01,1048.7"];\n\t47\t[height=0.5,\n\t\tpos="776,882",\n\t\twidth=0.75];\n\t47 -> 39\t[pos="e,737.48,100.08 791.96,867.02 817.07,843.37 863,792.78 863,739 863,739 863,739 863,233 863,169.11 790.29,125.02 746.8,104.36"];\n\t47 -> 30\t[pos="e,638.88,681.59 768.64,864.67 760.11,846.37 745.14,816.1 729,792 703.32,753.64 668.02,713.29 645.86,689.14"];\n\t47 -> 27\t[pos="e,709.08,824.56 759.6,867.17 747.36,856.85 730.45,842.58 716.73,831.01"];\n\t48\t[height=0.5,\n\t\tpos="704,882",\n\t\twidth=0.75];\n\t48 -> 27\t[pos="e,695.71,828.28 701.34,864.05 700.13,856.35 698.66,847.03 697.3,838.36"];\n\t50\t[height=0.5,\n\t\tpos="808,522",\n\t\twidth=0.75];\n\t50 -> 28\t[pos="e,808,468.1 808,503.7 808,495.98 808,486.71 808,478.11"];\n\t52\t[height=0.5,\n\t\tpos="560,954",\n\t\twidth=0.75];\n\t52 -> 31\t[pos="e,617.2,897.38 574.57,938.83 584.75,928.94 598.52,915.55 610.03,904.36"];\n\t53\t[height=0.5,\n\t\tpos="181,1026",\n\t\twidth=0.75];\n\t53 -> 46\t[pos="e,181.76,972.1 181.25,1007.7 181.36,999.98 181.49,990.71 181.61,982.11"];\n\t54\t[height=0.5,\n\t\tpos="488,954",\n\t\twidth=0.75];\n\t54 -> 11\t[pos="e,488,900.1 488,935.7 488,927.98 488,918.71 488,910.11"];\n}\n'
        #'digraph { a->b [pos="e,1973.5,1067.3 1048.5,\\\r\n\\\n1243.5 1613.9,1127.1 1973.3,\\\r\n1072.6"];}' # too short, doesn't work for some reason
        code = dot2tex.dot2tex(graph)

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


class RoundedStyleIssue64Tests(unittest.TestCase):
    # https://github.com/kjellmf/dot2tex/issues/64

    def test_draw_statements(self):
        """There should be at least two \\draw statements"""
        test_graph = r"""
        digraph {
            start[shape="box", style=rounded];
        }
        """
        code = dot2tex.dot2tex(test_graph, codeonly=True)
        self.assertGreaterEqual(code.count("\\draw"), 2)
        self.assertTrue("controls" in code)


class NodeNameIssue41Tests(unittest.TestCase):
    # https://github.com/kjellmf/dot2tex/issues/41

    def test_parsing1(self):
        """Should not throw a ParseException"""
        test_graph = r"""
        digraph G {
            node [shape="circle"];
            "a" -> "b" -> "3" -> "-4" -> "a";
        }
        """
        try:
            code = dot2tex.dot2tex(test_graph, codeonly=True, format="tikz")
        except ParseException:
            self.fail("Failed to parse graph")

    def test_parsing2(self):
        """Should not throw a ParseException"""
        test_graph = r"""
        digraph G {
            node [shape="circle"];
            a -> b -> 3 -> -4 -> a;
        }
        """
        try:
            code = dot2tex.dot2tex(test_graph, codeonly=True, format="tikz")
        except ParseException:
            self.fail("Failed to parse graph")


class MultilineTests(unittest.TestCase):
    # https://github.com/kjellmf/dot2tex/issues/27

    def test_multiline(self):
        """There should be three lines"""
        test_graph = r"""
        digraph {
            a -> b [label="line1\nline2\nline3"]
        }
        """
        code = dot2tex.dot2tex(test_graph, codeonly=True, format="tikz")
        self.assertGreaterEqual(code.count("node {line"), 3)

    def test_multiline_autosize(self):
        """There should be three lines"""
        test_graph = r"""
        digraph {
            a -> b [label="line1\nline2\nline3"]
        }
        """
        code = dot2tex.dot2tex(test_graph, codeonly=True, format="tikz", autosize=True)
        self.assertGreaterEqual(code.count("node {line"), 3)

    def test_is_multiline_function(self):
        self.assertTrue(is_multiline_label(mobj({"label": r"line1\nline2\nline3"})))
        self.assertTrue(is_multiline_label(mobj({"label": r"line1\lline2\lline3"})))
        self.assertTrue(is_multiline_label(mobj({"label": r"line1\rline2\nline3"})))
        self.assertFalse(is_multiline_label(mobj({"texlbl": "something", "label": r"line1\nlin2\line3"})))
        self.assertFalse(is_multiline_label(mobj({"label": "line1\nlin2\nline3"})))


if __name__ == '__main__':
    unittest.main()
