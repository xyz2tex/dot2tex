import logging

from .base import DotConvBase, parse_drawstring
from .utils import smart_float, nsplit, getboolattr, tikzify

log = logging.getLogger("dot2tex")

PGF_TEMPLATE = r"""\documentclass{article}
\usepackage[x11names, svgnames, rgb]{xcolor}
\usepackage[<<textencoding>>]{inputenc}
\usepackage{tikz}
\usetikzlibrary{snakes,arrows,shapes}
\usepackage{amsmath}
<<startpreprocsection>>%
\usepackage[active,auctex]{preview}
<<endpreprocsection>>%
<<gvcols>>%
<<startoutputsection>>
<<cropcode>>%
<<endoutputsection>>
<<docpreamble>>%

\begin{document}
\pagestyle{empty}
%
<<startpreprocsection>>%
<<preproccode>>
<<endpreprocsection>>%
%
<<startoutputsection>>
\enlargethispage{100cm}
% Start of code
% \begin{tikzpicture}[anchor=mid,>=latex',line join=bevel,<<graphstyle>>]
\begin{tikzpicture}[>=latex',line join=bevel,<<graphstyle>>]
  \pgfsetlinewidth{1bp}
<<figpreamble>>%
<<drawcommands>>
<<figpostamble>>%
\end{tikzpicture}
% End of code
<<endoutputsection>>
%
\end{document}
%
<<start_figonlysection>>
\begin{tikzpicture}[>=latex,line join=bevel,<<graphstyle>>]
  \pgfsetlinewidth{1bp}
<<figpreamble>>%
<<drawcommands>>
<<figpostamble>>%
\end{tikzpicture}
<<end_figonlysection>>
<<startcodeonlysection>>
<<figpreamble>>%
<<drawcommands>>
<<figpostamble>>%
<<endcodeonlysection>>
"""
PGF210_TEMPLATE = r"""\documentclass{article}
% dot2tex template for PGF 2.10
\usepackage[x11names, svgnames, rgb]{xcolor}
\usepackage[<<textencoding>>]{inputenc}
\usepackage{tikz}
\usetikzlibrary{snakes,arrows,shapes}
\usepackage{amsmath}
<<startpreprocsection>>%
\usepackage[active,auctex]{preview}
<<endpreprocsection>>%
<<gvcols>>%
<<startoutputsection>>
<<cropcode>>%
<<endoutputsection>>
<<docpreamble>>%

\begin{document}
\pagestyle{empty}
%
<<startpreprocsection>>%
<<preproccode>>
<<endpreprocsection>>%
%
<<startoutputsection>>
\enlargethispage{100cm}
% Start of code
% \begin{tikzpicture}[anchor=mid,>=latex',line join=bevel,<<graphstyle>>]
\begin{tikzpicture}[>=latex',line join=bevel,<<graphstyle>>]
  \pgfsetlinewidth{1bp}
<<figpreamble>>%
<<drawcommands>>
<<figpostamble>>%
\end{tikzpicture}
% End of code
<<endoutputsection>>
%
\end{document}
%
<<start_figonlysection>>
\begin{tikzpicture}[>=latex,line join=bevel,<<graphstyle>>]
  \pgfsetlinewidth{1bp}
<<figpreamble>>%
<<drawcommands>>
<<figpostamble>>%
\end{tikzpicture}
<<end_figonlysection>>
<<startcodeonlysection>>
<<figpreamble>>%
<<drawcommands>>
<<figpostamble>>%
<<endcodeonlysection>>
"""
PGF118_TEMPLATE = r"""\documentclass{article}
\usepackage[x11names, rgb]{xcolor}
\usepackage[<<textencoding>>]{inputenc}
\usepackage{tikz}
\usepackage{pgflibrarysnakes}
\usepackage{pgflibraryarrows,pgflibraryshapes}
\usepackage{amsmath}
<<startpreprocsection>>%
\usepackage[active,auctex]{preview}
<<endpreprocsection>>%
<<gvcols>>%
<<cropcode>>%
<<docpreamble>>%

\begin{document}
\pagestyle{empty}
%
<<startpreprocsection>>%
<<preproccode>>
<<endpreprocsection>>%
%
<<startoutputsection>>
\enlargethispage{100cm}
% Start of code
\begin{tikzpicture}[>=latex',join=bevel,<<graphstyle>>]
  \pgfsetlinewidth{1bp}
<<figpreamble>>%
<<drawcommands>>
<<figpostamble>>%
\end{tikzpicture}
% End of code
<<endoutputsection>>
%
\end{document}
%
<<start_figonlysection>>
\begin{tikzpicture}[>=latex,join=bevel,<<graphstyle>>]
  \pgfsetlinewidth{1bp}
<<figpreamble>>%
<<drawcommands>>
<<figpostamble>>%
\end{tikzpicture}
<<end_figonlysection>>
<<startcodeonlysection>>
<<figpreamble>>%
<<drawcommands>>
<<figpostamble>>%
<<endcodeonlysection>>
"""


