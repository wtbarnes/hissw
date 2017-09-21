import os
from distutils.core import setup

# create home directory
if not os.path.isdir(os.path.join(os.environ['HOME'], '.hissw')):
    os.mkdir(os.path.join(os.environ['HOME'], '.hissw'))

setup(
    name='hissw',
    license='MIT',
    version='0.1',
    author='Will Barnes',
    url='https://github.com/wtbarnes/hissw',
    package_data={'hissw': ['templates/*']},
    packages=['hissw'],
    author_email='will.t.barnes@gmail.com',
    description='SSWIDL code in your Python workflow'
)
