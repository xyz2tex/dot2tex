Installation guide
==================

Dependencies
------------

The following software and modules are required to run dot2tex:

- Python_ 2.4+
- pyparsing_. Version 1.4.8 or later is recommended.
- Graphviz_. A recent version is required.
- preview_. A LaTeX package for extracting parts of a document. A free-standing part of the `preview-latex`_/`AUCTeX`_ bundle.
- `PGF/TikZ`_ version 2.0 or later.

Users have reported problems using dot2tex with old versions of pyparsing and Graphviz.

A natural companion to dot2tex is `the dot2texi LaTeX package`_ for embedding graphs directly in your LaTeX source code.

Dot2tex was developed and tested using Python_ 2.4 and 2.5. However, dot2tex will probably run fine using Python 2.3.


From source
-----------

Download a zip or a tarball from the download_ page. It is also available on CTAN_. Unpack the file to a directory and run ``python`` on the ``setup.py`` file::

    $ python setup.py install

This will create a dot2tex module in your Python module directory and a wrapper script in your ``SCRIPTS`` directory. Note that a few warnings will be displayed. You can safely ignore them. The warnings are shown because there is some extra information in the ``setup.py`` file that distutils does not understand.

Using easy_install
------------------

The easiest way to install dot2tex is to use `easy_install`_::

    $ easy_install dot2tex

The command will locate dot2tex and download it automatically. Note that documentation and examples are not installed by default. `Easy_install`_ will also create a wrapper script or EXE file for you and install dependencies if necessary.


.. _download: http://www.fauskes.net/code/dot2tex/download/

Binary packages
---------------

Binary packages are available for Debian_ and OpenSUSE_.

Development version
-------------------

The development version of ``dot2tex`` is  available from a `Mercurial repository`_ hosted at Google code. To get the code you can use the following command::

    hg clone https://dot2tex.googlecode.com/hg/ dot2tex

.. _Debian: http://packages.qa.debian.org/d/dot2tex.html
.. _OpenSUSE: http://download.opensuse.org/repositories/home:/jimfunk/
.. _Mercurial repository: http://code.google.com/p/dot2tex/source

.. include:: common.inc