import logging

from .base import DotConvBase
from .utils import smart_float, tikzify

log = logging.getLogger("dot2tex")

PSTRICKS_TEMPLATE = r"""\documentclass{article}
% <<bbox>>
\usepackage[x11names,svgnames]{xcolor}
\usepackage[<<textencoding>>]{inputenc}
\usepackage{graphicx}
\usepackage{pstricks}
\usepackage{amsmath}
<<startpreprocsection>>%
\usepackage[active,auctex]{preview}
<<endpreprocsection>>%
<<gvcols>>%
<<docpreamble>>%


\begin{document}
\pagestyle{empty}
<<startpreprocsection>>%
<<preproccode>>%
<<endpreprocsection>>%
<<startoutputsection>>%
\enlargethispage{100cm}

% Start of code
\begin{pspicture}[linewidth=1bp<<graphstyle>>]<<bbox>>
  \pstVerb{2 setlinejoin} % set line join style to 'mitre'
<<figpreamble>>%
<<drawcommands>>
<<figpostamble>>%
\end{pspicture}
% End of code
<<endoutputsection>>%
\end{document}
%
<<start_figonlysection>>
\begin{pspicture}[linewidth=1bp<<graphstyle>>]<<bbox>>
  \pstVerb{2 setlinejoin} % set line join style to 'mitre'
<<figpreamble>>%
<<drawcommands>>
<<figpostamble>>%
\end{pspicture}
<<end_figonlysection>>
%
<<startcodeonlysection>>
<<figpreamble>>%
<<drawcommands>>
<<figpostamble>>%
<<endcodeonlysection>>
"""


class Dot2PSTricksConv(DotConvBase):
    """PSTricks converter backend"""

    def __init__(self, options=None):
        DotConvBase.__init__(self, options)
        if not self.template:
            self.template = PSTRICKS_TEMPLATE
        self.styles = dict(
            dotted="linestyle=dotted",
            dashed="linestyle=dashed",
            bold="linewidth=2pt",
            solid="",
            filled="",
        )

    def do_graphtmp(self):
        self.pencolor = ""
        self.fillcolor = ""
        self.color = ""
        self.body += '{\n'
        DotConvBase.do_graph(self)
        self.body += '}\n'

    def draw_ellipse(self, drawop, style=None):
        op, x, y, w, h = drawop
        s = ""
        if op == 'E':
            if style:
                style = style.replace('filled', '')
            stylestr = 'fillstyle=solid'
        else:
            stylestr = ""

        if style:
            if stylestr:
                stylestr += ',' + style
            else:
                stylestr = style

        s += "  \psellipse[%s](%sbp,%sbp)(%sbp,%sbp)\n" % (stylestr, smart_float(x), smart_float(y),
                                                           # w+self.linewidth,h+self.linewidth)
                                                           smart_float(w), smart_float(h))

        return s

    def draw_polygon(self, drawop, style=None):
        op, points = drawop
        pp = ['(%sbp,%sbp)' % (smart_float(p[0]), smart_float(p[1])) for p in points]
        stylestr = ""
        if op == 'P':
            if style:
                style = style.replace('filled', '')
            stylestr = "fillstyle=solid"
        if style:
            if stylestr:
                stylestr += ',' + style
            else:
                stylestr = style

        s = "  \pspolygon[%s]%s\n" % (stylestr, "".join(pp))
        return s

    def draw_polyline(self, drawop, style=None):
        op, points = drawop
        pp = ['(%sbp,%sbp)' % (smart_float(p[0]), smart_float(p[1])) for p in points]
        s = "  \psline%s\n" % "".join(pp)
        return s

    def draw_bezier(self, drawop, style=None):
        op, points = drawop
        pp = []
        for point in points:
            pp.append("(%sbp,%sbp)" % (smart_float(point[0]), smart_float(point[1])))

        arrowstyle = ""
        return "  \psbezier{%s}%s\n" % (arrowstyle, "".join(pp))

    def draw_text(self, drawop, style=None):
        if len(drawop) == 7:
            c, x, y, align, w, text, valign = drawop
        else:
            c, x, y, align, w, text = drawop
            valign = ""
        if align == "-1":
            alignstr = 'l'  # left aligned
        elif align == "1":
            alignstr = 'r'  # right aligned
        else:
            alignstr = ""  # centered (default)
        if alignstr or valign:
            alignstr = '[' + alignstr + valign + ']'
        s = "  \\rput%s(%sbp,%sbp){%s}\n" % (alignstr, smart_float(x), smart_float(y), text)
        return s

    def set_color(self, drawop):
        c, color = drawop
        color = self.convert_color(color)
        s = ""
        if c == 'c':
            # set pen color
            if self.pencolor != color:
                self.pencolor = color
                s = "  \psset{linecolor=%s}\n" % color
            else:
                return ""
        elif c == 'C':
            # set fill color
            if self.fillcolor != color:
                self.fillcolor = color
                s = "  \psset{fillcolor=%s}\n" % color
            else:
                return ""
        elif c == 'cC':
            if self.color != color:
                self.color = color
                self.pencolor = self.fillcolor = color
                s = "  \psset{linecolor=%s}\n" % color
        else:
            log.warning('Unhandled color: %s', drawop)
        return s

    def set_style(self, drawop):
        c, style = drawop
        psstyle = self.styles.get(style, "")
        if psstyle:
            return "  \psset{%s}\n" % psstyle
        else:
            return ""

    def filter_styles(self, style):
        filtered_styles = []
        for item in style.split(','):
            keyval = item.strip()
            if keyval.find('setlinewidth') < 0:
                filtered_styles.append(keyval)
        return ', '.join(filtered_styles)

    def start_node(self, node):
        self.pencolor = ""
        self.fillcolor = ""
        self.color = ""
        return "{%\n"

    def end_node(self, node):
        return "}%\n"

    def start_edge(self):
        self.pencolor = ""
        self.fillcolor = ""
        return "{%\n"

    def end_edge(self):
        return "}%\n"

    def start_graph(self, graph):
        self.pencolor = ""
        self.fillcolor = ""
        self.color = ""
        return "{\n"

    def end_graph(self, node):
        return "}\n"

    def draw_edge(self, edge):
        s = ""
        if edge.attr.get('style', '') in ['invis', 'invisible']:
            return ""
        edges = self.get_edge_points(edge)
        for arrowstyle, points in edges:
            if arrowstyle == '--':
                arrowstyle = ''
            color = getattr(edge, 'color', '')
            if self.color != color:
                if color:
                    s += self.set_color(('c', color))
                else:
                    # reset to default color
                    s += self.set_color(('c', 'black'))
            pp = []
            for point in points:
                p = point.split(',')
                pp.append("(%sbp,%sbp)" % (smart_float(p[0]), smart_float(p[1])))

            edgestyle = edge.attr.get('style', '')
            styles = []
            if arrowstyle:
                styles.append('arrows=%s' % arrowstyle)
            if edgestyle:
                edgestyles = [self.styles.get(key.strip(), key.strip())
                              for key in edgestyle.split(',') if key]
                styles.extend(edgestyles)
            if styles:
                stylestr = ",".join(styles)
            else:
                stylestr = ""
            if not self.options.get('straightedges'):
                s += "  \psbezier[%s]%s\n" % (stylestr, "".join(pp))
            else:
                s += "  \psline[%s]%s%s\n" % (stylestr, pp[0], pp[-1])
                # s += "  \psbezier[%s]{%s}%s\n" % (stylestr, arrowstyle,"".join(pp))
                ##        if edge.label:
                ##            x,y = edge.lp.split(',')
                ##            #s += "\\rput(%s,%s){%s}\n" % (x,y,edge.label)
        return s

    def init_template_vars(self):
        DotConvBase.init_template_vars(self)
        # Put a ',' before <<graphstyle>>
        graphstyle = self.templatevars.get('<<graphstyle>>', '')
        if graphstyle:
            graphstyle = graphstyle.strip()
            if not graphstyle.startswith(','):
                graphstyle = ',' + graphstyle
                self.templatevars['<<graphstyle>>'] = graphstyle


