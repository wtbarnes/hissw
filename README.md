# :snake: :sunny: hiss(w)
[![Build Status](https://travis-ci.org/wtbarnes/hissw.svg?branch=master)](https://travis-ci.org/wtbarnes/hissw)

Include those pesky SSWIDL scripts in your Python workflow. See the [docs](https://wtbarnes.github.io/hissw/) for more info.

## Install
hissw depends on the following Python packages,

* [Jinja2](http://jinja.pocoo.org/docs/dev/)
* [scipy](https://docs.scipy.org/doc/)

The best way to install these is with [conda](https://www.anaconda.com/download/). You'll also need a local install of IDL and the [Solarsoft library](http://www.lmsal.com/solarsoft/). Then, install hissw from GitHub,

```shell
$ git clone https://github.com/wtbarnes/hissw.git
$ cd hissw && python setup.py install
```

**Note: hissw relies on executing several shell commands in the background and as a consequence Windows is not supported.** 

## Reporting Issues and Contributing
Open an [issue on GitHub](https://github.com/wtbarnes/hissw/issues) to report a problem. [Pull requests](https://github.com/wtbarnes/hissw/pulls) welcome.
