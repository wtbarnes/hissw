import os
import setuptools
from distutils.core import setup

# create home directory
if not os.path.isdir(os.path.join(os.environ['HOME'], '.hissw')):
    os.mkdir(os.path.join(os.environ['HOME'], '.hissw'))

with open('README.md', 'r') as f:
    long_description=f.read()

setup(
    name='hissw',
    license='MIT',
    version='1.2',
    description='Seamlessly integrate SSWIDL code into your Python workflow',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Will Barnes',
    author_email='will.t.barnes@gmail.com',
    url='https://github.com/wtbarnes/hissw',
    package_data={'hissw': ['templates/*']},
    packages=['hissw'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords='solar sun ssw solar-physics idl sswidl solarsoft',
    project_urls={
        'Documentation': 'https://wtbarnes.github.io/hissw/',
        'Source': 'https://github.com/wtbarnes/hissw/',
    },
    install_requires=['jinja2', 'scipy'],
    python_requires='>=3'
)
