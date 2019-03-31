import logging
import os
import re
import sys
import tempfile
from subprocess import Popen, PIPE

from . import dotparsing
from .utils import nsplit, chunks, escape_texchars, smart_float, replace_tags, is_multiline_label

# initialize logging module
log = logging.getLogger("dot2tex")


DEFAULT_TEXTENCODING = 'utf8'
DEFAULT_OUTPUT_FORMAT = 'pgf'
DEFAULT_LABEL_XMARGIN = 0.11
DEFAULT_LABEL_YMARGIN = 0.055
DEFAULT_EDGELABEL_XMARGIN = 0.01
DEFAULT_EDGELABEL_YMARGIN = 0.01


def create_xdot(dotdata, prog='dot', options=''):
    """Run a graph through Graphviz and return an xdot-version of the graph"""
    # The following code is from the pydot module written by Ero Carrera
    progs = dotparsing.find_graphviz()

    # prog = 'dot'
    if progs is None:
        log.error('Could not locate Graphviz binaries')
        return None
    if not prog in progs:
        log.error('Invalid prog=%s', prog)
        raise NameError('The %s program is not recognized. Valid values are %s' % (prog, list(progs)))

    tmp_fd, tmp_name = tempfile.mkstemp()
    os.close(tmp_fd)
    if os.sys.version_info[0] >= 3:
        with open(tmp_name, 'w', encoding="utf8") as f:
            f.write(dotdata)
    else:
        with open(tmp_name, 'w') as f:
            f.write(dotdata)
    output_format = 'xdot'
    progpath = '"%s"' % progs[prog].strip()
    cmd = progpath + ' -T' + output_format + ' ' + options + ' ' + tmp_name
    log.debug('Creating xdot data with: %s', cmd)
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, close_fds=(sys.platform != 'win32'))
    (stdout, stderr) = (p.stdout, p.stderr)
    try:
        data = stdout.read()
    finally:
        stdout.close()

    try:
        error_data = stderr.read()
        if error_data:
            if b'Error:' in error_data:
                log.error("Graphviz returned with the following message: %s", error_data)
            else:
                # Graphviz raises a lot of warnings about too small labels,
                # we therefore log them using log.debug to "hide" them
                log.debug('Graphviz STDERR %s', error_data)
    finally:
        stderr.close()
    p.kill()
    p.wait()

    os.unlink(tmp_name)
    return data


def parse_dot_data(dotdata):
    """Wrapper for pydot.graph_from_dot_data

    Redirects error messages to the log.
    """
    parser = dotparsing.DotDataParser()
    try:
        graph = parser.parse_dot_data(dotdata)
    except dotparsing.ParseException:
        raise
    finally:
        del parser
    log.debug('Parsed graph:\n%s', str(graph))
    return graph


