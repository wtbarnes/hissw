The temperature response functions of the EUV channels of the Atmospheric Imaging Assembly (AIA) are used to understand the temperature of the plasma observed by the different telescopes on the instrument. 

While these are difficult to calculate, SSW provides a single simple routine to calculate them. The script below shows how you can easily calculate them using hissw and return the results to your current Python workspace and plot them with Matplotlib.

```python
import numpy as np
import matplotlib.pyplot as plt
import hissw
script = """
response = aia_get_response(/{{ flags | join(',/') }})
; Pull needed elements out of structure
logt = response.logte
resp94 = response.a94.tresp
resp131 = response.a131.tresp
resp171 = response.a171.tresp
resp193 = response.a193.tresp
resp211 = response.a211.tresp
resp335 = response.a335.tresp
; Interpolate
interp_logt = {{ interp_logt }}
interp_resp94 = interpol(resp94,logte,interp_logte)
interp_resp131 = interpol(resp131,logte,interp_logte)
interp_resp171 = interpol(resp171,logte,interp_logte)
interp_resp193 = interpol(resp193,logte,interp_logte)
interp_resp211 = interpol(resp211,logte,interp_logte)
interp_resp335 = interpol(resp335,logte,interp_logte)
"""
interp_logt = np.linspace(5,8,1000)
flags = ['temp','dn','timedepend_date','evenorm']
ssw = hissw.ScriptMaker(ssw_packages=['sdo/aia'], ssw_paths=['aia'])
inputs = {'flags': flags, 'interp_logt': interp_logt.tolist()}
ssw_resp = ssw.run(script, args=inputs)
# Plotting
t = 10.**ssw_resp['logte']
interp_t = 10.**interp_logte
for i,channel in enumerate([94,131,171,193,211,335]):
    plt.plot(t, ssw_resp[f'resp{channel}'], 'o', color=f'C{i}', markevery=3)
    plt.plot(interp_t, ssw_resp[f'interp_resp{channel}'], '-', color=f'C{i}', label=f'{channel}')
plt.xlabel(r'$T$ [K]')
plt.ylabel('Response')
plt.xscale('log')
plt.yscale('log')
plt.ylim(1e-30,3e-24)
plt.legend()
plt.show()
```
![AIA Response Functions](../images/exAIA.png)