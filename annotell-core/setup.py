from setuptools import setup, find_namespace_packages
import re

URL = 'https://github.com/annotell/annotell-python'
LONG_DESCRIPTION = """annotell-core
============
Python 3 library providing tools Annotell
To install with pip run ``pip install annotell-core``
"""

package_name = 'annotell-core'

# resolve version by opening file. We cannot do import during install
# since the package does not yet exist
with open('annotell/core/__init__.py', 'r') as fd:
    match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                      fd.read(), re.MULTILINE)
    version = match.group(1) if match else None

if not version:
    raise RuntimeError('Cannot find version information')

# https://packaging.python.org/guides/packaging-namespace-packages/
namespaces = ["annotell"]
packages = find_namespace_packages(include=['annotell.*'])

# Should be one of:
# 'Development Status :: 3 - Alpha'
# 'Development Status :: 4 - Beta'
# 'Development Status :: 5 - Production/Stable'
release_status = "Development Status :: 3 - Alpha"

setup(
    name=package_name,
    packages=packages,
    namespace_packages=namespaces,
    version=version,
    description='Annotell Core Lib',
    long_description=LONG_DESCRIPTION,
    author='Annotell',
    author_email=['michel.edkrantz@annotell.com',
                  'daniel@annotell.com'],
    license='MIT',
    url=URL,
    download_url='%s/tarball/%s' % (URL, version),
    keywords=['API', 'Annotell'],
    install_requires=[
        'requests>=2.5'
    ],
    include_package_data=True,
    package_data={
        '': ['*.rst', 'LICENSE'],
    },
    classifiers=[
        release_status,
        'License :: OSI Approved :: MIT License'
        'Programming Language :: Python',
    ],
)