def parse_drawstring(drawstring):
    """Parse drawstring and returns a list of draw operations"""

    # The draw string parser is a bit clumsy and slow
    def doeE(c, s):
        """Parse ellipse"""
        # E x0 y0 w h  Filled ellipse ((x-x0)/w)^2 + ((y-y0)/h)^2 = 1
        # e x0 y0 w h  Unfilled ellipse ((x-x0)/w)^2 + ((y-y0)/h)^2 = 1
        tokens = s.split()[0:4]
        if not tokens:
            return None
        points = [float(t) for t in tokens]
        didx = sum(len(t) for t in tokens) + len(points) + 1
        return didx, (c, points[0], points[1], points[2], points[3])

    def doPLB(c, s):
        """Parse polygon, polyline og B-spline"""
        # P n x1 y1 ... xn yn  Filled polygon using the given n points
        # p n x1 y1 ... xn yn  Unfilled polygon using the given n points
        # L n x1 y1 ... xn yn  Polyline using the given n points
        # B n x1 y1 ... xn yn  B-spline using the given n control points
        # b n x1 y1 ... xn yn  Filled B-spline using the given n control points
        tokens = s.split()
        n = int(tokens[0])
        points = [float(t) for t in tokens[1:n * 2 + 1]]
        didx = sum(len(t) for t in tokens[1:n * 2 + 1]) + n * 2 + 2
        npoints = nsplit(points, 2)
        return didx, (c, npoints)

    def doCS(c, s):
        """Parse fill or pen color"""
        # C n -c1c2...cn  Set fill color.
        # c n -c1c2...cn  Set pen color.
        # Graphviz uses the following color formats:
        # "#%2x%2x%2x"    Red-Green-Blue (RGB)
        #   "#%2x%2x%2x%2x" Red-Green-Blue-Alpha (RGBA)
        #   H[, ]+S[, ]+V   Hue-Saturation-Value (HSV) 0.0 <= H,S,V <= 1.0
        #   string  color name
        tokens = s.split()
        n = int(tokens[0])
        tmp = len(tokens[0]) + 3
        d = s[tmp:tmp + n]
        didx = len(d) + tmp + 1
        return didx, (c, d)

    def doFont(c, s):
        # F s n -c1c2...cn
        # Set font. The font size is s points. The font name consists of
        # the n characters following '-'.
        tokens = s.split()
        size = tokens[0]
        n = int(tokens[1])
        tmp = len(size) + len(tokens[1]) + 4
        d = s[tmp:tmp + n]
        didx = len(d) + tmp
        return didx, (c, size, d)

    def doText(c, s):
        # T x y j w n -c1c2...cn
        # Text drawn using the baseline point (x,y). The text consists of the
        # n characters following '-'. The text should be left-aligned
        # (centered, right-aligned) on the point if j is -1 (0, 1), respectively.
        # The value w gives the width of the text as computed by the library.
        tokens = s.split()
        x, y, j, w = tokens[0:4]
        n = int(tokens[4])
        tmp = sum(len(t) for t in tokens[0:5]) + 7
        text = s[tmp:tmp + n]
        didx = len(text) + tmp
        return didx, [c, x, y, j, w, text]

    cmdlist = []
    stat = {}
    idx = 0
    s = drawstring.strip().replace('\\', '')
    while idx < len(s) - 1:
        didx = 1
        c = s[idx]
        stat[c] = stat.get(c, 0) + 1
        try:
            if c in ('e', 'E'):
                didx, cmd = doeE(c, s[idx + 1:])
                cmdlist.append(cmd)
            elif c in ('p', 'P', 'L', 'b', 'B'):
                didx, cmd = doPLB(c, s[idx + 1:])
                cmdlist.append(cmd)
            elif c in ('c', 'C', 'S'):
                didx, cmd = doCS(c, s[idx + 1:])
                cmdlist.append(cmd)
            elif c == 'F':
                didx, cmd = doFont(c, s[idx + 1:])
                cmdlist.append(cmd)
            elif c == 'T':
                didx, cmd = doText(c, s[idx + 1:])
                cmdlist.append(cmd)
        except Exception as err:
            log.debug("Failed to parse drawstring %s\n%s", s, err.message)

        idx += didx
    return cmdlist, stat


def get_graphlist(gg, l=None):
    """Traverse a graph with subgraphs and return them as a list"""
    if not l:
        l = []
        outer = True
    else:
        outer = False
    l.append(gg)
    if gg.get_subgraphs():
        for g in gg.get_subgraphs():
            get_graphlist(g, l)
    if outer:
        return l


