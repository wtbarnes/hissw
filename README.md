# :snake: :sunny: hiss(w)
[![Build Status](https://travis-ci.org/wtbarnes/hissw.svg?branch=master)](https://travis-ci.org/wtbarnes/hissw)

Include those pesky SSWIDL scripts in your Python workflow. See the [docs](https://wtbarnes.github.io/hissw/) for more info.

## Install
hissw depends on the following Python packages,

* [Jinja2](http://jinja.pocoo.org/docs/dev/)
* [scipy](https://docs.scipy.org/doc/)

The best way to install these is with [conda](https://www.anaconda.com/download/) or from PyPI, i.e. `pip install <package-name>`. You'll also need a local install of IDL and the [Solarsoft library](http://www.lmsal.com/solarsoft/). To install hissw,

```shell
$ pip install hissw
```

which will automatically install the package and its dependencies. Alternatively, you can install hissw from GitHub,

```shell
$ git clone https://github.com/wtbarnes/hissw.git
$ cd hissw && python setup.py install
```

You can then run the tests to make sure everything is working alright,
```
$ pytest
```

**Note: hissw relies on executing several shell commands. This has not been tested on Windows.** 

## Reporting Issues and Contributing
Open an [issue on GitHub](https://github.com/wtbarnes/hissw/issues) to report a problem. [Pull requests](https://github.com/wtbarnes/hissw/pulls) welcome.
