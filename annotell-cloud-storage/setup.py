from setuptools import setup, find_namespace_packages
import re

URL = 'https://github.com/annotell/annotell-python'

package_name = 'annotell-cloud-storage'

LONG_DESCRIPTION = f"""{package_name}
============
Python 3 library providing Annotell tools
To install with pip run ``pip install {package_name}``
"""

# resolve version by opening file. We cannot do import during install
# since the package does not yet exist
with open('annotell/cloud_storage/__init__.py', 'r') as fd:
    match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                      fd.read(), re.MULTILINE)
    version = match.group(1) if match else None

if not version:
    raise RuntimeError('Cannot find version information')

# https://packaging.python.org/guides/packaging-namespace-packages/
packages = find_namespace_packages(include=['annotell.*'])

# Should be one of:
# 'Development Status :: 3 - Alpha'
# 'Development Status :: 4 - Beta'
# 'Development Status :: 5 - Production/Stable'
release_status = "Development Status :: 3 - Alpha"

setup(
    name=package_name,
    packages=packages,
    namespace_packages=["annotell"],
    version=version,
    description='Annotell Cloud Storage Lib',
    long_description=LONG_DESCRIPTION,
    author='Annotell',
    author_email=['michel.edkrantz@annotell.com'],
    license='MIT',
    url=URL,
    download_url='%s/tarball/%s' % (URL, version),
    keywords=['API', 'Annotell'],
    install_requires=[
        'google-cloud-storage>=1.23.0,<2'
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
