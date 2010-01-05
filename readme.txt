dot2tex - A Graphviz to LaTeX converter
=======================================

Copyright (C) 2007-2008 Kjell Magne Fauske
License: MIT (See LICENSE for details.)
Version: 2.8.7
URL: http://www.fauskes.net/code/dot2tex/

Dot2tex is a tool for converting graphs rendered by Graphviz to formats
that can be used with LaTeX.

Installation
============

Before you install dot2tex you have to have a working Python environment
installed on your system. Dot2tex has been developed and tested with
Python 2.4, but it will probably run fine using Python 2.3. In addition
you'll need the following modules:

    * pyparsing (http://pyparsing.wikispaces.com/). A recent version is required.
      Older version like for instance 1.3.2 does not work with dot2tex.
    * preview (http://www.ctan.org/tex-archive/help/Catalogue/entries/preview.html)
      A stand-alone part of the preview-latex/AUCTeX bundle.
      Required for preprocessing graphs with LaTeX.
    * PGF/TikZ 2.0 or later required. 

Note. If you have dot2tex version 2.5.0 or older installed, please remove the old
version of the dot2tex.py file in your SCRIPTS directory before you install the
latest dot2tex version. Otherwise the new dot2tex wrapper script will try to load
the dot2tex.py as a module.

From source
-----------

Download a zip or a tarball from the download_ page. It is also available on
CTAN_. Unpack the file to a directory and run ``python`` on the ``setup.py``
file::

    $ python setup.py install

This will create a dot2tex module in your Python module directory and a wrapper
script in your ``SCRIPTS`` directory. Note that a few warnings will be
displayed. You can safely ignore them. The warnings are shown because there is
some extra information in the ``setup.py`` file that distutils does not understand.

.. _download: http://www.fauskes.net/code/dot2tex/download/
.. _CTAN: http://www.ctan.org/tex-archive/help/Catalogue/entries/dot2tex.html

Using easy_install
------------------

The easiest way to install dot2tex is to use `easy_install`_::

    $ easy_install dot2tex

The command will locate dot2tex and download it automatically. Note that
documentation and examples are not installed by default. `Easy_install`_
will also create a wrapper script or EXE file for you and install dependencies
if necessary.

.. _easy_install: http://peak.telecommunity.com/DevCenter/EasyInstall

Binary packages
---------------

Binary packages are available for Debian_ and OpenSUSE_.

.. _Debian: http://packages.qa.debian.org/d/dot2tex.html
.. _OpenSUSE: http://download.opensuse.org/repositories/home:/jimfunk/

Development version
-------------------

The development version of ``dot2tex`` is  available from a
`Subversion repository`_ hosted at Google code. To get the code you can use the following command::

    svn checkout http://dot2tex.googlecode.com/svn/trunk/ dot2tex


.. _Subversion repository: http://code.google.com/p/dot2tex/source


What's new in version 2.8.7
===========================

Bugfixes:

    - Edges with no edge points are now properly handled.  
    - Fixed handling of stderr when creating xdot data.
    - Exceptions are now caught when accessing invalid win32 registry keys.
    - Updated Graphviz registry key.
    - Fixed templates so that crop code is not inserted when preprocessing the graph.

For a full list of changes see changelog.txt
