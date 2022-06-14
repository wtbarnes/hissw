# :snake: :sunny: hiss(w)

[![GHA](https://github.com/wtbarnes/hissw/workflows/Deploy%20Docs/badge.svg)](https://github.com/wtbarnes/hissw/actions)
[![PyPI](https://img.shields.io/pypi/v/hissw.svg)](https://pypi.python.org/pypi)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4039915.svg)](https://doi.org/10.5281/zenodo.5519495)


Easily integrate SSWIDL into your Python workflows.
See the [docs](https://wtbarnes.github.io/hissw/) for more info.

## Install

To install hissw,

```shell
$ pip install hissw
```

which will automatically install the package and its dependencies.
hissw depends on the [Jinja2](http://jinja.pocoo.org/docs/dev/) and [scipy](https://docs.scipy.org/doc/) libraries. 
You can also install these manually with [conda](https://www.anaconda.com/download/) or from PyPI, i.e. `pip install <package-name>`.
Additionally, you'll need a local install of IDL and the [Solarsoft library](http://www.lmsal.com/solarsoft/).

Alternatively, you can install hissw from GitHub,

```shell
$ git clone https://github.com/wtbarnes/hissw.git
$ cd hissw && python -m pip install -e[all,test]
```

and then run the tests to make sure everything is working alright. Note that you must specify paths to SSW and IDL appropriately.

```shell
$ pytest --ssw-home=<path to top of SSW tree> --idl-home=<path to top level dir of IDL install>
```

**Note: hissw relies on executing several shell commands. This has not been tested on Windows.**

## Citing `hissw`

If you use `hissw` in your work, please use the following citation,

```bibtex
@software{will_barnes_2022_6640421,
  author       = {Will Barnes and
                  Bin Chen},
  title        = {wtbarnes/hissw: v2.0},
  month        = jun,
  year         = 2022,
  publisher    = {Zenodo},
  version      = {v2.0},
  doi          = {10.5281/zenodo.6640421},
  url          = {https://doi.org/10.5281/zenodo.6640421}
}
```

## Reporting Issues and Contributing

Open an [issue on GitHub](https://github.com/wtbarnes/hissw/issues) to report a problem.
[Pull requests](https://github.com/wtbarnes/hissw/pulls) welcome.
