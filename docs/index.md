# hiss(w)

The [SolarSoftware](http://www.lmsal.com/solarsoft/) (SSW) stack contains nearly every piece of software a solar physicist needs. While libraries like [Astropy](http://www.astropy.org/), [SunPy](http://sunpy.org/), and [ChiantiPy](https://github.com/chianti-atomic/ChiantiPy) provide Python equivalents to many of these IDL packages, there's still a lot of functionality only available in SSW.

**hissw** (*hiss* (like a snake) + SSW) is a (*VERY*) lightweight (~1 file) Python package that allows you to write IDL scripts (either inline or in a separate file) which use your installed SSW packages and return the results to your local Python namespace. hissw uses Jinja2 templates to generate SSW startup scripts and then runs your IDL code using `subprocess`, i.e. the shell. You can also use Jinja syntax to inject arguments from Python into IDL. The results are then saved to a file and then loaded back in using the amazing [`readsav()` function in `scipy.io`](https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.io.readsav.html).

## Install and Configuration

hissw has two dependencies,

1. `jinja2` a powerful templating engine
2. `scipy` standard scientific tools for Python

To install hissw and its dependencies,

```shell
$ pip install hissw
```

You can also install the above dependencies with [`conda`](https://www.anaconda.com/download/). Alternatively, you can download and install the source yourself,

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

Note that if you do not create this file, **you will be required to specify it each time you setup a SSW script environment**, using the keywords `ssw_home` and `idl_home`.

If you've downloaded the source, you can run the tests (requires `pytest` to be installed) to make sure everything is working properly,

```shell
$ pytest
```

## Bridging the IDL-Python Gap the Bad Way...

hissw is a hack, albeit a clever one. In general, the methodology employed here (round-tripping everything in memory to disk) is a *terrible idea*. There's no shared memory between Python and IDL or anything fancy like that. If you're interested in something more complicated (and harder to install), you may want to check out the more official [Python-to-IDL bridge](https://www.harrisgeospatial.com/docs/Python.html).

## Word(s) of Caution

* Python-3 only
* A local install of of IDL **and** SSW is required
* Relies on executing shell commands with the `subprocess` module. I've only tested this on Linux and macOS. **Windows users may encounter difficulties.**
* Be careful when injecting large pieces of data into your IDL script as this must be written to a file. It may be better to load it at (IDL) runtime.
* Widgets and plotting will (likely) **not** work
* This has **not** been tested extensively against all SSW/IDL functionality. There are likely many cases where hissw will not work. [Bug reports](https://github.com/wtbarnes/hissw/issues) and [pull requests](https://github.com/wtbarnes/hissw/pulls) welcome!