class DotConvBase(object):
    """Dot2TeX converter base"""

    def __init__(self, options=None):
        self.color = ""
        self.opacity = None
        try:
            self.template
        except AttributeError:
            self.template = options.get('template', '')
        self.textencoding = options.get('encoding', DEFAULT_TEXTENCODING)
        self.templatevars = {}
        self.body = ""
        if options.get('templatefile', ''):
            self.load_template(options['templatefile'])
        if options.get('template', ''):
            self.template = options['template']

        self.options = options or {}
        if options.get('texpreproc') or options.get('autosize'):
            self.dopreproc = True
        else:
            self.dopreproc = False

    def load_template(self, templatefile):
        try:
            with open(templatefile) as f:
                self.template = f.read()
        except:
            pass

    def convert_file(self, filename):
        """Load dot file and convert"""
        pass

    def start_fig(self):
        return ""

    def end_fig(self):
        return ""

    def draw_ellipse(self, drawop, style=None):
        return ""

    def draw_bezier(self, drawop, style=None):
        return ""

    def draw_polygon(self, drawop, style=None):
        return ""

    def draw_polyline(self, drawop, style=None):
        return ""

    def draw_text(self, drawop, style=None):
        return ""

    def output_node_comment(self, node):
        return "  %% Node: %s\n" % node.name

    def output_edge_comment(self, edge):
        src = edge.get_source()
        dst = edge.get_destination()
        if self.directedgraph:
            edge = '->'
        else:
            edge = '--'
        return "  %% Edge: %s %s %s\n" % (src, edge, dst)

    def set_color(self, node):
        return ""

    def set_style(self, node):
        return ""

    def draw_edge(self, edge):
        return ""

    def start_node(self, node):
        return ""

    def end_node(self, node):
        return ""

    def start_graph(self, graph):
        return ""

    def end_graph(self, graph):
        return ""

    def start_edge(self):
        return ""

    def end_edge(self):
        return ""

    def filter_styles(self, style):
        return style

    def convert_color(self, drawopcolor, pgf=False):
        """Convert color to a format usable by LaTeX and XColor"""
        # Graphviz uses the following color formats:
        # "#%2x%2x%2x"    Red-Green-Blue (RGB)
        #   "#%2x%2x%2x%2x" Red-Green-Blue-Alpha (RGBA)
        #   H[, ]+S[, ]+V   Hue-Saturation-Value (HSV) 0.0 <= H,S,V <= 1.0
        #   string  color name

        # Is the format RBG(A)?
        if drawopcolor.startswith('#'):
            t = list(chunks(drawopcolor[1:], 2))
            # parallell lines not yet supported
            if len(t) > 6:
                t = t[0:3]
            rgb = [(round((int(n, 16) / 255.0), 2)) for n in t]
            if pgf:
                colstr = "{rgb}{%s,%s,%s}" % tuple(rgb[0:3])
                opacity = "1"
                if len(rgb) == 4:
                    opacity = rgb[3]
                return colstr, opacity
            else:
                return "[rgb]{%s,%s,%s}" % tuple(rgb[0:3])

        elif (len(drawopcolor.split(' ')) == 3) or (len(drawopcolor.split(',')) == 3):
            # are the values space or comma separated?
            hsb = drawopcolor.split(',')
            if not len(hsb) == 3:
                hsb = drawopcolor.split(' ')
            if pgf:
                return "{hsb}{%s,%s,%s}" % tuple(hsb)
            else:
                return "[hsb]{%s,%s,%s}" % tuple(hsb)
        else:
            drawopcolor = drawopcolor.replace('grey', 'gray')
            drawopcolor = drawopcolor.replace('_', '')
            drawopcolor = drawopcolor.replace(' ', '')
            return drawopcolor

    def do_drawstring(self, drawstring, drawobj, texlbl_name="texlbl", use_drawstring_pos=False):
        """Parse and draw drawsting

        Just a wrapper around do_draw_op.
        """
        drawoperations, stat = parse_drawstring(drawstring)
        return self.do_draw_op(drawoperations, drawobj, stat, texlbl_name, use_drawstring_pos)

    def do_draw_op(self, drawoperations, drawobj, stat, texlbl_name="texlbl", use_drawstring_pos=False):
        """Excecute the operations in drawoperations"""
        s = ""
        for drawop in drawoperations:
            op = drawop[0]
            style = getattr(drawobj, 'style', None)
            # styles are not passed to the draw operations in the
            # duplicate mode
            if style and not self.options.get('duplicate'):
                # map Graphviz styles to backend styles
                style = self.filter_styles(style)
                styles = [self.styles.get(key.strip(), key.strip())
                          for key in style.split(',') if key]
                style = ','.join(styles)
            else:
                style = None

            if op in ['e', 'E']:
                s += self.draw_ellipse(drawop, style)
            elif op in ['p', 'P']:
                s += self.draw_polygon(drawop, style)
            elif op == 'L':
                s += self.draw_polyline(drawop, style)
            elif op in ['C', 'c']:
                s += self.set_color(drawop)
            elif op == 'S':
                s += self.set_style(drawop)
            elif op in ['B']:
                s += self.draw_bezier(drawop, style)
            elif op in ['T']:
                # Need to decide what to do with the text
                # Note that graphviz removes the \ character from the draw
                # string. Use \\ instead
                # Todo: Use text from node|edge.label or name
                # Todo: What about multiline labels?
                text = drawop[5]
                # head and tail label
                texmode = self.options.get('texmode', 'verbatim')
                if drawobj.attr.get('texmode', ''):
                    texmode = drawobj.attr['texmode']
                if texlbl_name in drawobj.attr:
                    # the texlbl overrides everything
                    text = drawobj.attr[texlbl_name]
                elif texmode == 'verbatim':
                    # verbatim mode
                    text = escape_texchars(text)
                    pass
                elif texmode == 'math':
                    # math mode
                    text = "$%s$" % text

                drawop[5] = text
                if self.options.get('alignstr', ''):
                    drawop.append(self.options.get('alignstr'))
                if stat['T'] == 1 and \
                        self.options.get('valignmode', 'center') == 'center':
                    # do this for single line only
                    # force centered alignment
                    drawop[3] = '0'
                    if not use_drawstring_pos:
                        if texlbl_name == "tailtexlbl":
                            pos = drawobj.attr.get('tail_lp') or \
                                  drawobj.attr.get('pos')
                        elif texlbl_name == "headtexlbl":
                            pos = drawobj.attr.get('head_lp') or \
                                  drawobj.attr.get('pos')
                        else:
                            pos = drawobj.attr.get('lp') or \
                                  drawobj.attr.get('pos')

                        if pos:
                            coord = pos.split(',')
                            if len(coord) == 2:
                                drawop[1] = coord[0]
                                drawop[2] = coord[1]
                            pass
                lblstyle = drawobj.attr.get('lblstyle')
                exstyle = drawobj.attr.get('exstyle', '')
                if exstyle:
                    if lblstyle:
                        lblstyle += ',' + exstyle
                    else:
                        lblstyle = exstyle
                s += self.draw_text(drawop, lblstyle)
        return s

    def do_nodes(self):
        s = ""
        for node in self.nodes:
            self.currentnode = node
            general_draw_string = node.attr.get('_draw_', "")
            label_string = node.attr.get('_ldraw_', "")

            drawstring = general_draw_string + " " + label_string

            if not drawstring.strip():
                continue
            # detect node type
            shape = node.attr.get('shape', '')
            if not shape:
                shape = 'ellipse'  # default
                # extract size information
            x, y = node.attr.get('pos', '').split(',')

            # width and height are in inches. Convert to bp units
            # w = float(node.attr['width']) * INCH2BP
            # h = float(node.attr['height']) * INCH2BP

            s += self.output_node_comment(node)
            s += self.start_node(node)
            s += self.do_drawstring(drawstring, node)
            s += self.end_node(node)
        self.body += s

    def get_edge_points(self, edge):
        # edge BNF
        # <edge>   :: <spline> (';' <spline>)*
        #   <spline> :: <endp>? <startp>? <point> <triple>+
        #   <point>  :: <x> ',' <y>
        #   <triple> :: <point> <point> <point>
        #   <endp>   :: "e" "," <x> "," <y>
        ##        spline ( ';' spline )*
        ##where spline  =   (endp)? (startp)? point (triple)+
        ##and triple    =   point point point
        ##and endp  =   "e,%d,%d"
        ##and startp    =   "s,%d,%d"
        ##If a spline has points p1 p2 p3 ... pn, (n = 1 (mod 3)), the points correspond to the control points of a B-spline from p1 to pn. If startp is given, it touches one node of the edge, and the arrowhead goes from p1 to startp. If startp is not given, p1 touches a node. Similarly for pn and endp.
        pos = edge.attr.get('pos')
        if pos:
            segments = pos.split(';')
        else:
            return []

        return_segments = []
        for pos in segments:
            points = pos.split(' ')
            # check direction
            arrow_style = '--'
            i = 0
            if points[i].startswith('s'):
                p = points[0].split(',')
                tmp = "%s,%s" % (p[1], p[2])
                if points[1].startswith('e'):
                    points[2] = tmp
                else:
                    points[1] = tmp
                del points[0]
                arrow_style = '<-'
                i += 1
            if points[0].startswith('e'):
                p = points[0].split(',')
                points.pop()
                points.append("%s,%s" % (p[1], p[2]))
                del points[0]
                arrow_style = '->'
                i += 1
            if i > 1:
                arrow_style = '<->'

            arrow_style = self.get_output_arrow_styles(arrow_style, edge)

            return_segments.append((arrow_style, points))

        return return_segments

    def do_edges(self):
        s = ""
        s += self.set_color(('cC', "black"))
        for edge in self.edges:
            general_draw_string = edge.attr.get('_draw_', "")
            label_string = edge.attr.get('_ldraw_', "")
            head_arrow_string = edge.attr.get('_hdraw_', "")
            tail_arrow_string = edge.attr.get('_tdraw_', "")
            tail_label_string = edge.attr.get('_tldraw_', "")
            head_label_string = edge.attr.get('_hldraw_', "")

            # Note that the order of the draw strings should be the same
            # as in the xdot output.
            drawstring = general_draw_string + " " + head_arrow_string + " " + tail_arrow_string \
                         + " " + label_string
            drawop, stat = parse_drawstring(drawstring)
            if not drawstring.strip():
                continue
            s += self.output_edge_comment(edge)
            if self.options.get('duplicate'):
                s += self.start_edge()
                s += self.do_draw_op(drawop, edge, stat)
                s += self.do_drawstring(tail_label_string, edge, "tailtexlbl")
                s += self.do_drawstring(head_label_string, edge, "headtexlbl")
                s += self.end_edge()
            else:
                s += self.draw_edge(edge)
                s += self.do_drawstring(label_string, edge)
                s += self.do_drawstring(tail_label_string, edge, "tailtexlbl")
                s += self.do_drawstring(head_label_string, edge, "headtexlbl")
        self.body += s

    def do_graph(self):
        general_draw_string = self.graph.attr.get('_draw_', "")
        label_string = self.graph.attr.get('_ldraw_', "")
        # Avoid filling background of graphs with white
        if general_draw_string.startswith('c 5 -white C 5 -white') \
                and not self.graph.attr.get('style'):
            general_draw_string = ''
        if getattr(self.graph, '_draw_', None):
            # bug
            general_draw_string = "c 5 -black " + general_draw_string  # self.graph._draw_
            pass
        drawstring = general_draw_string + " " + label_string
        if drawstring.strip():
            s = self.start_graph(self.graph)
            g = self.do_drawstring(drawstring, self.graph)
            e = self.end_graph(self.graph)
            if g.strip():
                self.body += s + g + e

    def set_options(self):
        # process options
        # Warning! If graph attribute is true and command line option is false,
        # the graph attribute will be used. Command line option should have
        # precedence.
        self.options['alignstr'] = self.options.get('alignstr', '') \
                                   or getattr(self.main_graph, 'd2talignstr', '')

        # Todo: bad!
        self.options['valignmode'] = getattr(self.main_graph, 'd2tvalignmode', '') \
                                     or self.options.get('valignmode', 'center')

    def convert(self, dotdata):
        # parse data processed by dot.
        log.debug('Start conversion')
        main_graph = parse_dot_data(dotdata)

        if not self.dopreproc and not hasattr(main_graph, 'xdotversion'):
            # Older versions of Graphviz does not include the xdotversion
            # attribute
            if not (dotdata.find('_draw_') > 0 or dotdata.find('_ldraw_') > 0):
                # need to convert to xdot format
                # Warning. Pydot will not include custom attributes
                log.info('Trying to create xdotdata')

                tmpdata = create_xdot(dotdata, self.options.get('prog', 'dot'),
                                      options=self.options.get('progoptions', ''))
                if tmpdata is None or not tmpdata.strip():
                    log.error('Failed to create xdotdata. Is Graphviz installed?')
                    sys.exit(1)
                log.debug('xdotdata:\n' + str(tmpdata))
                main_graph = parse_dot_data(tmpdata)
                log.debug('dotparsing graph:\n' + str(main_graph))
            else:
                # old version
                pass

        self.main_graph = main_graph
        self.pencolor = ""
        self.fillcolor = ""
        self.linewidth = 1
        # Detect graph type
        self.directedgraph = main_graph.directed

        if self.dopreproc:
            return self.do_preview_preproc()

        # Remove annoying square
        # Todo: Remove squares from subgraphs. See pgram.dot
        dstring = self.main_graph.attr.get('_draw_', "")
        if dstring:
            self.main_graph.attr['_draw_'] = ""

        self.set_options()

        # A graph can consists of nested graph. Extract all graphs
        graphlist = get_graphlist(self.main_graph, [])

        self.body += self.start_fig()

        # To get correct drawing order we need to iterate over the graphs
        # multiple times. First we draw the graph graphics, then nodes and
        # finally the edges.

        # todo: support the outputorder attribute
        for graph in graphlist:
            self.graph = graph
            self.do_graph()

        if True:
            self.nodes = list(main_graph.allnodes)
            self.edges = list(main_graph.alledges)
            if not self.options.get('switchdraworder'):
                self.do_edges()  # tmp
                self.do_nodes()
            else:
                self.do_nodes()
                self.do_edges()

        self.body += self.end_fig()
        return self.output()

    def clean_template(self, template):
        """Remove preprocsection or outputsection"""
        if not self.dopreproc and self.options.get('codeonly'):
            r = re.compile('<<startcodeonlysection>>(.*?)<<endcodeonlysection>>',
                           re.DOTALL | re.MULTILINE)
            m = r.search(template)
            if m:
                return m.group(1).strip()
        if not self.dopreproc and self.options.get('figonly'):
            r = re.compile('<<start_figonlysection>>(.*?)<<end_figonlysection>>',
                           re.DOTALL | re.MULTILINE)
            m = r.search(template)
            if m:
                return m.group(1)
            r = re.compile('<<startfigonlysection>>(.*?)<<endfigonlysection>>',
                           re.DOTALL | re.MULTILINE)
            m = r.search(template)
            if m:
                return m.group(1)

        if self.dopreproc:
            r = re.compile('<<startoutputsection>>.*?<<endoutputsection>>',
                           re.DOTALL | re.MULTILINE)
        else:
            r = re.compile('<<startpreprocsection>>.*?<<endpreprocsection>>',
                           re.DOTALL | re.MULTILINE)
            # remove codeonly and figonly section
        r2 = re.compile('<<start_figonlysection>>.*?<<end_figonlysection>>',
                        re.DOTALL | re.MULTILINE)
        tmp = r2.sub('', template)
        r2 = re.compile('<<startcodeonlysection>>.*?<<endcodeonlysection>>',
                        re.DOTALL | re.MULTILINE)
        tmp = r2.sub('', tmp)
        return r.sub('', tmp)

    def init_template_vars(self):
        variables = {}
        # get bounding box
        bbstr = self.main_graph.attr.get('bb', '')
        if bbstr:
            bb = bbstr.split(',')
            variables['<<bbox>>'] = "(%sbp,%sbp)(%sbp,%sbp)\n" % (
                smart_float(bb[0]), smart_float(bb[1]), smart_float(bb[2]), smart_float(bb[3]))
            variables['<<bbox.x0>>'] = bb[0]
            variables['<<bbox.y0>>'] = bb[1]
            variables['<<bbox.x1>>'] = bb[2]
            variables['<<bbox.y1>>'] = bb[3]
        variables['<<figcode>>'] = self.body.strip()
        variables['<<drawcommands>>'] = self.body.strip()
        variables['<<textencoding>>'] = self.textencoding
        docpreamble = (self.options.get('docpreamble', '')
                       or getattr(self.main_graph, 'd2tdocpreamble', ''))
        variables['<<docpreamble>>'] = docpreamble
        variables['<<figpreamble>>'] = self.options.get('figpreamble', '') \
                                       or getattr(self.main_graph, 'd2tfigpreamble', '%')
        variables['<<figpostamble>>'] = self.options.get('figpostamble', '') \
                                        or getattr(self.main_graph, 'd2tfigpostamble', '')
        variables['<<graphstyle>>'] = self.options.get('graphstyle', '') \
                                      or getattr(self.main_graph, 'd2tgraphstyle', '')
        variables['<<margin>>'] = self.options.get('margin', '0pt')
        variables['<<startpreprocsection>>'] = variables['<<endpreprocsection>>'] = ''
        variables['<<startoutputsection>>'] = variables['<<endoutputsection>>'] = ''
        if self.options.get('gvcols'):
            variables['<<gvcols>>'] = "\input{gvcols.tex}"
        else:
            variables['<<gvcols>>'] = ""
        self.templatevars = variables

    def output(self):
        self.init_template_vars()
        template = self.clean_template(self.template)
        code = replace_tags(template, self.templatevars,
                            self.templatevars)
        return code

    def get_label(self, drawobj, label_attribute="label", tex_label_attribute="texlbl"):
        text = ""
        texmode = self.options.get('texmode', 'verbatim')
        if getattr(drawobj, 'texmode', ''):
            texmode = drawobj.texmode
        text = getattr(drawobj, label_attribute, None)

        # log.warning('text %s %s',text,str(drawobj))

        if text is None or text.strip() == '\\N':
            if not isinstance(drawobj, dotparsing.DotEdge):
                text = getattr(drawobj, 'name', None) or \
                       getattr(drawobj, 'graph_name', '')
                text = text.replace("\\\\", "\\")
            else:
                text = ''
        elif text.strip() == '\\N':
            text = ''
        else:
            text = text.replace("\\\\", "\\")

        if getattr(drawobj, tex_label_attribute, ''):
            # the texlbl overrides everything
            text = drawobj.texlbl
        elif texmode == 'verbatim':
            # verbatim mode
            text = escape_texchars(text)
            pass
        elif texmode == 'math':
            # math mode
            text = "$%s$" % text

        return text

    def get_node_preproc_code(self, node):
        return node.attr.get('texlbl', '')

    def get_edge_preproc_code(self, edge, attribute="texlbl"):
        return edge.attr.get(attribute, '')

    def get_graph_preproc_code(self, graph):
        return graph.attr.get('texlbl', '')

    def get_margins(self, element):
        """Return element margins"""
        margins = element.attr.get('margin')

        if margins:
            margins = margins.split(',')
            if len(margins) == 1:
                xmargin = ymargin = float(margins[0])
            else:
                xmargin = float(margins[0])
                ymargin = float(margins[1])
        else:
            # use default values
            if isinstance(element, dotparsing.DotEdge):
                xmargin = DEFAULT_EDGELABEL_XMARGIN
                ymargin = DEFAULT_EDGELABEL_YMARGIN
            else:
                xmargin = DEFAULT_LABEL_XMARGIN
                ymargin = DEFAULT_LABEL_YMARGIN
        return xmargin, ymargin

    # Todo: Add support for head and tail labels!
    # Todo: Support rect nodes if possible.
    def do_preview_preproc(self):
        # setDotAttr(self.maingraph)
        self.init_template_vars()
        template = self.clean_template(self.template)
        template = replace_tags(template, self.templatevars,
                                self.templatevars)
        pp = TeXDimProc(template, self.options)
        usednodes = {}
        usededges = {}
        usedgraphs = {}

        # iterate over every element in the graph
        counter = 0
        for node in self.main_graph.allnodes:
            name = node.name
            if node.attr.get('fixedsize', '') == 'true' \
                    or node.attr.get('style', '') in ['invis', 'invisible']:
                continue
            if node.attr.get('shape', '') == 'record':
                log.warning('Record nodes not supported in preprocessing mode: %s', name)
                continue
            texlbl = self.get_label(node)

            if texlbl:
                node.attr['texlbl'] = texlbl
                code = self.get_node_preproc_code(node)
                pp.add_snippet(name, code)

            usednodes[name] = node

        for edge in dotparsing.flatten(self.main_graph.alledges):
            if not edge.attr.get('label') and not edge.attr.get('texlbl') and not edge.attr.get("headlabel") \
                    and not edge.attr.get("taillabel"):
                continue
            # Ensure that the edge name is unique.
            name = edge.src.name + edge.dst.name + str(counter)
            if is_multiline_label(edge):
                continue
            label = self.get_label(edge)
            headlabel = self.get_label(edge, "headlabel", "headtexlbl")
            taillabel = self.get_label(edge, "taillabel", "tailtexlbl")
            if label:
                name = edge.src.name + edge.dst.name + str(counter)
                edge.attr['texlbl'] = label
                code = self.get_edge_preproc_code(edge)
                pp.add_snippet(name, code)

            if headlabel:
                headlabel_name = name + "headlabel"
                edge.attr['headtexlbl'] = headlabel
                code = self.get_edge_preproc_code(edge, "headtexlbl")
                pp.add_snippet(headlabel_name, code)

            if taillabel:
                taillabel_name = name + "taillabel"
                edge.attr['tailtexlbl'] = taillabel
                code = self.get_edge_preproc_code(edge, "tailtexlbl")
                pp.add_snippet(taillabel_name, code)

            counter += 1
            usededges[name] = edge

        for graph in self.main_graph.allgraphs:
            if not graph.attr.get('label') and not graph.attr.get('texlbl'):
                continue
            # Make sure that the name is unique
            name = graph.name + str(counter)

            counter += 1
            label = self.get_label(graph)
            graph.attr['texlbl'] = label
            code = self.get_graph_preproc_code(graph)
            pp.add_snippet(name, code)
            usedgraphs[name] = graph

        ok = pp.process()

        if not ok:
            errormsg = """\
Failed to preprocess the graph.
Is the preview LaTeX package installed? ((Debian package preview-latex-style)
To see what happened, run dot2tex with the --debug option.
"""
            log.error(errormsg)
            sys.exit(1)

        for name, item in usednodes.items():
            if not item.attr.get('texlbl'):
                continue
            node = item
            hp, dp, wt = pp.texdims[name]
            if self.options.get('rawdim'):
                # use dimensions from preview.sty directly
                node.attr['width'] = wt
                node.attr['height'] = hp + dp
                node.attr['label'] = " "
                node.attr['fixedsize'] = 'true'
                self.main_graph.allitems.append(node)
                continue

            xmargin, ymargin = self.get_margins(node)
            ht = hp + dp
            minwidth = float(item.attr.get('width') or DEFAULT_NODE_WIDTH)
            minheight = float(item.attr.get('height') or DEFAULT_NODE_HEIGHT)
            if self.options.get('nominsize'):
                width = wt + 2 * xmargin
                height = ht + 2 * ymargin
            else:
                if (wt + 2 * xmargin) < minwidth:
                    width = minwidth
                else:
                    width = wt + 2 * xmargin
                height = ht
                if ((hp + dp) + 2 * ymargin) < minheight:
                    height = minheight
                else:
                    height = ht + 2 * ymargin
            # Treat shapes with equal width and height differently
            # Warning! Rectangles will not always fit inside a circle
            #          Should use the diagonal.
            if item.attr.get('shape', '') in ['circle', 'Msquare', 'doublecircle', 'Mcircle']:
                if wt < height and width < height:
                    width = height
                else:
                    height = width

            node.attr['width'] = width
            node.attr['height'] = height
            node.attr['label'] = " "

            node.attr['fixedsize'] = 'true'
            self.main_graph.allitems.append(node)

        for name, item in usededges.items():
            edge = item
            hp, dp, wt = pp.texdims[name]
            xmargin, ymargin = self.get_margins(edge)
            labelcode = '<<<table border="0" cellborder="0" cellpadding="0">' \
                        '<tr><td fixedsize="true" width="%s" height="%s">a</td>' \
                        '</tr></table>>>'
            if "texlbl" in edge.attr:
                edge.attr['label'] = labelcode % ((wt + 2 * xmargin) * 72, (hp + dp + 2 * ymargin) * 72)
            if "tailtexlbl" in edge.attr:
                hp, dp, wt = pp.texdims[name + "taillabel"]
                edge.attr['taillabel'] = labelcode % ((wt + 2 * xmargin) * 72, (hp + dp + 2 * ymargin) * 72)
            if "headtexlbl" in edge.attr:
                hp, dp, wt = pp.texdims[name + "headlabel"]
                edge.attr['headlabel'] = labelcode % ((wt + 2 * xmargin) * 72, (hp + dp + 2 * ymargin) * 72)

        for name, item in usedgraphs.items():
            graph = item
            hp, dp, wt = pp.texdims[name]
            xmargin, ymargin = self.get_margins(graph)
            labelcode = '<<<table border="0" cellborder="0" cellpadding="0">' \
                        '<tr><td fixedsize="true" width="%s" height="%s">a</td>' \
                        '</tr></table>>>'
            graph.attr['label'] = labelcode % ((wt + 2 * xmargin) * 72, (hp + dp + 2 * ymargin) * 72)

        self.main_graph.attr['d2toutputformat'] = self.options.get('format',
                                                                   DEFAULT_OUTPUT_FORMAT)
        graphcode = str(self.main_graph)
        graphcode = graphcode.replace('<<<', '<<')
        graphcode = graphcode.replace('>>>', '>>')
        return graphcode

    def get_output_arrow_styles(self, arrow_style, edge):
        return arrow_style


