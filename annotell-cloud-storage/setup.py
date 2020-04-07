from setuptools import setup, find_namespace_packages
import re

URL = 'https://github.com/annotell/annotell-python'

package_name = 'annotell-cloud-storage'

with open('README.md') as f:
    LONG_DESCRIPTION = f.read()

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

setup(
    name=package_name,
    packages=packages,
    namespace_packages=["annotell"],
    version=version,
    description='Annotell Cloud Storage Lib',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author='Annotell',
    author_email='Michel Edkrantz <michel.edkrantz@annotell.com>',
    license='MIT',
    url=URL,
    download_url='%s/tarball/%s' % (URL, version),
    keywords=['API', 'Annotell'],
    install_requires=[
        'google-cloud-storage>=1.23.0,<2',
        'requests>2.20<3'
    ],
    python_requires='~=3.6',
    include_package_data=True,
    package_data={
        '': ['*.md', 'LICENSE'],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
    ],
)
