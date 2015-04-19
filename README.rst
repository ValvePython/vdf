|pypi| |license| |coverage| |master_build|

VDF is Valve's KeyValue text file format

https://developer.valvesoftware.com/wiki/KeyValues

The module works just like ``json`` to convert VDF to a dict, and vise-versa.


Known Issues
------------

- order is not preserved due to using ``dict``
- there are known files that contain duplicate keys


Install
-----------

You can grab the latest release from https://pypi.python.org/pypi/vdf or via ``pip``

.. code:: bash

    pip install vdf


Usage
-----------

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


.. |pypi| image:: https://img.shields.io/pypi/v/vdf.svg?style=flat&label=latest%20version
    :target: https://pypi.python.org/pypi/vdf
    :alt: Latest version released on PyPi

.. |license| image:: https://img.shields.io/pypi/l/vdf.svg?style=flat&label=license
    :target: https://pypi.python.org/pypi/vdf
    :alt: MIT License

.. |coverage| image:: https://img.shields.io/coveralls/rossengeorgiev/vdf-python/master.svg?style=flat
    :target: https://coveralls.io/r/rossengeorgiev/vdf-python?branch=master
    :alt: Test coverage

.. |master_build| image:: https://img.shields.io/travis/rossengeorgiev/vdf-python/master.svg?style=flat&label=master%20build
    :target: http://travis-ci.org/rossengeorgiev/vdf-python
    :alt: Build status of master branch
