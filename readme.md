dot2tex - A Graphviz to LaTeX converter
=======================================

Copyright (C) 2006-2019 Kjell Magne Fauske

License: MIT (See LICENSE for details.)

Version: 2.12.dev

URL: https://github.com/kjellmf/dot2tex

Documentation: http://dot2tex.readthedocs.org/

Dot2tex is a tool for converting graphs rendered by Graphviz to formats
that can be used with LaTeX.

Installation
============

Before you install dot2tex you have to have a working Python environment
installed on your system. Dot2tex works with Python 2.7 and Python 3. In addition
you'll need the following modules:

* [pyparsing](https://github.com/pyparsing/pyparsing). A recent version is required.
      Older version like for instance 1.3.2 does not work with dot2tex.
* [preview](http://www.ctan.org/tex-archive/help/Catalogue/entries/preview.html)
      A stand-alone part of the preview-latex/AUCTeX bundle.
      Required for preprocessing graphs with LaTeX.
* PGF/TikZ 2.0 or later required.

Note. If you have dot2tex version 2.5.0 or older installed, please remove the old
version of the dot2tex.py file in your SCRIPTS directory before you install the
latest dot2tex version. Otherwise the new dot2tex wrapper script will try to load
the dot2tex.py as a module.

Using pip
---------

The easiest way to install dot2tex is to use [pip][]:

    $ pip install dot2tex

The command will locate dot2tex and download it automatically along with dependencies. Note that
documentation and examples are not installed by default. 

[pip]: http://www.pip-installer.org/en/latest/#

Binary packages
---------------

Binary packages are available for [Debian][] and [OpenSUSE][].

[Debian]: http://packages.qa.debian.org/d/dot2tex.html
[OpenSUSE]: http://download.opensuse.org/repositories/home:/jimfunk/

From source
-----------

Download a zip or a tarball from the download_ page. Unpack the file to a directory and run ``python`` on the ``setup.py``
file:

    $ python setup.py install

This will create a dot2tex module in your Python module directory and a wrapper
script in your ``SCRIPTS`` directory. Note that a few warnings will be
displayed. You can safely ignore them. The warnings are shown because there is
some extra information in the ``setup.py`` file that distutils does not understand.


Development version
-------------------

The development version of ``dot2tex`` is  [available on GitHub](https://github.com/kjellmf/dot2tex).

Contribute
==========

- Issue tracker: https://github.com/kjellmf/dot2tex/issues
- Source code: https://github.com/kjellmf/dot2tex