class Dot2PGFConv(DotConvBase):
    """PGF/TikZ converter backend"""
    arrows_map_210 = {"dot": "*", "odot": "o", "empty": "open triangle 45", "invempty": "open triangle 45 reversed",
                      "diamond": "diamond", "odiamond": "open diamond", "ediamond": "open diamond", "box": "square",
                      "obox": "open square", "vee": "stealth'", "open": "stealth'", "tee": "|",
                      "crow": "stealth reversed"}

    def __init__(self, options=None):
        DotConvBase.__init__(self, options)
        if not self.template:
            if options.get('pgf118'):
                self.template = PGF118_TEMPLATE
            elif options.get('pgf210'):
                self.template = PGF210_TEMPLATE
            else:
                self.template = PGF_TEMPLATE
        self.styles = dict(dashed='dashed', dotted='dotted',
                           bold='very thick', filled='fill', invis="",
                           rounded='rounded corners', )
        self.dashstyles = dict(
            dashed='\pgfsetdash{{3pt}{3pt}}{0pt}',
            dotted='\pgfsetdash{{\pgflinewidth}{2pt}}{0pt}',
            bold='\pgfsetlinewidth{1.2pt}')

    def start_node(self, node):
        # Todo: Should find a more elegant solution
        self.pencolor = ""
        self.fillcolor = ""
        self.color = ""
        return "\\begin{scope}\n"

    def end_node(self, node):
        return "\\end{scope}\n"

    def start_edge(self):
        # Todo: Should find a more elegant solution
        # self.pencolor = "";
        # self.fillcolor = ""
        # self.color = ""
        return "\\begin{scope}\n"

    def end_edge(self):
        return "\\end{scope}\n"

    def start_graph(self, graph):
        # Todo: Should find a more elegant solution
        self.pencolor = ""
        self.fillcolor = ""
        self.color = ""
        return "\\begin{scope}\n"

    def end_graph(self, graph):
        return "\\end{scope}\n"

    def set_color(self, drawop):
        c, color = drawop
        res = self.convert_color(color, True)
        opacity = None
        if len(res) == 2:
            ccolor, opacity = res
        else:
            ccolor = res
        s = ""
        if c == 'cC':
            if self.color != color:
                self.color = color
                self.pencolor = color
                self.fillcolor = color
                if ccolor.startswith('{'):
                    # rgb or hsb
                    s += "  \definecolor{newcol}%s;\n" % ccolor
                    ccolor = 'newcol'
                s += "  \pgfsetcolor{%s}\n" % ccolor
        elif c == 'c':
            # set pen color
            if self.pencolor != color:
                self.pencolor = color
                self.color = ''
                if ccolor.startswith('{'):
                    # rgb or hsb
                    s += "  \definecolor{strokecol}%s;\n" % ccolor
                    ccolor = 'strokecol'
                s += "  \pgfsetstrokecolor{%s}\n" % ccolor
            else:
                return ""
        elif c == 'C':
            # set fill color
            if self.fillcolor != color:
                self.fillcolor = color
                self.color = ''
                if ccolor.startswith('{'):
                    # rgb
                    s += "  \definecolor{fillcol}%s;\n" % ccolor
                    ccolor = 'fillcol'
                s += "  \pgfsetfillcolor{%s}\n" % ccolor
                if not opacity is None:
                    self.opacity = opacity
                    # Todo: The opacity should probably be set directly when drawing
                    # The \pgfsetfillcopacity cmd affects text as well
                    # s += "  \pgfsetfillopacity{%s};\n" % opacity
                else:
                    self.opacity = None
            else:
                return ""
        return s

    def set_style(self, drawop):
        c, style = drawop
        pgfstyle = self.dashstyles.get(style, "")
        if pgfstyle:
            return "  %s\n" % pgfstyle
        else:
            return ""

    def filter_styles(self, style):
        filtered_styles = []
        for item in style.split(','):
            keyval = item.strip()
            if keyval.find('setlinewidth') < 0 and not keyval == 'filled':
                filtered_styles.append(keyval)
        return ', '.join(filtered_styles)

    def draw_ellipse(self, drawop, style=None):
        op, x, y, w, h = drawop
        s = ""
        if op == 'E':
            if self.opacity is not None:
                # Todo: Need to know the state of the current node
                cmd = 'filldraw [opacity=%s]' % self.opacity
            else:
                cmd = 'filldraw'
        else:
            cmd = "draw"

        if style:
            stylestr = " [%s]" % style
        else:
            stylestr = ''
        s += "  \%s%s (%sbp,%sbp) ellipse (%sbp and %sbp);\n" % (cmd, stylestr, smart_float(x), smart_float(y),
                                                                 # w+self.linewidth,h+self.linewidth)
                                                                 smart_float(w), smart_float(h))
        return s

    def draw_polygon(self, drawop, style=None):
        op, points = drawop
        pp = ['(%sbp,%sbp)' % (smart_float(p[0]), smart_float(p[1])) for p in points]
        cmd = "draw"
        if op == 'P':
            cmd = "filldraw"

        if style:
            stylestr = " [%s]" % style
        else:
            stylestr = ''
        s = "  \%s%s %s -- cycle;\n" % (cmd, stylestr, " -- ".join(pp))
        return s

    def draw_polyline(self, drawop, style=None):
        op, points = drawop
        pp = ['(%sbp,%sbp)' % (smart_float(p[0]), smart_float(p[1])) for p in points]
        stylestr = ''
        return "  \draw%s %s;\n" % (stylestr, " -- ".join(pp))

    def draw_text(self, drawop, style=None):
        # The coordinates given by drawop are not the same as the node
        # coordinates! This may give som odd results if graphviz' and
        # LaTeX' fonts are very different.
        if len(drawop) == 7:
            c, x, y, align, w, text, valign = drawop
        else:
            c, x, y, align, w, text = drawop

        styles = []
        if align == "-1":
            alignstr = 'right'  # left aligned
        elif align == "1":
            alignstr = 'left'  # right aligned
        else:
            alignstr = ""  # centered (default)
        styles.append(alignstr)
        styles.append(style)
        lblstyle = ",".join([i for i in styles if i])
        if lblstyle:
            lblstyle = '[' + lblstyle + ']'
        s = "  \draw (%sbp,%sbp) node%s {%s};\n" % (smart_float(x), smart_float(y), lblstyle, text)
        return s

    def draw_bezier(self, drawop, style=None):
        s = ""
        c, points = drawop
        pp = []
        for point in points:
            pp.append("(%sbp,%sbp)" % (smart_float(point[0]), smart_float(point[1])))

        pstrs = ["%s .. controls %s and %s " % p for p in nsplit(pp, 3)]
        stylestr = ''
        s += "  \draw%s %s .. %s;\n" % (stylestr, " .. ".join(pstrs), pp[-1])
        return s

    def do_edges(self):
        s = ""
        s += self.set_color(('cC', "black"))
        for edge in self.edges:
            general_draw_string = getattr(edge, '_draw_', "")
            label_string = getattr(edge, '_ldraw_', "")
            head_arrow_string = getattr(edge, '_hdraw_', "")
            tail_arrow_string = getattr(edge, '_tdraw_', "")
            tail_label_string = getattr(edge, '_tldraw_', "")
            head_label_string = getattr(edge, '_hldraw_', "")

            # Note that the order of the draw strings should be the same
            # as in the xdot output.
            drawstring = general_draw_string + " " + head_arrow_string + " " + tail_arrow_string \
                         + " " + label_string
            draw_operations, stat = parse_drawstring(drawstring)
            if not drawstring.strip():
                continue
            s += self.output_edge_comment(edge)
            if self.options.get('duplicate'):
                s += self.start_edge()
                s += self.do_draw_op(draw_operations, edge, stat)
                s += self.do_drawstring(tail_label_string, edge, "tailtexlbl")
                s += self.do_drawstring(head_label_string, edge, "headtexlbl")
                s += self.end_edge()
            else:
                topath = getattr(edge, 'topath', None)
                s += self.draw_edge(edge)
                if not self.options.get('tikzedgelabels') and not topath:
                    s += self.do_drawstring(label_string, edge)
                    s += self.do_drawstring(tail_label_string, edge, "tailtexlbl")
                    s += self.do_drawstring(head_label_string, edge, "headtexlbl")
                else:
                    s += self.do_drawstring(tail_label_string, edge, "tailtexlbl")
                    s += self.do_drawstring(head_label_string, edge, "headtexlbl")

        self.body += s

    def draw_edge(self, edge):
        s = ""
        if edge.attr.get('style', '') in ['invis', 'invisible']:
            return ""
        edges = self.get_edge_points(edge)
        for arrowstyle, points in edges:
            # arrowstyle, points = self.get_edge_points(edge)
            # PGF uses the fill style when drawing some arrowheads. We have to
            # ensure that the fill color is the same as the pen color.
            color = getattr(edge, 'color', '')

            if self.color != color:
                if color:
                    s += self.set_color(('cC', color))
                else:
                    # reset to default color
                    s += self.set_color(('cC', 'black'))

            pp = []
            for point in points:
                p = point.split(',')
                pp.append("(%sbp,%sbp)" % (smart_float(p[0]), smart_float(p[1])))

            edgestyle = edge.attr.get('style', '')

            styles = []
            if arrowstyle != '--':
                styles = [arrowstyle]

            if edgestyle:
                edgestyles = [self.styles.get(key.strip(), key.strip()) for key in edgestyle.split(',') if key]
                styles.extend(edgestyles)

            stylestr = ",".join(styles)
            topath = getattr(edge, 'topath', None)

            pstrs = ["%s .. controls %s and %s " % x for x in nsplit(pp, 3)]
            extra = ""
            if self.options.get('tikzedgelabels') or topath:
                edgelabel = self.get_label(edge)
                # log.warning('label: %s', edgelabel)
                lblstyle = getattr(edge, 'lblstyle', '')
                if lblstyle:
                    lblstyle = '[' + lblstyle + ']'
                else:
                    lblstyle = ''
                if edgelabel:
                    extra = " node%s {%s}" % (lblstyle, edgelabel)
            src = pp[0]
            dst = pp[-1]
            if topath:
                s += "  \draw [%s] %s to[%s]%s %s;\n" % (stylestr, src,
                                                         topath, extra, dst)
            elif not self.options.get('straightedges'):
                s += "  \draw [%s] %s ..%s %s;\n" % (stylestr, " .. ".join(pstrs), extra, pp[-1])
            else:
                s += "  \draw [%s] %s --%s %s;\n" % (stylestr, pp[0], extra, pp[-1])

        return s

    def get_output_arrow_styles(self, arrow_style, edge):
        dot_arrow_head = edge.attr.get("arrowhead")
        dot_arrow_tail = edge.attr.get("arrowtail")
        output_arrow_style = arrow_style
        if dot_arrow_head:
            pgf_arrow_head = self.arrows_map_210.get(dot_arrow_head)
            if pgf_arrow_head:
                output_arrow_style = output_arrow_style.replace(">", pgf_arrow_head)
        if dot_arrow_tail:
            pgf_arrow_tail = self.arrows_map_210.get(dot_arrow_tail)
            if pgf_arrow_tail:
                output_arrow_style = output_arrow_style.replace("<", pgf_arrow_tail)
        return output_arrow_style

    def init_template_vars(self):
        DotConvBase.init_template_vars(self)
        if self.options.get('crop'):
            cropcode = "\\usepackage[active,tightpage]{preview}\n" + \
                       "\\PreviewEnvironment{tikzpicture}\n" + \
                       "\\setlength\\PreviewBorder{%s}" % self.options.get('margin', '0pt')
        else:
            cropcode = ""
        variables = {'<<cropcode>>': cropcode}
        self.templatevars.update(variables)

    def get_node_preproc_code(self, node):
        lblstyle = node.attr.get('lblstyle', '')
        text = node.attr.get('texlbl', '')
        if lblstyle:
            return "  \\tikz \\node[%s] {%s};\n" % (lblstyle, text)
        else:
            return r"\tikz \node {" + text + "};"

    def get_edge_preproc_code(self, edge, attribute="texlbl"):
        lblstyle = edge.attr.get('lblstyle', '')
        text = edge.attr.get(attribute, '')
        if lblstyle:
            return "  \\tikz \\node[%s] {%s};\n" % (lblstyle, text)
        else:
            return r"\tikz \node " + "{" + text + "};"

    def get_graph_preproc_code(self, graph):
        lblstyle = graph.attr.get('lblstyle', '')
        text = graph.attr.get('texlbl', '')
        if lblstyle:
            return "  \\tikz \\node[%s] {%s};\n" % (lblstyle, text)
        else:
            return r"\tikz \node {" + text + "};"


