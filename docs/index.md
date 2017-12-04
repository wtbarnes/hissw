# hiss(w)
hissw (pronounced hiss **or** hiss-SSW) provides a simple (and hack-y) way to interface with IDL and the SolarSoftware (SSW) stack using Python. This is especially useful if you are looking to gradually move away from IDL, but still need to make use of several tools in the SSWIDL ecosystem.

## Install and Configuration
Install the dependencies with `conda` (preferred) or `pip`,

```shell
$ conda install jinja2 scipy
```

and then install this package from GitHub via `pip`,

```shell
$ pip install git+git://github.com/wtbarnes/hissw.git
```

Alternatively, you can download and install the source yourself,

```shell
$ git clone https://github.com/wtbarnes/hissw.git
$ cd hissw
$ python setup.py install
```

Lastly, you can set the locations of your IDL and SSW installs in a configuration file located in `$HOME/.hissw/hisswrc`,

```ini
[hissw]
ssw_home=/path/to/ssw/tree
idl_home=/path/to/local/idl/install
```

## Bridging the IDL-Python Gap the Bad Way...

## Word(s) of Caution
* Unfortunately, a local install of of IDL **and** SSW is required
* Relies on executing shell commands with the `subprocess` module. As such, only Unix-like platforms (e.g. Linux, macOS) are supported
* Widgets and plotting will not work
* This has **not** been tested extensively against all SSW/IDL functionality. There are likely many cases where hissw will not work. [Bug reports](https://github.com/wtbarnes/hissw/issues) and [pull requests](https://github.com/wtbarnes/hissw/pulls) welcome!

