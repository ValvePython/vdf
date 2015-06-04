|pypi| |license| |coverage| |master_build|

VDF is Valve's KeyValue text file format

https://developer.valvesoftware.com/wiki/KeyValues

The module works just like ``json`` to convert VDF to a dict, and vise-versa.


Problems & solutions
--------------------

- There are known files that contain duplicate keys. This can be solved by
  creating a class inheriting from ``dict`` and implementing a way to handle
  duplicate keys. See example implementation of DuplicateOrderedDict_.

- By default parsing will return a ``dict``, which doesn't preserve nor guarantee
  key order due to `hash randomization`_. If key order is important then
  I suggest using ``collections.OrderedDict`` as mapper. See example below.


Install
-------

You can grab the latest release from https://pypi.python.org/pypi/vdf or via ``pip``

.. code:: bash

    pip install vdf


Example usage
-------------

.. code:: python

    import vdf

    # parsing vdf from file or string
    d = vdf.load(open('file.txt'))
    d = vdf.loads(vdf_text)
    d = vdf.parse(open('file.txt'))
    d = vdf.parse(vdf_text)

    # dumping dict as vdf to string
    vdf_text = vdf.dumps(d)
    indented_vdf = vdf.dumps(d, pretty=True)

    # dumping dict as vdf to file
    vdf.dump(d, open('file2.txt','w'), pretty=True)


Using ``OrderedDict`` to preserve key order.

.. code:: python

    import vdf
    from collections import OrderedDict

    # parsing vdf from file or string
    d = vdf.load(open('file.txt'), mapper=OrderedDict)
    d = vdf.loads(vdf_text, mapper=OrderedDict)


.. |pypi| image:: https://img.shields.io/pypi/v/vdf.svg?style=flat&label=latest%20version
    :target: https://pypi.python.org/pypi/vdf
    :alt: Latest version released on PyPi

.. |license| image:: https://img.shields.io/pypi/l/vdf.svg?style=flat&label=license
    :target: https://pypi.python.org/pypi/vdf
    :alt: MIT License

.. |coverage| image:: https://img.shields.io/coveralls/ValvePython/vdf/master.svg?style=flat
    :target: https://coveralls.io/r/ValvePython/vdf?branch=master
    :alt: Test coverage

.. |master_build| image:: https://img.shields.io/travis/ValvePython/vdf/master.svg?style=flat&label=master%20build
    :target: http://travis-ci.org/ValvePython/vdf
    :alt: Build status of master branch

.. _DuplicateOrderedDict: https://github.com/rossengeorgiev/dota2_notebooks/blob/master/DuplicateOrderedDict_for_VDF.ipynb

.. _hash randomization: https://docs.python.org/2/using/cmdline.html#envvar-PYTHONHASHSEED
