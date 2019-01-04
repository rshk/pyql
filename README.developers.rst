PyQL developer's guide
######################


Creating a release
==================

1. Update version number in ``setup.py``
2. Update version number in ``docs/conf.py``
3. Commit changes, eg::

     git add setup.py docs/conf.py
     git commit -m '0.2.1 ...'

4. Tag the version, eg::

     git tag -a -m 'Version 0.2.1' v0.2.1

5. Push changes to GitHub::

     git push
     git push --tags

6. Release on PyPI::

     rm -rf dist
     python setup.py sdist bdist_wheel
     twine upload dist/*