PSTRICKSN_TEMPLATE = r"""\documentclass{article}
% <<bbox>>
\usepackage[x11names, svgnames]{xcolor}
\usepackage[<<textencoding>>]{inputenc}
\usepackage{graphicx}
\usepackage{pst-all}
\usepackage[a3paper,landscape]{geometry}
\usepackage{amsmath}
<<startpreprocsection>>%
\usepackage[active,auctex]{preview}
<<endpreprocsection>>%
<<gvcols>>%
<<docpreamble>>%


\begin{document}
\pagestyle{empty}
<<startpreprocsection>>%
<<preproccode>>%
<<endpreprocsection>>%
<<startoutputsection>>%
\enlargethispage{100cm}

% Start of code
\begin{pspicture}[linewidth=1bp<<graphstyle>>]<<bbox>>
  \pstVerb{2 setlinejoin} % set line join style to 'mitre'
<<figpreamble>>%
<<drawcommands>>
<<figpostamble>>%
\end{pspicture}
% End of code
<<endoutputsection>>%
\end{document}
%
<<start_figonlysection>>
\begin{pspicture}[linewidth=1bp<<graphstyle>>]<<bbox>>
  \pstVerb{2 setlinejoin} % set line join style to 'mitre'
<<figpreamble>>%
<<drawcommands>>
<<figpostamble>>%
\end{pspicture}
<<end_figonlysection>>
%
<<startcodeonlysection>>
<<figpreamble>>%
<<drawcommands>>
<<figpostamble>>%
<<endcodeonlysection>>
"""


