# :snake: :sunny: hiss(w)
Include those pesky SSWIDL scripts in your Python workflow.

The SSWIDL (or [SolarSoftware](http://www.lmsal.com/solarsoft/)) stack contains nearly every piece of software a solar physicist needs. While libraries like [Astropy](), [SunPy](), and [ChiantiPy]() provide Python equivalents to many of these IDL packages, there's still a lot of functionality only available in SSW and not enough hours in the day to rewrite it all in Python.

hissw is a lightweight package that allows you to write IDL scripts (either inline or in a separate file) which use your installed SSW packages and return the results to your local Python namespace. See below for an example of how to use hissw.

hissw does all of this using the Jinja2 templates to generate SSW startup scripts and then running your code in the background. The results are then saved to a file and then loaded back in using the amazing [`readsav()` function in `scipy.io`](https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.io.readsav.html).

## Install
hissw depends on the following packages,

* [Jinja2](http://jinja.pocoo.org/docs/dev/)
* [scipy](https://docs.scipy.org/doc/)

The best way to install these is with [conda](https://www.anaconda.com/download/). Then, install hissw from GitHub,

```shell
$ git clone https://github.com/wtbarnes/hissw.git
$ cd hissw && python setup.py install
```

## Example

## Reporting Issues and Contributing
Open an [issue on GitHub](https://github.com/wtbarnes/hissw/issues) to report a problem. [Pull requests](https://github.com/wtbarnes/hissw/pulls) welcome.
