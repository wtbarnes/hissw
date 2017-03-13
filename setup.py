import os
from distutils.core import setup

# create home directory
if not os.path.isdir(os.path.join(os.environ['HOME'], '.hissw')):
    os.mkdir(os.path.join(os.environ['HOME'], '.hissw'))

setup(
    name='hissw',
    version='1.0dev',
    author='Will Barnes',
    url='https://github.com/wtbarnes/hissw',
    package_data={'hissw':['templates/*']},
    packages=['hissw']
)