class Dot2PSTricksNConv(Dot2PSTricksConv):
    """A backend that utilizes the node and edge mechanism of PSTricks-Node"""

    def __init__(self, options=None):
        options = options or {}
        # to connect nodes they have to defined. Therefore we have to ensure
        # that code for generating nodes is outputted first.
        options['switchdraworder'] = True
        options['flattengraph'] = True
        options['rawdim'] = True
        self.template = PSTRICKSN_TEMPLATE
        Dot2PSTricksConv.__init__(self, options)

    def output_node_comment(self, node):
        # With the node syntax comments are unnecessary
        return ""

    def do_nodes(self):
        s = ""
        for node in self.nodes:
            self.currentnode = node

            psshadeoption = getattr(node, 'psshadeoption', '')
            psshape = getattr(node, 'psshape', '')

            # detect node type, if psshape is not set
            if len(psshape) == 0:
                shape = getattr(node, 'shape', 'ellipse')
                # box       -> psframebox
                # circle    -> pscirclebox
                # rectangle -> psframebox
                psshape = "psframebox"
                if shape == "circle":
                    psshape = "pscirclebox"
                if shape == "ellipse":
                    psshape = "psovalbox"
                if shape == "triangle":
                    psshape = "pstribox"
                    # TODO incomplete

            width = getattr(node, 'width', '1')
            height = getattr(node, 'height', '1')
            psbox = getattr(node, 'psbox', 'false')

            color = getattr(node, 'color', '')
            fillcolor = getattr(node, 'fillcolor', '')

            if len(color) > 0:
                psshadeoption = "linecolor=" + color + "," + psshadeoption
            if len(fillcolor) > 0:
                psshadeoption = "fillcolor=" + fillcolor + "," + psshadeoption

            style = getattr(node, 'style', '')
            if len(style) > 0:
                if style == "dotted":
                    psshadeoption = "linestyle=dotted," + psshadeoption
                if style == "dashed":
                    psshadeoption = "linestyle=dashed," + psshadeoption
                if style == "solid":
                    psshadeoption = "linestyle=solid," + psshadeoption
                if style == "bold":
                    psshadeoption = "linewidth=2pt," + psshadeoption

            pos = getattr(node, 'pos')
            if not pos:
                continue
            x, y = pos.split(',')
            label = self.get_label(node)
            pos = "%sbp,%sbp" % (smart_float(x), smart_float(y))
            # TODO style

            sn = ""
            sn += self.output_node_comment(node)
            sn += self.start_node(node)
            if psbox == "false":
                sn += "\\rput(%s){\\rnode{%s}{\\%s[%s]{%s}}}\n" % \
                      (pos, tikzify(node.name), psshape, psshadeoption, label)
            else:
                sn += "\\rput(%s){\\rnode{%s}{\\%s[%s]{\parbox[c][%sin][c]{%sin}{\centering %s}}}}\n" % \
                      (pos, tikzify(node.name), psshape, psshadeoption, height, width, label)
            sn += self.end_node(node)
            s += sn
        self.body += s

    def do_edges(self):
        s = ""
        for edge in self.edges:
            s += self.draw_edge(edge)
        self.body += s

    def draw_edge(self, edge):
        s = ""
        edges = self.get_edge_points(edge)
        for arrowstyle, points in edges:
            # styles = []
            psarrow = getattr(edge, 'psarrow', '')

            if len(psarrow) == 0:
                stylestr = '-'
            else:
                stylestr = psarrow

            psedge = getattr(edge, 'psedge', 'ncline')
            psedgeoption = getattr(edge, 'psedgeoption', '')

            color = getattr(edge, 'color', '')
            fillcolor = getattr(edge, 'fillcolor', '')

            if len(color) > 0:
                psedgeoption = "linecolor=" + color + "," + psedgeoption
            if len(fillcolor) > 0:
                psedgeoption = "fillcolor=" + fillcolor + "," + psedgeoption

            style = getattr(edge, 'style', '')
            if len(style) > 0:
                if style == "dotted":
                    psedgeoption = "linestyle=dotted," + psedgeoption
                if style == "dashed":
                    psedgeoption = "linestyle=dashed," + psedgeoption
                if style == "solid":
                    psedgeoption = "linestyle=solid," + psedgeoption
                if style == "bold":
                    psedgeoption = "linewidth=2pt," + psedgeoption

            pslabel = getattr(edge, 'pslabel', 'ncput')
            pslabeloption = getattr(edge, 'pslabeloption', '')
            label = getattr(edge, 'label', '')
            headlabel = getattr(edge, 'headlabel', '')
            taillabel = getattr(edge, 'taillabel', '')

            src = tikzify(edge.get_source())
            dst = tikzify(edge.get_destination())
            s = "\\%s[%s]{%s}{%s}{%s}\n" % (psedge, psedgeoption, stylestr, src, dst)
            if len(label) != 0:
                s += "\\%s[%s]{%s}\n" % (pslabel, pslabeloption, label)
            if len(headlabel) != 0:
                pslabelhead = 'npos=0.8,' + pslabeloption
                s += "\\%s[%s]{%s}\n" % (pslabel, pslabelhead, headlabel)
            if len(taillabel) != 0:
                pslabeltail = 'npos=0.2,' + pslabeloption
                s += "\\%s[%s]{%s}\n" % (pslabel, pslabeltail, taillabel)
        return s

    def start_node(self, node):
        return ""

    def end_node(self, node):
        return ""