DEFAULT_GRAPHLABEL_XMARGIN = 0.01
DEFAULT_GRAPHLABEL_YMARGIN = 0.01
DEFAULT_NODE_WIDTH = 0.75
DEFAULT_NODE_HEIGHT = 0.5
dimext = r"""
^.*? Preview:\s Snippet\s
(?P<number>\d*)\s ended.
\((?P<ht>\d*)\+(?P<dp>\d*)x(?P<wd>\d*)\)"""


class TeXDimProc:
    """Helper class for for finding the size of TeX snippets

    Uses preview.sty
    """

    # Produce document
    # Create a temporary directory
    # Compile file with latex
    # Parse log file
    # Update graph with with and height parameters
    # Clean up
    def __init__(self, template, options):
        self.template = template
        self.snippets_code = []
        self.snippets_id = []
        self.options = options
        self.dimext_re = re.compile(dimext, re.MULTILINE | re.VERBOSE)
        pass

    def add_snippet(self, snippet_id, code):
        """A a snippet of code to be processed"""
        self.snippets_id.append(snippet_id)
        self.snippets_code.append(code)

    def process(self):
        """Process all snippets of code with TeX and preview.sty

        Results are stored in the texdimlist and texdims class attributes.
        Returns False if preprocessing fails
        """
        import shutil

        if len(self.snippets_code) == 0:
            log.warning('No labels to preprocess')
            return True
        self.tempdir = tempfile.mkdtemp(prefix='dot2tex')
        log.debug('Creating temporary directroy %s' % self.tempdir)
        self.tempfilename = os.path.join(self.tempdir, 'dot2tex.tex')
        log.debug('Creating temporary file %s' % self.tempfilename)
        s = ""
        for n in self.snippets_code:
            s += "\\begin{preview}%\n"
            s += n.strip() + "%\n"
            s += "\end{preview}%\n"
        with open(self.tempfilename, 'w') as f:
            f.write(self.template.replace('<<preproccode>>', s))
        with open(self.tempfilename, 'r') as f:
            s = f.read()
        log.debug('Code written to %s\n' % self.tempfilename + s)
        self.parse_log_file()
        shutil.rmtree(self.tempdir)
        log.debug('Temporary directory and files deleted')
        if self.texdims:
            return True
        else:
            return False
            # cleanup

    def parse_log_file(self):
        logfilename = os.path.splitext(self.tempfilename)[0] + '.log'
        tmpdir = os.getcwd()
        os.chdir(os.path.split(logfilename)[0])
        if self.options.get('usepdflatex'):
            command = 'pdflatex -interaction=nonstopmode %s' % self.tempfilename
        else:
            command = 'latex -interaction=nonstopmode %s' % self.tempfilename
        log.debug('Running command: %s' % command)

        p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, close_fds=(sys.platform != 'win32'))
        (stdout, stderr) = (p.stdout, p.stderr)
        try:
            data = stdout.read()
            log.debug("stdout from latex\n %s", data)
        finally:
            stdout.close()

        try:
            error_data = stderr.read()
            if error_data:
                log.debug('latex STDERR %s', error_data)
        finally:
            stderr.close()
        p.kill()
        p.wait()

        with open(logfilename, 'r') as f:
            logdata = f.read()
        log.debug('Logfile from LaTeX run: \n' + logdata)
        os.chdir(tmpdir)

        texdimdata = self.dimext_re.findall(logdata)
        log.debug('Texdimdata: ' + str(texdimdata))
        if len(texdimdata) == 0:
            log.error('No dimension data could be extracted from dot2tex.tex.')
            self.texdims = None
            return

        c = 1.0 / 4736286
        self.texdims = {}
        self.texdimlist = [(float(i[1]) * c, float(i[2]) * c, float(i[3]) * c) for i in texdimdata]
        self.texdims = dict(zip(self.snippets_id, self.texdimlist))