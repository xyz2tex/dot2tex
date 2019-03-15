Installation guide
==================

Dependencies
------------

The following software and modules are required to run dot2tex:

- Python_ 2.7 or 3.x.
- pyparsing_. Version 1.4.8 or later is recommended.
- Graphviz_. A recent version is required.
- preview_. A LaTeX package for extracting parts of a document. A free-standing part of the `preview-latex`_/`AUCTeX`_ bundle.
- `PGF/TikZ`_ version 2.0 or later.

Users have reported problems using dot2tex with old versions of pyparsing and Graphviz.

A natural companion to dot2tex is `the dot2texi LaTeX package <dot2texi_>`_ for embedding graphs directly in your LaTeX source code.


Using pip or easy_install
-------------------------

The easiest way to install dot2tex is to use `pip`_ (recommended) or `easy_install`_::

    $ pip install dot2tex

or `easy_install`_::

    $ easy_install dot2tex

If you are on Linux or Mac OS X you may have to call `pip`_ or `easy_install`_ using ``sudo``::

    $ sudo pip install dot2tex

The commands will locate dot2tex and download it automatically. Note that documentation and examples are not installed by default. `Pip` and `easy_install`_ will also create a wrapper script or EXE file for you and install dependencies if necessary.


.. _download: https://pypi.python.org/pypi/dot2tex#downloads

Binary packages
---------------

Binary packages are available for Debian_ and OpenSUSE_.


From source
-----------

Download a zip or a tarball from the download_ page. Unpack the file to a directory and run ``python`` on the ``setup.py`` file::

    $ python setup.py install

This will create a dot2tex module in your Python modue directory and a wrapper script in your ``SCRIPTS`` directory. Note that a few warnings will be displayed. You can safely ignore them. The warnings are shown because there is some extra information in the ``setup.py`` file that distutils does not understand.


Development version
-------------------

The development version of ``dot2tex`` is  `hosted on GitHub <https://github.com/kjellmf/dot2tex>`_. To get the code you can use the following command::

    git clone https://github.com/kjellmf/dot2tex.git

.. _Debian: http://packages.qa.debian.org/d/dot2tex.html
.. _OpenSUSE: https://build.opensuse.org/package/show/home:jimfunk/dot2tex


.. include:: common.inc