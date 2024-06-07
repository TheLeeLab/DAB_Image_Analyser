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
import numpy as np
import shutil

from DAB_Analysis_Functions import DAB

D = DAB()


dataDirectory = "/home/pyodide/data"
files = os.listdir(dataDirectory)
# TODO: deal with multiple files
file = os.path.join(dataDirectory, files[0])

data = D.imread(file)
# TODO: fixme
for f in files:
    os.remove(os.path.join(dataDirectory, f))


def analyse_image(image, file):
    """analyse_image function
    takes image and filename and analyses the image for display

    Args:
        img (np.ndarray): image data
        filename (str): filename string"""
        
    asyn_LMean = document.getElementById("asyn_LMean").value
    asyn_aMean = document.getElementById("asyn_aMean").value
    asyn_bMean = document.getElementById("asyn_bMean").value
    asyn_threshold = document.getElementById("asyn_threshold").value

    analyse_nuclei = document.getElementById("analyseNuclei").checked
    nuclei_LMean = document.getElementById("nuclei_LMean").value
    nuclei_aMean = document.getElementById("nuclei_aMean").value
    nuclei_bMean = document.getElementById("nuclei_bMean").value
    nuclei_threshold = document.getElementById("nuclei_threshold").value

    if analyse_nuclei:
        (
            image_mask_asyn,
            image_mask_nuclei,
            table_asyn,
            table_nuclei,
            asyn_params,
            nuclei_params,
        ) = D.analyse_DAB_and_cells(
            image,
            file,
            asyn_params=np.array(
                [asyn_LMean, asyn_aMean, asyn_bMean, asyn_threshold], dtype=np.float64
            ),
            nuclei_params=np.array(
                [nuclei_LMean, nuclei_aMean, nuclei_bMean, nuclei_threshold],
                dtype=np.float64,
            ),
            check_mask=0,
        )
        masks = np.dstack([image_mask_asyn, image_mask_nuclei])
    else:
        image_mask_asyn, table_asyn, asyn_params = D.analyse_DAB(
            image,
            file,
            asyn_params=np.array(
                [asyn_LMean, asyn_aMean, asyn_bMean, asyn_threshold], dtype=np.float64
            ),
            check_mask=0,
        )
        masks = image_mask_asyn

    imgdata = D.plot_masks(image, masks)

    canvas = document.getElementById("canvas")

    canvas.setAttribute(
        "style",
        'background: url("data:image/png;base64,'
        + str(base64.b64encode(imgdata), "ascii")
        + '"); background-size: contain; width: 100%; background-repeat: no-repeat;',
    )

    plt.clf()

    if not os.path.exists("output"):
        os.mkdir("output")
    table_asyn.to_csv("output/table_asyn.csv")
    asyn_params.to_csv("output/asyn_params.csv")

    if analyse_nuclei:
        table_nuclei.to_csv("output/table_nuclei.csv")
        nuclei_params.to_csv("output/nuclei_params.csv")
    shutil.make_archive("output", format="zip", root_dir="output")

    downloadButton = document.getElementById("downloadZip")
    downloadButton.style = "visibility: visible"

    reanalyseButton = document.getElementById("reanalyse")
    reanalyseButton.style = "visibility: visible"


analyse_image(data, file)
