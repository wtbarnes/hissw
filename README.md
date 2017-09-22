# :snake: :sunny: hiss(w)
Include those pesky SSWIDL scripts in your Python workflow.

The SSWIDL (or [SolarSoftware](http://www.lmsal.com/solarsoft/)) stack contains nearly every piece of software a solar physicist needs. While libraries like [Astropy](http://www.astropy.org/), [SunPy](http://sunpy.org/), and [ChiantiPy](https://github.com/chianti-atomic/ChiantiPy) provide Python equivalents to many of these IDL packages, there's still a lot of functionality only available in SSW and not enough hours in the day to rewrite it all in Python.

**hissw** is a lightweight package that allows you to write IDL scripts (either inline or in a separate file) which use your installed SSW packages and return the results to your local Python namespace. hissw uses Jinja2 templates to generate SSW startup scripts and then runs your IDL code in the background. You can also use Jinja syntax to inject arguments from Python into IDL. The results are then saved to a file and then loaded back in using the amazing [`readsav()` function in `scipy.io`](https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.io.readsav.html).

## Install
hissw depends on the following Python packages,

* [Jinja2](http://jinja.pocoo.org/docs/dev/)
* [scipy](https://docs.scipy.org/doc/)

The best way to install these is with [conda](https://www.anaconda.com/download/). You'll also need a local install of IDL and the [Solarsoft library](http://www.lmsal.com/solarsoft/). Then, install hissw from GitHub,

```shell
$ git clone https://github.com/wtbarnes/hissw.git
$ cd hissw && python setup.py install
```

## Example
Calculate the 94 angstrom AIA response function, interpolate it to a Numpy array, and plot it in matplotlib.

```python
>>> import numpy as np
>>> import matplotlib.pyplot as plt
>>> import hissw
>>> script = """
response = aia_get_response(/{{ flags | join(',/') }})
logte = response.logte
resp94 = response.a94.tresp
interp_logte = {{ interp_logte }}
interp_resp94 = interpol(resp94,logte,interp_logte)
"""
>>> interp_logte = np.linspace(5,8,1000)
>>> flags = ['temp','dn','timedepend_date','evenorm']
>>> ssw = hissw.ScriptMaker(ssw_pkg_list=['sdo/aia'], ssw_path_list=['aia'])
>>> inputs = {'flags': flags, 'interp_logte': interp_logte.tolist()}
>>> ssw_resp = ssw.run([(script, inputs)])
>>> plt.plot(ssw_resp['logte'], ssw_resp['resp94'], 'o')
>>> plt.plot(interp_logte, ssw_resp['interp_resp94'], '--')
>>> plt.show()
```

## Reporting Issues and Contributing
Open an [issue on GitHub](https://github.com/wtbarnes/hissw/issues) to report a problem. [Pull requests](https://github.com/wtbarnes/hissw/pulls) welcome.
