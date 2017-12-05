# hiss(w)
The [SolarSoftware](http://www.lmsal.com/solarsoft/) (SSW) stack contains nearly every piece of software a solar physicist needs. While libraries like [Astropy](http://www.astropy.org/), [SunPy](http://sunpy.org/), and [ChiantiPy](https://github.com/chianti-atomic/ChiantiPy) provide Python equivalents to many of these IDL packages, there's still a lot of functionality only available in SSW and not enough hours in the day to rewrite it all in Python.

**hissw** (pronounced hiss **or** hiss-SSW) is a (*VERY*) lightweight (~1 file) package that allows you to write IDL scripts (either inline or in a separate file) which use your installed SSW packages and return the results to your local Python namespace. hissw uses Jinja2 templates to generate SSW startup scripts and then runs your IDL code in the background. You can also use Jinja syntax to inject arguments from Python into IDL. The results are then saved to a file and then loaded back in using the amazing [`readsav()` function in `scipy.io`](https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.io.readsav.html).

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

