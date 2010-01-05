import os,sys

from os.path import join,basename,splitext,normpath,abspath

from string import Template
import logging
import unittest

# intitalize logging module
log = logging.getLogger("test_graphparser")
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
# set a format which is simpler for console use
formatter = logging.Formatter('%(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
log.addHandler(console)

#LOG_FILENAME = splitext(__file__)[0]+'.log'
#hdlr = logging.FileHandler(LOG_FILENAME)
#log.addHandler(hdlr)
#formatter = logging.Formatter('%(levelname)-8s %(message)s')
#hdlr.setFormatter(formatter)
#log.setLevel(logging.INFO)

# Directory with test files
BASE_DIR = join(abspath(os.path.dirname(__file__)),"")
TESTFILES_DIR = "testgraphs/"
TESTFILES_PATH = join(BASE_DIR,TESTFILES_DIR)
DEST_DIR = join(BASE_DIR,'tmp/')


def runcmd(syscmd):
    #err = os.system(syscmd)
    sres = os.popen(syscmd)
    resdata =  sres.read()
    err = sres.close()
    if err:
        log.warning('Failed to run command:\n%s',syscmd)
        log.debug('Output:\n%s',resdata)
    return err

def meps(filename):
    fn = splitext(filename)[0]
    s = "latex -halt-on-error -interaction nonstopmode %s.tex" % fn
    err = runcmd(s)
    if err: return err
    if sys.platform=='win32':
        s = "dvips -Ppdf -G0 -D600 -E* -o%s.eps %s.dvi" % (fn,fn)
        err = runcmd(s)
        if err: return err
        s = "epstool --bbox --copy --output %s_tmp.eps %s.eps" % (fn,fn)
        err = runcmd(s)
        if err: return err
        try:
            os.remove("%s.eps" % fn)
            os.remove("%s.dvi" % fn)
            os.remove("%s.aux" % fn)
            os.remove("%s.log" % fn)
        #os.remove("%s.pgf" % fn)

        except:
            raise
        os.rename("%s_tmp.eps" % fn,"%s.eps" % fn)
        s = "epstopdf %s.eps" % fn
        err = runcmd(s)
    else:
        s = "dvips %s.dvi" % fn
        err = runcmd(s)
        s = "ps2eps -B -f %s.ps" % fn
        err = runcmd(s)
        if err: return err
        s = "epstopdf %s.eps" % fn
        err = runcmd(s)

    return err





testdotfile = normpath(join(BASE_DIR,'testgraphs/','concentrate.dot'))


textemplate = r"""
\documentclass{article}
\usepackage{tikz}

\usepackage{verbatim}
\usepackage[active,tightpage]{preview}
\setlength\PreviewBorder{0pt}%
\PreviewEnvironment{tikzpicture}

\begin{document}
\begin{tikzpicture}
\matrix[every node/.style={draw=black!20}] (mtrx) {
\node[label=below:original] {\includegraphics{$testfile}}; & \node[label=below:tikz] {\includegraphics{${testfile}_tikz}};\\
\node[label=below:pgf] {\includegraphics{${testfile}_pgf}}; & \node[label=below:pst] {\includegraphics{${testfile}_pst}};\\
};
\node[above] at (mtrx.north) {$testfile};
\end{tikzpicture}
\end{document}
"""

s = Template(textemplate)

def create_pdf(texfile,use_pdftex=True):
    if not splitext(texfile)[1]:
        fn = basename(texfile)+'.tex'
    else:
        fn = basename(texfile)
    if sys.platform=='win32':
        syscmd = 'texify --pdf --clean %s' % (fn)
    else:
        syscmd = 'pdflatex -halt-on-error -interaction nonstopmode %s' % (fn)
    err = runcmd(syscmd)
    return err




def create_original(dotfilename):
    # Process the file with dot and create a pdf
    #   dot -Tps2 file.dot > file.ps
    #   ps2pdf file.ps
    basefn = basename(dotfilename)
    destfile = normpath(join(DEST_DIR,splitext(basefn)[0]))
    cwd = os.getcwd()
    os.chdir(os.path.dirname(destfile))
    syscmd = 'dot -Tps2 %s > %s.ps' % (dotfilename,destfile)
    err = runcmd(syscmd)
    syscmd = 'ps2pdf %s.ps' % (destfile)
    #os.remove("%s.ps" % destfile)
    err = runcmd(syscmd)
    os.chdir(cwd)
    return err

def create_tikz(dotfilename):
    basefn = basename(dotfilename)
    destfile = normpath(join(DEST_DIR,splitext(basefn)[0]))+'_tikz'
    syscmd = 'dot2tex -ftikz --crop %s > %s.tex' % (dotfilename,destfile)
    err = runcmd(syscmd)
    cwd = os.getcwd()
    os.chdir(os.path.dirname(destfile))
    err = create_pdf(destfile)
    #os.remove(destfile)
    os.chdir(cwd)
    return err

def create_pgf(dotfilename):
    basefn = basename(dotfilename)
    destfile = normpath(join(DEST_DIR,splitext(basefn)[0]))+'_pgf'
    syscmd = 'dot2tex --crop %s > %s.tex' % (dotfilename,destfile)
    err = runcmd(syscmd)
    cwd = os.getcwd()
    os.chdir(os.path.dirname(destfile))
    err = create_pdf(destfile)
    #os.remove(destfile)
    os.chdir(cwd)
    return err

def create_pst(dotfilename):
    basefn = basename(dotfilename)
    destfile = normpath(join(DEST_DIR,splitext(basefn)[0]))+'_pst'
    syscmd = 'dot2tex -fpst %s > %s.tex' % (dotfilename,destfile)
    err = runcmd(syscmd)
    cwd = os.getcwd()
    os.chdir(os.path.dirname(destfile))
    #syscmd = 'meps %s' % (basename(destfile))
    #err = runcmd(syscmd)
    err = meps(basename(destfile))
    os.chdir(cwd)
    return err

def create_comparefile(dotfilename):
    basefn = basename(dotfilename)
    destfile = normpath(join(DEST_DIR,splitext(basefn)[0]))+'_cmp.tex'
    f = open(destfile,'w')
    f.write(s.substitute(testfile=splitext(basefn)[0]))
    f.close()
    cwd = os.getcwd()
    os.chdir(os.path.dirname(destfile))
    err = create_pdf(destfile)
    #if sys.platform=='win32':
    #    syscmd = "start %s" % splitext(basename(destfile))[0]+'.pdf'
    #    err = runcmd(syscmd)

    os.chdir(cwd)


# Get a dot file to test

# Create a tikz version
# create a pgf version
# create a pstricks version
# Combine the images in a latex file

def compare_output(testdotfile):
    err = create_original(testdotfile)
    if err: return err
    err = create_tikz(testdotfile)
    if err: return err
    err = create_pgf(testdotfile)
    if err: return err
    err = create_pst(testdotfile)
    if err: return err
    err = create_comparefile(testdotfile)
    return err


# From
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/541096
def confirm(prompt=None, resp=False):
    """prompts for yes or no response from the user. Returns True for yes and
    False for no.

    'resp' should be set to the default value assumed by the caller when
    user simply types ENTER.

    >>> confirm(prompt='Create Directory?', resp=True)
    Create Directory? [y]|n:
    True
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y:
    False
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: y
    True

    """

    if prompt is None:
        prompt = 'Confirm'

    if resp:
        prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
    else:
        prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')

    while True:
        ans = raw_input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print 'please enter y or n.'
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False


def run_rendertest(dotfile):
    print "Processing %s" % dotfile
    err = compare_output(normpath(join(TESTFILES_PATH,dotfile)))
    if err:
        return False
    else:
        return True
    s = "Is %s correct?" % (dotfile)
    return confirm(s,resp=True)


class RenderTest(unittest.TestCase):
    cmplist = []
    def setUp(self):
        if not os.path.exists(DEST_DIR):
            os.mkdir(DEST_DIR)

    def test_autosize(self):
        fn = 'autosize.dot'
        self.failUnless(run_rendertest(fn))
        self.cmplist.append(fn)

    def test_compassports(self):
        fn = 'compassports.dot'
        self.failUnless(run_rendertest(fn))
        self.cmplist.append(fn)

    def test_concentrate(self):
        fn = 'concentrate.dot'
        self.failUnless(run_rendertest(fn))
        self.cmplist.append(fn)

    def test_escstr(self):
        fn = 'escstr.dot'
        self.failUnless(run_rendertest(fn))
        self.cmplist.append(fn)

    def test_invis(self):
        fn = 'invis.dot'
        self.failUnless(run_rendertest(fn))
        self.cmplist.append(fn)

    def test_nodenames(self):
        fn = 'nodenames.dot'
        self.failUnless(run_rendertest(fn))
        self.cmplist.append(fn)

    def test_colors(self):
        fn = 'colors.dot'
        self.failUnless(run_rendertest(fn))
        self.cmplist.append(fn)

    def test_zzzzzzzzzzzfinal(self):
        os.chdir(DEST_DIR)
        flist =[]
        for dotfile in self.cmplist:
            basefn = basename(dotfile)
            flist.append(normpath(join(splitext(basefn)[0]))+'_cmp.pdf')
        s = "pdftk %s cat output testrenders.pdf dont_ask" % " ".join(flist)
        err = runcmd(s)
        self.failIf(err)
        if sys.platform=='win32':
            syscmd = "start %s" % 'testrenders.pdf'
            err = runcmd(syscmd)
        print "Check testrenders.pdf manually"

testdotfile2 = normpath(join(TESTFILES_PATH,'compassports.dot'))

if __name__ == '__main__':
    #compare_output(testdotfile2)
    unittest.main()
