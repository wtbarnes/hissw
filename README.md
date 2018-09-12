# :snake: :sunny: hiss(w)

[![Build Status](https://travis-ci.org/wtbarnes/hissw.svg?branch=master)](https://travis-ci.org/wtbarnes/hissw)
[![PyPI](https://img.shields.io/pypi/v/hissw.svg)](https://pypi.python.org/pypi)

Include those pesky SSWIDL scripts in your Python workflow. See the [docs](https://wtbarnes.github.io/hissw/) for more info.

## Install

To install hissw,

```shell
$ pip install hissw
```

which will automatically install the package and its dependencies. hissw depends on the [Jinja2](http://jinja.pocoo.org/docs/dev/) and [scipy](https://docs.scipy.org/doc/) libraries. You can also install these manually with [conda](https://www.anaconda.com/download/) or from PyPI, i.e. `pip install <package-name>`. Additionally, you'll need a local install of IDL and the [Solarsoft library](http://www.lmsal.com/solarsoft/).

Alternatively, you can install hissw from GitHub,

```shell
$ git clone https://github.com/wtbarnes/hissw.git
$ cd hissw && python setup.py install
```

and then run the tests to make sure everything is working alright,
```
$ pytest
```

**Note: hissw relies on executing several shell commands. This has not been tested on Windows.** 

## Reporting Issues and Contributing

Open an [issue on GitHub](https://github.com/wtbarnes/hissw/issues) to report a problem. [Pull requests](https://github.com/wtbarnes/hissw/pulls) welcome.
