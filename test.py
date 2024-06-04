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

from js import document

import matplotlib.pyplot as plt
import base64

from DAB_Analysis_Functions import DAB
D = DAB()

lstatus = document.getElementById("status")


file = '4.ome.tif'
data = D.imread(file)
image_mask_asyn, table_asyn, asyn_params = D.analyse_DAB(file, check_mask=0)

def plot_image(image):
    imgdata = D.plot_masks(image)

    canvas = document.getElementById("canvas")

    canvas.setAttribute("style", "background: url(\"data:image/png;base64,"
                        + str(base64.b64encode(imgdata), "ascii")
                        +  "\"); background-size: contain;")

    plt.clf()

plot_image(data)