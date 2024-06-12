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
from skimage.measure import label, regionprops_table
from skimage.color import rgb2gray, hed2rgb, rgb2hed
from skimage.morphology import reconstruction
from skimage.filters import threshold_otsu
import pandas as pd


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
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
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

    def clean_nuclear_mask(self, mask):
        """ clean_nuclear_mask function
        takes mask, and cleans up nuclei
        removes 3*3 (i.e. diffraction limited) objects
        clears border, connects larger aggregates if small "holes" inside, etc
        ================INPUTS============= 
        mask is logical array of image mask
        ================OUTPUT============= 
        cleaned_mask is cleaned up mask """
        mask_disk = 1*ski.morphology.binary_closing(mask, ski.morphology.disk(1))
        seed = np.copy(mask_disk)
        seed[1:-1, 1:-1] = mask_disk.max()
        
        mask_filled = ski.morphology.reconstruction(seed, mask_disk, method='erosion')
        cleaned_mask = ski.segmentation.clear_border(mask_filled)
       
        label_img = label(cleaned_mask)
        props = regionprops_table(label_img, properties=('area',
                                                         'axis_minor_length'))
        Area = props['area']
        indices_toremove = np.unique(np.unique(label_img)[1:]*(Area < 60))[1:]
        mask=np.isin(label_img,indices_toremove)
        cleaned_mask[mask] = 0
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

    def otsu_filtering(self, image):
        """ otsu threshold a single colour image
        
        Args:
            image (np.2darray): single grayscale image
        Returns:
            mask (np.2darray): single boolean mask image"""
            
        seed = np.copy(image)
        seed[1:-1, 1:-1] = image.max()
        mask = image
        
        filled = reconstruction(seed, mask, method='erosion')
        holes = np.abs(image-filled)
        thresh = threshold_otsu(holes)
        if thresh > 0.025:
            mask = holes > thresh
        else:
            mask = np.full_like(holes, False)
        return mask

    def analyse_DAB(self, img, filename):
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
            table_asyn (pd.DataArray): pandas array of asyn data"""

        ihc_hed = rgb2hed(self.im2double(img))
        # Create an RGB image for each of the stains
        null = np.zeros_like(ihc_hed[:, :, 0])
        ihc_d = hed2rgb(np.stack((null, null, ihc_hed[:, :, 2]), axis=-1))

        dab_image = rgb2gray(ihc_d)

        image_mask_asyn = self.otsu_filtering(dab_image)
        image_mask_asyn = self.clean_protein_mask(image_mask_asyn)

        label_img_asyn = label(image_mask_asyn)
        props_asyn = regionprops_table(
            label_img_asyn,
            properties=("area", "centroid", "axis_major_length", "axis_minor_length"),
        )

        table_asyn = pd.DataFrame(props_asyn)
        table_asyn["pseudo_circularity"] = self.pseudo_circularity(
            props_asyn["axis_major_length"], props_asyn["axis_minor_length"]
        )
        table_asyn["filename"] = np.full_like(
            props_asyn["axis_minor_length"], filename, dtype="object"
        )

        return image_mask_asyn, table_asyn

    def analyse_DAB_and_cells(self, img, filename):
        """analyse_DAB function
        takes file, and uses initial parameters and rate to separate out
        coloured objects
        then returns table with object information

        Args:
            img (np.ndarray): image data
            filename (str): filename string

        Returns:
            image_mask_asyn (np.2darray): mask of protein
            table_asyn (pd.DataArray): pandas array of asyn data
            image_mask_nuclei (np.2darray): mask of nuclei
            table_nuclei (pd.DataArray): pandas array of nuclei data"""

        ihc_hed = rgb2hed(self.im2double(img))
        # Create an RGB image for each of the stains
        null = np.zeros_like(ihc_hed[:, :, 0])
        ihc_d = hed2rgb(np.stack((null, null, ihc_hed[:, :, 2]), axis=-1))
        ihc_h = hed2rgb(np.stack((ihc_hed[:, :, 0], null, null), axis=-1))

        dab_image = rgb2gray(ihc_d)

        image_mask_asyn = self.otsu_filtering(dab_image)
        image_mask_asyn = self.clean_protein_mask(image_mask_asyn)

        test = ihc_h
        test[image_mask_asyn == 1] = np.median(ihc_h[:, :, 0])
        nuclei_image = rgb2gray(test)

        image_mask_nuclei = self.otsu_filtering(nuclei_image)
        image_mask_nuclei = self.clean_nuclear_mask(image_mask_nuclei)

        label_img_asyn = label(image_mask_asyn)
        props_asyn = regionprops_table(
            label_img_asyn,
            properties=("area", "centroid", "axis_major_length", "axis_minor_length"),
        )

        table_asyn = pd.DataFrame(props_asyn)
        table_asyn["pseudo_circularity"] = self.pseudo_circularity(
            props_asyn["axis_major_length"], props_asyn["axis_minor_length"]
        )
        table_asyn["filename"] = np.full_like(
            props_asyn["axis_minor_length"], filename, dtype="object"
        )

        label_img_nucl = label(image_mask_nuclei)
        props_nuclei = regionprops_table(
            label_img_nucl,
            properties=("area", "centroid", "axis_major_length", "axis_minor_length"),
        )
        table_nuclei = pd.DataFrame(props_nuclei)
        table_nuclei["pseudo_circularity"] = self.pseudo_circularity(
            props_nuclei["axis_major_length"], props_nuclei["axis_minor_length"]
        )
        return image_mask_asyn, table_asyn, image_mask_nuclei, table_nuclei

    def plot_masks(self, img, masks=None):
        """plot_masks function
        takes image, and optional masks, and plots them together

        Args:
            img (np.ndarray): image data
            masks (np.ndarry): mask data

        Returns:
            fig (object): figure object
            axes (object): axis object"""
        import matplotlib.pyplot as plt

        if isinstance(masks, type(None)):
            fig, axes = plt.subplots(1, 1)
            axes.imshow(img)
            axes.axis("off")
        else:
            fig, axes = plt.subplots(1, 1)

            axes.imshow(img)
            if len(masks.shape) > 2:  # if multiple masks
                colors = ["darkred", "darkblue"]
                for i in np.arange(masks.shape[2]):  # plot multiple masks
                    axes.contour(
                        masks[:, :, i], [0.5], linewidths=0.5, colors=colors[i]
                    )
            else:
                axes.contour(masks, [0.5], linewidths=0.5, colors="darkred")

            axes.axis("off")
        
        return fig, axes
