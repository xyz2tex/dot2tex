.. _using-dot2tex-as-a-module:

Using dot2tex as a module
=========================

It is possible to load dot2tex as a module for use in other Python programs. Here is a basic example:

.. sourcecode:: python

    import dot2tex
    testgraph = """
    digraph G {
        a -> b -> c -> a;
    }
    """
    texcode = dot2tex.dot2tex(testgraph, format='tikz', crop=True)

The ``dot2tex`` function is the main interface:

.. sourcecode:: python

    dot2tex(dotsource,**kwargs)

It takes the following input arguments:

    ======================  ===================================================
    Argument                Description
    ======================  ===================================================
    ``dotsource``           A string containing a DOT or XDOT graph.
    ``**kwargs``            An arbitrary number of conversion options passed as
                            keyword arguments
    ======================  ===================================================

The function returns the resulting LaTeX code as a string.

The supported options are the same as the :ref:`command line options <command-line-options>` (long version). Here are a few examples:

.. sourcecode:: python

    import dot2tex as d2t
    texcode = d2t.dot2tex(testgraph, format='tikz', crop=True)
    texcode = d2t.dot2tex(testgraph, preproc=True,figonly=True)
    texcode = d2t.dot2tex(testgraph, debug=True)

Option values are either strings or booleans. Note that some of the command line options are not relevant when using dot2tex as a module.

To specify a template you can use the ``template`` option like this:

.. sourcecode:: python

    import dot2tex
    mytemplate = "<<drawcommands>>"
    texcode = dot2tex.dot2tex(graph, template = mytemplate)


.. _module-debugging:

Debugging
---------

You can set ``debug=True`` to create a detailed log useful for debugging. To retrieve the content of the log you can use the ``get_logstream`` function. It will return a ``StringIO`` instance. You can then use the ``getvalue()`` class method to get the actual text. Example:

.. sourcecode:: python

    import dot2tex
    texcode = dot2tex.dot2tex(testgraph, debug=True)
    logstream = dot2tex.get_logstream()
    print logstream.getvalue()


.. _positions-output-format:

The ``positions`` output format
-------------------------------

When you use dot2tex as a module you have access to the special ``positions`` output format if you use ``format=positions``.
The ``dot2tex`` function will then return dictionary with node name as key and a (x, y) tuple with the
center position of the node as value:

.. sourcecode:: python

    >>> import dot2tex
    >>> testgraph = """
    ... digraph G {
    ...    a -> b -> c -> a;
    ... }
    """
    >>> dot2tex.dot2tex(testgraph, format='positions')
    {'a': [54, 162], 'b': [27, 90], 'c': [54, 18]}