TIKZ_TEMPLATE = r"""\documentclass{article}
\usepackage[x11names, svgnames, rgb]{xcolor}
\usepackage[<<textencoding>>]{inputenc}
\usepackage{tikz}
\usetikzlibrary{snakes,arrows,shapes}
\usepackage{amsmath}
<<startpreprocsection>>%
\usepackage[active,auctex]{preview}
<<endpreprocsection>>%
<<gvcols>>%
<<startoutputsection>>
<<cropcode>>%
<<endoutputsection>>
<<docpreamble>>%

\begin{document}
\pagestyle{empty}
%
<<startpreprocsection>>%
<<preproccode>>
<<endpreprocsection>>%
%
<<startoutputsection>>
\enlargethispage{100cm}
% Start of code
\begin{tikzpicture}[>=latex',line join=bevel,<<graphstyle>>]
<<figpreamble>>%
<<drawcommands>>
<<figpostamble>>%
\end{tikzpicture}
% End of code
<<endoutputsection>>
%
\end{document}
%
<<start_figonlysection>>
\begin{tikzpicture}[>=latex,line join=bevel,<<graphstyle>>]
<<figpreamble>>%
<<drawcommands>>
<<figpostamble>>%
\end{tikzpicture}
<<end_figonlysection>>
<<startcodeonlysection>>
<<figpreamble>>%
<<drawcommands>>
<<figpostamble>>%
<<endcodeonlysection>>
"""
TIKZ210_TEMPLATE = r"""\documentclass{article}
% dot2tex template for PGF 2.10
\usepackage[x11names, svgnames, rgb]{xcolor}
\usepackage[<<textencoding>>]{inputenc}
\usepackage{tikz}
\usetikzlibrary{snakes,arrows,shapes}
\usepackage{amsmath}
<<startpreprocsection>>%
\usepackage[active,auctex]{preview}
<<endpreprocsection>>%
<<gvcols>>%
<<startoutputsection>>
<<cropcode>>%
<<endoutputsection>>
<<docpreamble>>%

\begin{document}
\pagestyle{empty}
%
<<startpreprocsection>>%
<<preproccode>>
<<endpreprocsection>>%
%
<<startoutputsection>>
\enlargethispage{100cm}
% Start of code
\begin{tikzpicture}[>=latex',line join=bevel,<<graphstyle>>]
<<figpreamble>>%
<<drawcommands>>
<<figpostamble>>%
\end{tikzpicture}
% End of code
<<endoutputsection>>
%
\end{document}
%
<<start_figonlysection>>
\begin{tikzpicture}[>=latex,line join=bevel,<<graphstyle>>]
<<figpreamble>>%
<<drawcommands>>
<<figpostamble>>%
\end{tikzpicture}
<<end_figonlysection>>
<<startcodeonlysection>>
<<figpreamble>>%
<<drawcommands>>
<<figpostamble>>%
<<endcodeonlysection>>
"""
TIKZ118_TEMPLATE = r"""\documentclass{article}
\usepackage[x11names, svgnames, rgb]{xcolor}
\usepackage[<<textencoding>>]{inputenc}
\usepackage{tikz}
\usepackage{pgflibrarysnakes}
\usepackage{pgflibraryarrows,pgflibraryshapes}
\usepackage{amsmath}
<<startpreprocsection>>%
\usepackage[active,auctex]{preview}
<<endpreprocsection>>%
<<gvcols>>%
<<cropcode>>%
<<docpreamble>>%

\begin{document}
\pagestyle{empty}
%
<<startpreprocsection>>%
<<preproccode>>
<<endpreprocsection>>%
%
<<startoutputsection>>
\enlargethispage{100cm}
% Start of code
\begin{tikzpicture}[>=latex',join=bevel,<<graphstyle>>]
<<figpreamble>>%
<<drawcommands>>
<<figpostamble>>%
\end{tikzpicture}
% End of code
<<endoutputsection>>
%
\end{document}
%
<<start_figonlysection>>
\begin{tikzpicture}[>=latex,join=bevel,<<graphstyle>>]
<<figpreamble>>%
<<drawcommands>>
<<figpostamble>>%
\end{tikzpicture}
<<end_figonlysection>>
<<startcodeonlysection>>
<<figpreamble>>%
<<drawcommands>>
<<figpostamble>>%
<<endcodeonlysection>>
"""


