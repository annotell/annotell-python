import setuptools
import re

URL = 'https://github.com/annotell/annotell-python'
LONG_DESCRIPTION = """annotell-core
============
Python 3 library providing tools Annotell
To install with pip run ``pip install annotell-core``
"""

# resolve version by opening file. We cannot do import duing install
# since the package does not yet exist
with open('annotell/core/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

package_name = 'annotell-core'
setuptools.setup(
    name = package_name,
    packages = ["annotell", "annotell/core"],
    version = version,
    description = 'Annotell Core lib',
    long_description = LONG_DESCRIPTION,
    author = 'Annotell',
    author_email = ['michel.edkrantz@annotell.com',
                    'daniel@annotell.com'],
    license = 'MIT',
    url = URL,
    download_url = '%s/tarball/%s' % (URL, version),
    keywords = ['API', 'Annotell'],
    install_requires = [
        'requests>=2.5'
    ],
    include_package_data=True,
    package_data={
        '': ['*.rst', 'LICENSE'],
    },
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License'
        'Programming Language :: Python',
    ],
)
