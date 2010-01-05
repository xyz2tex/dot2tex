"""
Script to build the the dot2tex examples.
"""


import re, os,shutil, glob,sys,logging

from os.path import join,basename,splitext,normpath,abspath

# intitalize logging module
log = logging.getLogger("test_graphparser")
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
# set a format which is simpler for console use
formatter = logging.Formatter('%(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
log.addHandler(console)


BASE_DIR = join(abspath(os.path.dirname(__file__)),"")
DEST_DIR = join(BASE_DIR,'exrender/')
EXAMPLES_DIR = normpath(abspath(join(BASE_DIR,"../examples/")))


def copyifnewer(source, dest):
    """Copy source to dest if dest is older than source or doesn't exists"""
    copy = False
    # Check that dest exists. Create dir if necessary
    if os.path.exists(dest):
        # get source's and dest's timpestamps
        source_ts = os.path.getmtime(source)
        dest_ts = os.path.getmtime(dest)
        # compare timestamps
        if source_ts > dest_ts: copy = True
    else:
        copy = True
        dir = os.path.dirname(dest)
        if dir != '' and not os.path.exists(dir):
            os.makedirs(dir)
    # copy source to dest
    if copy:
        shutil.copy2(source, dest)


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


def find_command(data):
    commands = re.findall(r"\$ ((?:.*?) dot2tex (?:.*?))$", data,
    re.MULTILINE|re.VERBOSE)
    if commands:
        return commands[0].strip()
    else:
        return None



def make_img(c, filenm, name):
        filename = os.path.splitext(filenm)[0]
        err = runcmd(c)
        if err:
            return err

        if (c.find('--crop') > -1):
            #os.system('del %s.png %s.jpg' % (name,name))
            err = create_pdf(filename)
            #print "using mppdf"
        else:
            err = meps(filename)

        return err




def build_gallery(filelist):
    #os.chdir(EXAMPLES_DIR)
    entrylist = []
    failedfiles = []
    for file in filelist:
        f = open(file,'r')
        data = f.read()
        f.close()
        entry = {}
        dirname, filename = os.path.split(file)
        os.chdir(dirname)
        name = os.path.splitext(filename)[0]



        command = find_command(data)

        if command:
            c = command.replace("dot2tex.py","dot2tex")
        else:
            c = "dot2tex %s > %s.tex" % (file, name)
        print c

        err = make_img(c,filename,'')
        if err:
            log.warning('Failed to build %s',filename)
            failedfiles.append(filename)
    return failedfiles




if __name__ == "__main__":
    filelist = []
    exdir= EXAMPLES_DIR
    os.chdir(exdir)
    for f in glob.glob("*.dot"):
        if not f.find('dot2tex-fig') > 0:
            src = os.path.join(exdir,f)
            dst = normpath(join(DEST_DIR,basename(src)))
            filelist.append(dst)
            copyifnewer(src,dst)



    failedfiles = build_gallery(filelist)
    if failedfiles:
        log.warning('Failed files: %s',failedfiles);
        sys.exit(1)
    else:
        print "All tests passed!"
        sys.exit(0)

    #filelist=['distances.dot','tikzshapes.dot']



