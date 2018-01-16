Description
===========

.. _Sphinx: http://www.sphinx-doc.org
.. _virtualenv: https://virtualenv_.pypa.io

Le Tyran d'axilane - Michel Grimaud - ebook


Identification
--------------

- **Title:** Tyran Axilane
- **Description:** Le Tyran d'axilane - Michel Grimaud - ebook
- **GitHub:** https://github.com/tantale/tyran_axilane.git
- **Main page:** https://tantale.github.io/tyran_axilane/
- **Keywords:** epub


Install the project
-------------------

Install the **tyran_axilane** project in a virtualenv_ by running::

    # -- Clone the repository
    cd ~/workspace
    git clone https://github.com/tantale/tyran_axilane.git

    # -- Create a new Python executable
    cd ~/virtualenv
    virtualenv py-tyran_axilane
    source py-tyran_axilane/bin/activate

    # -- Install the dependencies (Sphinx and plugins)
    cd ~/workspace/tyran_axilane
    pip install .


Build the documentation
-----------------------

**tyran_axilane** is a Sphinx_ project.

Build **tyran_axilane** documentation by running::

    # -- Build the documentation
    cd ~/workspace/tyran_axilane
    python setup.py build_sphinx

The HTML documentation is then available in the ``dist/docs`` subdirectory.
You can open the index page: ``dist/docs/index.html``.


Release
-------

Before releasing: activate your virtualenv_ and move to the project's working directory::

    source ~/virtualenv/py-tyran_axilane/bin/activate
    cd ~/workspace/tyran_axilane

Prepare the next release: update the change log.

Check the release::

    python setup.py release

Commit and tag your release::

    # -- Bug fix or small improvement (spelling/typo): X.Y.Z => X.Y.Z+1
    bumpversion patch

    # -- Minor release (new articles): X.Y.Z => X.Y+1.0
    bumpversion minor

    # -- Major release (new features): X.Y.Z => X+1.0.0
    bumpversion major

Push the release::

    git push origin master --tags

Enjoy.