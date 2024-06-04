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
import os

from DAB_Analysis_Functions import DAB
D = DAB()


dataDirectory = '/home/pyodide/data'
files = os.listdir(dataDirectory)
# TODO: deal with multiple files
file = os.path.join(dataDirectory, files[0])

data = D.imread(file)
# TODO: fixme
for f in files:
    os.remove(os.path.join(dataDirectory, f))

def analyse_image(image):

    image_mask_asyn, table_asyn, asyn_params = D.analyse_DAB(image, check_mask=0)

    imgdata = D.plot_masks(image, image_mask_asyn)

    canvas = document.getElementById("canvas")

    canvas.setAttribute("style", "background: url(\"data:image/png;base64,"
                        + str(base64.b64encode(imgdata), "ascii")
                        +  "\"); background-size: contain; width: 100%; background-repeat: no-repeat;")

    plt.clf()

    table_asyn.to_csv('table_asyn.csv')
    downloadButton = document.getElementById("downloadCSV")
    downloadButton.style = "visibility: visible"
    downloadButton.innerHTML = "Download"
    document.body.append(downloadButton)

analyse_image(data)