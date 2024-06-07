#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 15:21:34 2023

Class related to analysis of DAB stained images

@author: jbeckwith
"""
import numpy as np
import skimage as ski
import cv2
import io


class DAB:
    def __init__(self):
        self = self
        return

    def imread(self, file):
        """imread function
        takes RGB image and corrects openCV's ordering

        Args:
            file (str): file path

        Returns:
            img (np.2darray): array"""
        img = cv2.imread(file)
        return img

    def im2double(self, img):
        """im2double function
        takes image and normalises to double

        Args:
            img (np.2darray): image object

        Returns:
            imdouble (np.2darray): numpy array converted to double"""
        info = np.iinfo(img.dtype)  # Get the data type of the input image
        imdouble = (
            img.astype(np.float32) / info.max
        )  # Divide all values by the largest possible value in the datatype
        return imdouble

    def getMeanchannelvalues(self, image, mask):
        """getMeanLABvalues function
        takes image, image mask and gets mean channel components
        assumes Lab colour space

        Args:
            image (np.2darray): numpy array
            mask (np.2darray): numpy logical array

        Returns:
            imdouble is numpy array"""
        LMean = np.nanmean(
            np.multiply(image[:, :, 0], mask)
        )  # mean of only the pixels within the masked area.
        aMean = np.nanmean(
            np.multiply(image[:, :, 1], mask)
        )  # mean of only the pixels within the masked area.
        bMean = np.nanmean(
            np.multiply(image[:, :, 2], mask)
        )  # mean of only the pixels within the masked area.
        return LMean, aMean, bMean

    def pseudo_circularity(self, MajorAxisLength, MinorAxisLength):
        """pseudo_circularity function
        takes major and minor axis length and computes pseudo-circularity

        Args:
            MajorAxisLength (np.float): major axis length in pixels
            MinorAxisLength (np.float): minor axis length in pixels

        Returns:
            p_circ (np.float64): pseudo-circularity (runs from 0--1)"""
        p_circ = np.divide(
            np.multiply(2, MinorAxisLength), np.add(MinorAxisLength, MajorAxisLength)
        )
        return p_circ

    def clean_nuclear_mask(self, image_mask):
        """clean_nuclear_mask function
        takes image_mask, and cleans up nuclei
        removes 3*3 (i.e. diffraction limited) objects
        clears border, connects larger nuclei if small "holes" inside, etc

        Args:
            image_mask (np.2darray): logical array of image mask

        Returns:
            cleaned_mask (np.2darray): cleaned up mask"""
        mask_disk = 1 * ski.morphology.binary_closing(
            image_mask, ski.morphology.disk(3)
        )
        seed = np.copy(mask_disk)
        seed[1:-1, 1:-1] = mask_disk.max()

        mask_filled = ski.morphology.reconstruction(seed, mask_disk, method="erosion")
        cleaned_mask = 1 * ski.morphology.binary_closing(
            mask_filled, ski.morphology.disk(2)
        )

        from skimage.measure import label, regionprops_table

        label_img = label(cleaned_mask)
        props = regionprops_table(label_img, properties=("area", "axis_minor_length"))
        Area = props["area"]
        indices_toremove = np.unique(np.unique(label_img)[1:] * (Area < 60))[1:]
        image_mask = np.isin(label_img, indices_toremove)
        cleaned_mask[image_mask] = 0
        return cleaned_mask

    def clean_protein_mask(self, image_mask):
        """clean_protein_mask function
        takes image_mask, and cleans up protein aggregates
        removes 3*3 (i.e. diffraction limited) objects
        clears border, connects larger aggregates if small "holes" inside, etc

        Args:
            image_mask (np.2darray): logical array of image mask

        Returns:
            cleaned_mask (np.2darray): cleaned up mask"""
        mask_disk = 1 * ski.morphology.binary_closing(
            image_mask, ski.morphology.disk(1)
        )
        seed = np.copy(mask_disk)
        seed[1:-1, 1:-1] = mask_disk.max()

        mask_filled = ski.morphology.reconstruction(seed, mask_disk, method="erosion")
        cleaned_mask = ski.segmentation.clear_border(mask_filled)

        from skimage.measure import label, regionprops_table

        label_img = label(cleaned_mask)
        props = regionprops_table(label_img, properties=("area", "axis_minor_length"))
        minorA = props["axis_minor_length"]
        Area = props["area"]
        indices_toremove = np.unique(
            np.hstack(
                [
                    np.unique(label_img)[1:] * (minorA < 3),
                    np.unique(label_img)[1:] * (Area < 9),
                ]
            )
        )[1:]
        image_mask = np.isin(label_img, indices_toremove)
        cleaned_mask[image_mask] = 0
        return cleaned_mask

    def colourFilterLab(
        self, image, initial_params, rate=[0.75, 4], percentage=0.075, maxiter=30
    ):
        """colourFilterLab function
        takes image, and uses initial parameters and rate to separate out
        coloured objects

        Args:
            image (np.2darray): image input
            initial_params (np.1darray): initial Lmean, aMean, bMean and threshold parameters
            rate (np.float64): how fast to change the parameters per iteration
            percentage (np.float64): percentage of pixels we worry about in the mask
            maxiter (int): how many iterations of optimisation to do (default 30)

        Returns:
            image_mask (np.2darray) logical array of image mask
            current_params (np.1darray) image analysis final params"""
        mask_current = np.zeros(image[:, :, 0].shape)
        LMean = initial_params[0]
        aMean = initial_params[1]
        bMean = initial_params[2]
        thres = initial_params[3]
        ratep_1 = rate[0]
        ratep_2 = rate[1]

        iteration = 1
        while (
            np.nansum(mask_current) < np.multiply(percentage, image[:, :, 0].size)
        ) and (iteration <= maxiter):
            deltaL = np.subtract(image[:, :, 0], LMean)  # get mean channel 1
            deltaa = np.subtract(image[:, :, 1], aMean)  # get mean channel 2
            deltab = np.subtract(image[:, :, 2], bMean)  # get mean channel 3
            deltaE = np.sqrt(
                (deltaL**2 + deltaa**2 + deltab**2)
            )  # get change versus iteration
            mask_previous = mask_current  # store previous mask
            mask_current = 1 * (deltaE <= thres)  # update mask
            mask_current = np.where(mask_current == 0, np.nan, mask_current)
            LMean, aMean, bMean = self.getMeanchannelvalues(
                image, mask_current
            )  # get new means
            LMean = np.multiply(LMean, ratep_1)  # adjust means with rate of change
            aMean = np.multiply(aMean, ratep_1)  # adjust means with rate of change
            bMean = np.multiply(bMean, ratep_1)  # adjust means with rate of change

            dEmask = np.multiply(deltaE, mask_current)
            meanMaskedDeltaE = np.nanmean(dEmask)
            stDevMaskedDeltaE = np.nanstd(dEmask)
            thres = np.add(meanMaskedDeltaE, np.multiply(ratep_2, stDevMaskedDeltaE))
            iteration += 1

        image_mask = mask_previous  # update mask
        image_mask[np.isnan(image_mask)] = 0
        current_params = np.array([LMean, aMean, bMean, thres])
        return image_mask, current_params

    def analyse_DAB(
        self, img, filename, asyn_params=np.array([27, 6, 5, 15]), use_defaults=1, check_mask=0
    ):
        """analyse_DAB function
        takes file, and uses initial parameters and rate to separate out
        coloured objects
        then returns table with object information

        Args:
            img (np.ndarray): image data
            filename (str): filename string
            asyn_params (np.1darry): initial default Lmean, aMean, bMean and threshold parameters
            nuclei_params (np.1darray): initial default Lmean, aMean, bMean and threshold parameters

        Returns:
            image_mask_asyn (np.2darray): mask of protein
            table_asyn (pd.DataArray): pandas array of asyn data
            asyn_params (pd.DataArray): parameters used to gets asyn mask"""
        lab_Image = ski.color.rgb2lab(self.im2double(img))
        if use_defaults == 0:
            init_guess = self.get_guess(self, img, lab_Image)
            asyn_params = np.hstack([init_guess], asyn_params[-1])

        image_mask_asyn, asyn_params = self.colourFilterLab(lab_Image, asyn_params)
        image_mask_asyn = self.clean_protein_mask(image_mask_asyn)
        if check_mask == 1:
            masks = image_mask_asyn
            self.plot_masks(img, masks)
        from skimage.measure import label, regionprops_table

        label_img_asyn = label(image_mask_asyn)
        props_asyn = regionprops_table(
            label_img_asyn,
            properties=("area", "centroid", "axis_major_length", "axis_minor_length"),
        )
        import pandas as pd

        table_asyn = pd.DataFrame(props_asyn)
        table_asyn["pseudo_circularity"] = self.pseudo_circularity(
            props_asyn["axis_major_length"], props_asyn["axis_minor_length"]
        )
        table_asyn["filename"] = np.full_like(props_asyn["axis_minor_length"].values, 
                                              filename, dtype='object')
        
        asyn_cols = ["asyn_LMean", "asyn_aMean", "asyn_bMean", "asyn_threshold"]
        asyn_params = pd.DataFrame([asyn_params], columns=asyn_cols)
        asyn_params["filename"] = np.full_like(asyn_params["asyn_LMean"].values, 
                                              filename, dtype='object')

        return image_mask_asyn, table_asyn, asyn_params

    def analyse_DAB_and_cells(
        self,
        img,
        filename,
        asyn_params=np.array([27, 6, 5, 15]),
        nuclei_params=np.array([70, 1, -5, 4]),
        use_defaults=1,
        check_mask=0,
    ):
        """analyse_DAB_and_cells function
        takes file, and uses initial parameters and rate to separate out
        coloured objects
        then returns table with object information

        Args:
            img (np.ndarray): image data
            filename (string): filename string
            asyn_params (np.1darry): initial default Lmean, aMean, bMean and threshold parameters
            nuclei_params (np.1darray): initial default Lmean, aMean, bMean and threshold parameters

        Returns:
            image_mask_asyn (np.2darray): mask of protein
            image_mask_nuclei (np.2darray): mask of nuclei
            table_asyn (pd.DataArray): pandas array of asyn data
            table_nuclei (pd.DataArray): pandas array of nuclei data
            asyn_params (pd.DataArray): parameters used to gets asyn mask
            nuclei_params (pd.DataArray): parameters used to get nuclear mask"""
        lab_Image = ski.color.rgb2lab(self.im2double(img))
        if use_defaults == 0:
            init_guess = self.get_guess(self, img, lab_Image)
            asyn_params = np.hstack([init_guess], asyn_params[-1])
            init_guess_n = self.get_guess(
                self,
                img,
                lab_Image,
                "select area that is just nuclear staining; press enter when complete",
            )
            nuclei_params = np.hstack([init_guess_n], nuclei_params[-1])

        image_mask_asyn, asyn_params = self.colourFilterLab(lab_Image, asyn_params)
        image_mask_asyn = self.clean_protein_mask(image_mask_asyn)
        image_mask_nuclei, nucl_params = self.colourFilterLab(
            lab_Image, nuclei_params, rate=[1, 2]
        )
        image_mask_nuclei = self.clean_nuclear_mask(image_mask_nuclei)
        if check_mask == 1:
            masks = np.dstack([image_mask_asyn, image_mask_nuclei])
            self.plot_masks(img, masks)
        from skimage.measure import label, regionprops_table

        label_img_asyn = label(image_mask_asyn)
        props_asyn = regionprops_table(
            label_img_asyn,
            properties=("area", "centroid", "axis_major_length", "axis_minor_length"),
        )
        import pandas as pd

        table_asyn = pd.DataFrame(props_asyn)
        table_asyn["pseudo_circularity"] = self.pseudo_circularity(
            props_asyn["axis_major_length"], props_asyn["axis_minor_length"]
        )
        table_asyn["filename"] = np.full_like(props_asyn["axis_minor_length"].values, 
                                              filename, dtype='object')


        label_img_nucl = label(image_mask_nuclei)
        props_nuclei = regionprops_table(
            label_img_nucl,
            properties=("area", "centroid", "axis_major_length", "axis_minor_length"),
        )
        table_nuclei = pd.DataFrame(props_nuclei)
        table_nuclei["pseudo_circularity"] = self.pseudo_circularity(
            props_nuclei["axis_major_length"], props_nuclei["axis_minor_length"]
        )
        table_nuclei["filename"] = np.full_like(table_nuclei["axis_minor_length"].values, 
                                              filename, dtype='object')


        asyn_cols = ["asyn_LMean", "asyn_aMean", "asyn_bMean", "asyn_threshold"]
        asyn_params = pd.DataFrame([asyn_params], columns=asyn_cols)
        asyn_params["filename"] = np.full_like(asyn_params["asyn_LMean"].values, 
                                              filename, dtype='object')

        nuclei_cols = [
            "nuclei_LMean",
            "nuclei_aMean",
            "nuclei_bMean",
            "nuclei_threshold",
        ]
        nuclei_params = pd.DataFrame([nucl_params], columns=nuclei_cols)
        nuclei_params["filename"] = np.full_like(nuclei_params["nuclei_LMean"].values, 
                                              filename, dtype='object')

        return (
            image_mask_asyn,
            image_mask_nuclei,
            table_asyn,
            table_nuclei,
            asyn_params,
            nuclei_params,
        )

    def get_guess(
        self,
        img,
        lab_image,
        message="select area that is just DAB-stained protein aggregate; press enter when complete",
    ):
        import cv2

        r = cv2.selectROI(message, cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

        cv2.destroyAllWindows()
        area = lab_image[int(r[1]) : int(r[1] + r[3]), int(r[0]) : int(r[0] + r[2])]
        init_guess = np.mean(np.mean(area, axis=1), axis=0)
        return init_guess

    def plot_masks(self, img, masks=None):
        """plot_masks function
        takes image, and optional masks, and plots them together

        Args:
            img (np.ndarray): image data
            masks (np.ndarry): mask data

        Returns:
            imgdata (bytes): figure in bytes"""
        import matplotlib.pyplot as plt

        if isinstance(masks, type(None)):
            fig, axes = plt.subplots(1, 1)
            axes.imshow(img)
            axes.axis("off")
        else:
            fig, axes = plt.subplots(1, 2, sharey=True)
            axes[0].imshow(img)

            axes[1].imshow(img)
            if len(masks.shape) > 2:  # if multiple masks
                colors = ["darkred", "darkblue"]
                for i in np.arange(masks.shape[2]):  # plot multiple masks
                    axes[1].contour(
                        masks[:, :, i], [0.5], linewidths=0.5, colors=colors[i]
                    )
            else:
                axes[1].contour(masks, [0.5], linewidths=0.5, colors="darkred")

            for a in axes:
                a.axis("off")

        plt.tight_layout()
        img_out = io.BytesIO()
        fig.savefig(img_out, format="png")
        img_out.seek(0)
        imgdata = img_out.read()

        return imgdata
