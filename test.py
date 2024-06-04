"""
    Copyright 2020 Hendrik Weimer

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

print("idealgas: Begin loading modules")

from js import window, document

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import io
import base64

from DAB_Analysis_Functions import DAB
D = DAB()

import sympy as sp


print("test: End loading modules")

lstatus = document.getElementById("status")


file = '4.ome.tif'
data = D.imread(file)
image_mask_asyn, table_asyn, asyn_params = D.analyse_DAB(file, check_mask=0)
print(table_asyn)

def plot_image(image):
    imgdata = D.plot_masks(image)

    canvas = document.getElementById("canvas")

    ctx = canvas.getContext("2d")

    canvas.setAttribute("style", "background: url(\"data:image/png;base64,"
                        + str(base64.b64encode(imgdata), "ascii")
                        +  "\"); background-size: contain;")

    plt.clf()

    print("idealgas: exiting plot_main")

plot_image(data)
    # push_queue(update_distributions, "Computing distributions...")

# def push_queue(func, str):
#     lstatus.innerHTML = str
#     window.setTimeout(func, 100)
    
    
# 

# globals = dict()

# globals['beta'] = 1
# globals['m'] = 1
# globals['k'] = 1
# globals['N'] = 100

# globals['Z'] = 1
# globals['size'] = 100
# globals['size2'] = 1000

# p2d = np.zeros((globals['size'], globals['size']))
# p1d = np.zeros(globals['size'])

# pxlist = np.linspace(-5, 5, globals['size'])
# pvlist = np.linspace(-5, 5, globals['size'])

# xlist = [0]*globals['N']
# globals['vlist'] = [0]*globals['N']

# M_pixel = np.zeros((2, 2))
# globals['firstrun'] = 1

# globals['V'] = lambda x: 1/2*x**2
# globals['F'] = lambda x: -x

# globals['sx'] = 1
# globals['sv'] = 1

# def V(x):
#     return globals['V'](x)

# def F(x):
#     return globals['F'](x)

# def E(x, v):
#     return 1/2*globals['m']*v**2 + V(x)

# def xpdf(x):
#     return np.exp(-globals['beta']*V(x))/globals['Z']

# def vpdf(v):
#     m = globals['m']
#     beta = globals['beta']
#     return np.sqrt(beta*m/2/np.pi)*np.exp(-beta*m*v**2/2)

# def plotimg(id):
#     imgtag = document.getElementById(id)
#     img =  io.StringIO()
#     plt.savefig(img, format="svg")
#     img.seek(0)
#     imgdata = img.read()

#     imgtag.setAttribute("src","data:image/svg+xml;base64,"
#                         + str(base64.b64encode(imgdata.encode()), "ascii"))
#     plt.clf()


# def draw_circle(ctx, x, y, r=5):

#     pixelx, pixely = plt2pix(x, y)
#     ctx.beginPath()
#     ctx.arc(int(pixelx), int(pixely), r, 0, 2*np.pi)
#     ctx.fillStyle = 'blue'
#     ctx.fill()
#     ctx.stroke()
    

# def replot_canvas():

#     dt = 1/25
    
#     canvas = document.getElementById("canvas")
#     ctx = canvas.getContext("2d")
    
#     ctx.clearRect(0, 0, cwidth, cheight)

#     m = globals['m']

#     vlist = globals['vlist']

#     for i in range(globals['N']):

#         # Verlocity Verlet integration
#         at = F(xlist[i])/m
#         xlist[i] += vlist[i]*dt + 0.5*at*dt**2
#         adt = F(xlist[i])/m
#         vlist[i] += 0.5*(at+adt)*dt

#         draw_circle(ctx, xlist[i], E(xlist[i], vlist[i]))
    
# def plt2pix(x, y):

#     # Transforming the plt coordinates into HTML canvas pixels
    
#     pixelx = M_pixel[0][0] + x*(M_pixel[1][0]-M_pixel[0][0])
#     pixely = M_pixel[0][1] + y*(M_pixel[1][1]-M_pixel[0][1])

#     # Rescale the plt coordinates to the HTML canvas size

#     pixelx = pixelx*cwidth/pwidth
#     pixely = pixely*cwidth/pwidth

#     # HTML canvas has y = 0 at the top instead of the bottom
    
#     pixely = cheight-pixely

#     return pixelx, pixely

# def set_main():

#     print("idealgas: entering set_main")

#     global cwidth, cheight

#     canvas = document.getElementById("canvas")

#     parentwidth = document.getElementById("parent").clientWidth
#     cwidth = parentwidth
#     cheight = int(cwidth*0.75)

#     canvas.setAttribute("width", cwidth)
#     canvas.setAttribute("height", cheight)

#     print("idealgas: exiting set_main")

#     push_queue(plot_main, "Plotting main window...")

# def plot_main():

#     print("idealgas: entering plot_main")

#     global pwidth

#     x = np.arange(-5, 5, 0.05)
#     y = V(x)

#     matplotlib.rcParams['font.size'] = 16
#     matplotlib.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'Liberation Sans', 'sans-serif']
    
#     fig, ax = plt.subplots()
#     ax.plot(x, y, linewidth=2)
#     ymin = np.argmin(y)
    
#     ax.set_xlabel("Position")
#     ax.set_ylabel("Energy")

#     ax.set_xlim(-5, 5)
#     ax.set_ylim(y[ymin]-1, 10/globals['beta'])

#     plt.tight_layout()

#     M_pixel[:][:] = ax.transData.transform([(0,0), (1,1)])
#     pwidth, pheight = fig.canvas.get_width_height()

#     img =  io.StringIO()
#     fig.savefig(img, format="svg")
#     img.seek(0)
#     imgdata = img.read()

#     canvas = document.getElementById("canvas")

#     ctx = canvas.getContext("2d")

#     canvas.setAttribute("style", "background: url(\"data:image/svg+xml;base64,"
#                         + str(base64.b64encode(imgdata.encode()), "ascii")
#                         +  "\"); background-size: contain;")

#     plt.clf()

#     print("idealgas: exiting plot_main")

#     push_queue(update_distributions, "Computing distributions...")

# # Calculate the density distributions for x and v

# def update_distributions():

#     print("idealgas: entering update_distributions")

#     globals['Z'] = 1

#     dx = 10/globals['size2']

#     globals['xcdf'] = np.zeros(globals['size2'])
#     globals['ixcdf'] = np.zeros(globals['size2'])

#     # We need the (inverse) CDF for the x variable to generate random numbers
#     # according to the distribution.

#     globals['sx'] = 0

#     for i in range(1, globals['size2']):
#         x = -5 +(i+ 0.5)*dx
#         y = xpdf(x)
#         globals['xcdf'][i] = globals['xcdf'][i-1]+dx*y
#         globals['sx'] += x**2*y*dx

#     globals['Z'] = globals['xcdf'][globals['size2']-1]

#     globals['xcdf'] /= globals['Z']
#     globals['sx'] /= globals['Z']

#     globals['sx'] = np.sqrt(globals['sx'])

#     dx2 = 1/globals['size2']

#     for i in range(globals['size2']):
#         x = -5 +(i+ 0.5)*dx
#         ix = int(np.around(globals['xcdf'][i]/dx2))
#         if ix >= globals['size2']:
#             ix = globals['size2']-1
#         globals['ixcdf'][ix] = x

#     # Sometimes we may get a zero for the inverse CDF because we have
#     # not generated a CDF value in that interval. We perform linear
#     # interpolation to fill the missing values.

#     inzero = 0
#     lastnz = 0

#     for i in range(globals['size2']):
#         if globals['ixcdf'][i] == 0:
#             if i == 0:
#                 globals['ixcdf'][0] = -10
#             elif inzero:
#                 pass
#             else:
#                 inzero = 1
#                 lastnz = i-1
                
#         elif inzero:
#             inzero = 0
#             dx = i-lastnz
#             dy = globals['ixcdf'][i]-globals['ixcdf'][lastnz]
#             for j in range(1, dx):
#                 globals['ixcdf'][lastnz+j] = globals['ixcdf'][lastnz] + dy/dx*j


#     for i in range(globals['size']):
#         for j in range(globals['size']):
#             p2d[j,i] = xpdf(pxlist[i])*vpdf(pvlist[j])

#     print("idealgas: exiting update_distributions")
    
#     push_queue(plot_distributions, "Plotting distributions...")


# def plot_distributions():

#     print("idealgas: entering plot_distributions")

#     matplotlib.rcParams['font.size'] = 32

#     size = globals['size']

#     plt.xticks([0, size/2, size-1], [-5, 0, 5])
#     plt.yticks([0, size/2, size-1], [-5, 0, 5])

#     plt.xlabel("Position")
#     plt.ylabel("Velocity")

#     plt.imshow(p2d, cmap='viridis')
#     cb = plt.colorbar()

#     cb.ax.locator_params(axis='y', nbins=3)

#     plt.tight_layout()

#     plotimg("phase")

#     plt.xlabel("Position")
#     plt.ylabel("Probability")

#     for i in range(globals['size']):
#         p1d[i] = xpdf(pxlist[i])

#     pmax = np.max(p1d)

#     plt.text(-4.5, 0.9*pmax, r'$\sigma_x = $' + "{:.2f}".format(globals['sx']))
#     plt.tight_layout()

#     plt.plot(pxlist, p1d, linewidth=3)
#     plt.tight_layout()

#     plotimg("xpdf")

#     plt.xlabel("Velocity")
#     plt.ylabel("Probability")


#     for i in range(globals['size']):
#         p1d[i] = vpdf(pvlist[i])

#     globals['sv'] = 1/np.sqrt(globals['beta']*globals['m'])
#     plt.text(-4.5, 0.9*vpdf(0), r'$\sigma_v = $' + "{:.2f}".format(globals['sv']))

#     plt.plot(pvlist, p1d, linewidth=3)
#     plt.tight_layout()

#     plotimg("vpdf")

#     print("idealgas: exiting plot_distributions")

#     push_queue(init_ode, "&nbsp;")


# def replot_distribs(params):

#     print("idealgas: Entering replot_distribs")

#     window.clearInterval(globals['timer'])

#     ibeta = document.getElementById("beta")
#     lbeta = document.getElementById("lbeta")

#     im = document.getElementById("m")
#     lm = document.getElementById("lm")

#     iV = document.getElementById("V")
#     lV = document.getElementById("lV")

#     fail = 0
#     plotall = 0

#     try:
#         globals['beta'] = float(ibeta.value)
#         lbeta.innerHTML = ""
#     except:
#         lbeta.innerHTML = "Input error"
#         lstatus.innerHTML = ""
#         fail = 1
        
#     try:
#         globals['m'] = float(im.value)
#         lm.innerHTML = ""
#     except:
#         lm.innerHTML = "Input error"
#         lstatus.innerHTML = ""
#         fail = 1

#     try:
#         # Generating Python function from SymPy expressions for the
#         # potential and the force.
        
#         x = sp.Symbol("x")

#         V = eval(iV.value)
#         F = -sp.diff(V, x)
        
#         globals['V'] = sp.lambdify(x, V, "numpy")
#         globals['F'] = sp.lambdify(x, F, "numpy")
#         if not np.isfinite(globals['V'](1)):
#             raise ValueError
#         lV.innerHTML = ""
#         plotall = 1
#     except:
#         lV.innerHTML = "Input error"
#         lstatus.innerHTML = ""
#         fail = 1
        

#     if fail == 0:

#         print("idealgas: Exiting replot_distribs")

#         if plotall:

#             push_queue(plot_main, "Plotting main window...")

#         else:

#             push_queue(update_distributions, "Plotting distributions...")

    


# def init_ode():

#     print("idealgas: entering init_ode")

#     # For N particles
#     # 1) Start with x(0) = x[i], v(0) = v[i]
#     # 2) Odeint
#     # 3) Plot

#     # Generate random x variables from the inverse of the CDF.

#     u = np.random.randint(globals['size2'], size=globals['N'])
#     globals['vlist'] = np.random.normal(loc=0, scale=1/np.sqrt(globals['beta']*globals['m']), size=globals['N'])

#     for i in range(globals['N']):
#         xlist[i] = globals['ixcdf'][u[i]]

#     print("setting timer")

#     globals['timer'] = window.setInterval(replot_canvas, 40)

#     if globals['firstrun'] == 1:

#         for i in ["beta", "m", "V"]:
#             ii = document.getElementById(i)
#             ii.addEventListener("change", replot_distribs)

#         globals['firstrun'] = 0

#     print("idealgas: exiting init_ode")

# push_queue(set_main, "Setting up main window...")