class Dot2TikZConv(Dot2PGFConv):
    """A backend that utilizes the node and edge mechanism of PGF/TikZ"""
    shape_map = {'doublecircle': 'circle, double',
                 'box': 'rectangle',
                 'rect': 'rectangle',
                 'none': 'draw=none',
                 'plaintext': 'draw=none',
                 'polygon': 'regular polygon, regular polygon sides=7',
                 'triangle': 'regular polygon, regular polygon sides=3',
                 'square': 'regular polygon, regular polygon sides=4',
                 'pentagon': 'regular polygon, regular polygon sides=5',
                 'hexagon': 'regular polygon, regular polygon sides=6',
                 'septagon': 'regular polygon, regular polygon sides=7',
                 'octagon': 'regular polygon, regular polygon sides=8',
                 'point': 'circle, fill',
                 'ellipse': 'ellipse',
                 'oval': 'ellipse',
                 'diamond': 'diamond',
                 'trapezium': 'trapezium',
                 'star': 'star',
                 'circle': 'circle',
                 }

    compass_map = {'n': 'north', 'ne': 'north east', 'e': 'east',
                   'se': 'south east', 's': 'south', 'sw': 'south west',
                   'w': 'west', 'nw': 'north west', 'center': 'center'}

    def __init__(self, options=None):
        # to connect nodes they have to defined. Therefore we have to ensure
        # that code for generating nodes is outputted first.
        options = options or {}
        options['switchdraworder'] = True
        options['flattengraph'] = True
        options['rawdim'] = True
        if options.get('pgf118'):
            self.template = TIKZ118_TEMPLATE
        elif options.get('pgf210'):
            self.template = TIKZ210_TEMPLATE
        else:
            self.template = TIKZ_TEMPLATE
        DotConvBase.__init__(self, options)

        self.styles = dict(dashed='dashed', dotted='dotted',
                           bold='very thick', filled='fill', invis="", invisible="",
                           rounded='rounded corners', )
        self.dashstyles = dict(
            dashed='\pgfsetdash{{3pt}{3pt}}{0pt}',
            dotted='\pgfsetdash{{\pgflinewidth}{2pt}}{0pt}',
            bold='\pgfsetlinewidth{1.2pt}')

    def set_options(self):
        Dot2PGFConv.set_options(self)
        self.options['tikzedgelabels'] = self.options.get('tikzedgelabels', '') \
                                         or getboolattr(self.main_graph, 'd2ttikzedgelabels', '')
        self.options['styleonly'] = self.options.get('styleonly', '') \
                                    or getboolattr(self.main_graph, 'd2tstyleonly', '')
        self.options['nodeoptions'] = self.options.get('nodeoptions', '') \
                                      or getattr(self.main_graph, 'd2tnodeoptions', '')
        self.options['edgeoptions'] = self.options.get('edgeoptions', '') \
                                      or getattr(self.main_graph, 'd2tedgeoptions', '')

    def output_node_comment(self, node):
        # With the node syntax comments are unnecessary
        return ""

    def set_tikzcolor(self, color, colorname):
        res = self.convert_color(color, True)
        if len(res) == 2:
            ccolor, opacity = res
            if not (opacity == '1'):
                log.warning('Opacity not supported yet: %s', res)
        else:
            ccolor = res
        s = ""
        if ccolor.startswith('{'):
            # rgb or hsb
            s += "  \definecolor{%s}%s;\n" % (colorname, ccolor)
            cname = colorname
        else:
            cname = color

        return s, cname

    def get_node_preproc_code(self, node):
        lblstyle = node.attr.get('lblstyle', '')

        shape = node.attr.get('shape', 'ellipse')
        shape = self.shape_map.get(shape, shape)
        # s += "%% %s\n" % (shape)
        label = node.attr.get('texlbl', '')
        style = node.attr.get('style', " ") or " "
        if lblstyle:
            if style.strip():
                style += ',' + lblstyle
            else:
                style = lblstyle

        sn = ""
        if self.options.get('styleonly'):
            sn += "\\tikz  \\node [%s] {%s};\n" % \
                  (style, label)
        else:
            sn += "\\tikz  \\node [draw,%s,%s] {%s};\n" % \
                  (shape, style, label)
        return sn

    def do_nodes(self):
        s = ""
        nodeoptions = self.options.get('nodeoptions')
        if nodeoptions:
            s += "\\begin{scope}[%s]\n" % nodeoptions
        for node in self.nodes:
            self.currentnode = node
            # detect node type
            dotshape = getattr(node, 'shape', 'ellipse')
            shape = None

            if node.attr.get('style') in ['invis', 'invisible']:
                shape = "coordinate"
            else:
                shape = self.shape_map.get(dotshape, shape)
            if shape is None:
                shape = 'ellipse'

            pos = getattr(node, 'pos', None)
            if not pos:
                continue
            x, y = pos.split(',')
            if dotshape != 'point':
                label = self.get_label(node)
            else:
                label = ''

            pos = "%sbp,%sbp" % (smart_float(x), smart_float(y))
            style = node.attr.get('style') or ""
            if node.attr.get('lblstyle'):
                if style:
                    style += ',' + node.attr['lblstyle']
                else:
                    style = node.attr['lblstyle']
            if node.attr.get('exstyle'):
                if style:
                    style += ',' + node.attr['exstyle']
                else:
                    style = node.attr['exstyle']
            sn = ""
            sn += self.output_node_comment(node)
            sn += self.start_node(node)
            if shape == "coordinate":
                sn += "  \\coordinate (%s) at (%s);\n" % (tikzify(node.name), pos)
            elif self.options.get('styleonly'):
                sn += "  \\node (%s) at (%s) [%s] {%s};\n" % \
                      (tikzify(node.name), pos, style, label)
            else:
                color = node.attr.get('color', '')
                drawstr = 'draw'
                if style.strip() == 'filled':
                    fillcolor = node.attr.get('fillcolor') or \
                                node.attr.get('color') or "gray"
                    drawstr = 'fill,draw'
                    style = ''
                    if color:
                        code, color = self.set_tikzcolor(color, 'strokecolor')
                        sn += code
                        code, fillcolor = self.set_tikzcolor(fillcolor, 'fillcolor')
                        sn += code
                        drawstr = "draw=%s,fill=%s" % (color, fillcolor)
                    else:
                        code, fillcolor = self.set_tikzcolor(fillcolor, 'fillcolor')
                        sn += code
                        drawstr = "draw,fill=%s" % fillcolor
                elif color:
                    code, color = self.set_tikzcolor(color, 'strokecolor')
                    sn += code
                    drawstr += '=' + color

                if style.strip():
                    sn += "  \\node (%s) at (%s) [%s,%s,%s] {%s};\n" % \
                          (tikzify(node.name), pos, drawstr, shape, style, label)
                else:
                    sn += "  \\node (%s) at (%s) [%s,%s] {%s};\n" % \
                          (tikzify(node.name), pos, drawstr, shape, label)
            sn += self.end_node(node)

            s += sn
        if nodeoptions:
            s += "\\end{scope}\n"
        self.body += s

    def do_edges(self):
        s = ""
        edgeoptions = self.options.get('edgeoptions')
        if edgeoptions:
            s += "\\begin{scope}[%s]\n" % edgeoptions
        for edge in self.edges:
            # general_draw_string = getattr(edge, '_draw_', "")
            label_string = getattr(edge, '_ldraw_', "")
            # head_arrow_string = getattr(edge, '_hdraw_', "")
            # tail_arrow_string = getattr(edge, '_tdraw_', "")
            tail_label_string = getattr(edge, '_tldraw_', "")
            head_label_string = getattr(edge, '_hldraw_', "")
            topath = getattr(edge, 'topath', None)
            s += self.draw_edge(edge)
            if not self.options.get('tikzedgelabels') and not topath:
                s += self.do_drawstring(label_string, edge)
                s += self.do_drawstring(tail_label_string, edge, "tailtexlbl")
                s += self.do_drawstring(head_label_string, edge, "headtexlbl")
            else:
                s += self.do_drawstring(tail_label_string, edge, "tailtexlbl")
                s += self.do_drawstring(head_label_string, edge, "headtexlbl")

        if edgeoptions:
            s += "\\end{scope}\n"
        self.body += s

    def draw_edge(self, edge):
        s = ""
        if edge.attr.get('style', '') in ['invis', 'invisible']:
            return ""
        edges = self.get_edge_points(edge)
        if len(edges) > 1:
            log.warning('The tikz output format does not support edge'
                        'concentrators yet. Expect ugly output or try the pgf or '
                        'pstricks output formats.')
        for arrowstyle, points in edges:
            # PGF uses the fill style when drawing some arrowheads. We have to
            # ensure that the fill color is the same as the pen color.
            color = edge.attr.get('color', '')
            pp = []
            for point in points:
                p = point.split(',')
                pp.append("(%sbp,%sbp)" % (smart_float(p[0]), smart_float(p[1])))

            edgestyle = edge.attr.get('style')

            styles = []
            if arrowstyle != '--':
                # styles.append(arrowstyle)
                styles = [arrowstyle]

            if edgestyle:
                edgestyles = [self.styles.get(key.strip(), key.strip()) \
                              for key in edgestyle.split(',') if key]
                styles.extend(edgestyles)

            stylestr = ",".join(styles)
            if color:
                code, color = self.set_tikzcolor(color, 'strokecolor')
                s += code
                stylestr = color + ',' + stylestr
            src = tikzify(edge.get_source())
            # check for a port
            if edge.src_port:
                src_anchor = self.compass_map.get(edge.src_port.split(':')[-1], '')
                if src_anchor:
                    src = "%s.%s" % (src, src_anchor)
            dst = tikzify(edge.get_destination())
            if edge.dst_port:
                dst_anchor = self.compass_map.get(edge.dst_port.split(':')[-1], '')
                if dst_anchor:
                    dst = "%s.%s" % (dst, dst_anchor)
            topath = edge.attr.get('topath')

            pstrs = ["%s .. controls %s and %s " % x for x in nsplit(pp, 3)]
            pstrs[0] = "(%s) ..controls %s and %s " % (src, pp[1], pp[2])
            extra = ""
            if self.options.get('tikzedgelabels') or topath:
                edgelabel = self.get_label(edge)
                # log.warning('label: %s', edgelabel)
                lblstyle = getattr(edge, 'lblstyle', '')
                exstyle = getattr(edge, 'exstyle', '')
                if exstyle:
                    if lblstyle:
                        lblstyle += ',' + exstyle
                    else:
                        lblstyle = exstyle
                if lblstyle:
                    lblstyle = '[' + lblstyle + ']'
                else:
                    lblstyle = ''
                if edgelabel:
                    extra = " node%s {%s}" % (lblstyle, edgelabel)

            if topath:
                s += "  \draw [%s] (%s) to[%s]%s (%s);\n" % (stylestr, src,
                                                             topath, extra, dst)
            elif not self.options.get('straightedges'):
                s += "  \draw [%s] %s ..%s (%s);\n" % (stylestr,
                                                       " .. ".join(pstrs), extra, dst)
            else:
                s += "  \draw [%s] (%s) --%s (%s);\n" % (stylestr, src, extra, dst)

        return s

    def start_node(self, node):
        return ""

    def end_node(self, node):
        return ""


class PositionsDotConv(Dot2PGFConv):
    """A converter that returns a dictionary with node positions

    Returns a dictionary with node name as key and a (x, y) tuple as value.
    """

    def output(self):
        positions = {}
        for node in self.nodes:
            pos = getattr(node, 'pos', None)
            if pos:
                try:
                    positions[node.name] = [int(p) for p in pos.split(',')]
                except ValueError:
                    positions[node.name] = [float(p) for p in pos.split(',')]
        return positions