import numpy as np
import imgaug.augmenters as iaa
import imageio
import imgaug as ia
import os
from PIL import Image
import shutil
import cv2
import matplotlib.pyplot as plt

RANGES=[10,8,6,4,2,1]

PATH_DATA_DIRS = ["/home/test","/home/second"]


# Sometimes(0.5, ...) applies the given augmenter in 50% of all cases,
# e.g. Sometimes(0.5, GaussianBlur(0.3)) would blur roughly every second image.
sometimes = lambda aug: iaa.Sometimes(0.5, aug)

# Define our sequence of augmentation steps that will be applied to every image
# All augmenters with per_channel=0.5 will sample one value _per image_
# in 50% of all cases. In all other cases they will sample new values
# _per channel_.
seq = iaa.SomeOf((0, 5),
    [
        iaa.OneOf([
            iaa.GaussianBlur((0, 3.0)), # blur images with a sigma between 0 and 3.0
            iaa.AverageBlur(k=(2, 7)), # blur image using local means with kernel sizes between 2 and 7
            iaa.MedianBlur(k=(3, 11)), # blur image using local medians with kernel sizes between 2 and 7
        ]),
        iaa.Sharpen(alpha=(0, 1.0), lightness=(0.75, 1.5)), # sharpen images
        iaa.Emboss(alpha=(0, 1.0), strength=(0, 2.0)), # emboss images
        # search either for all edges or for directed edges,
        # blend the result with the original image using a blobby mask
        iaa.SimplexNoiseAlpha(iaa.OneOf([
            iaa.EdgeDetect(alpha=(0.1, 0.5)),
            iaa.DirectedEdgeDetect(alpha=(0.1, 0.5), direction=(0.0, 0.5)),
        ])),
        iaa.AdditiveGaussianNoise(loc=0, scale=(0.0, 0.05*255), per_channel=0.5), # add gaussian noise to images
        iaa.CoarseDropout((0.03, 0.15), size_percent=(2, 5), per_channel=1),
        iaa.Add((-10, 10), per_channel=0.5), # change brightness of images (by -10 to 10 of original value)
        iaa.AddToHueAndSaturation((-20, 20)), # change hue and saturation
        # either change the brightness of the whole image (sometimes
        # per channel) or change the brightness of subareas
        iaa.OneOf([
            iaa.Multiply((0.5, 1.5), per_channel=0.5),
            iaa.FrequencyNoiseAlpha(
                exponent=(-4, 0),
                first=iaa.Multiply((0.5, 1.5), per_channel=True),
                second=iaa.ContrastNormalization((0.5, 2.0))
            )
        ]),
        iaa.ContrastNormalization((0.5, 2.0), per_channel=0.5), # improve or worsen the contrast
        iaa.OneOf([
            iaa.CoarseSaltAndPepper((0.03, 0.1), size_percent=(2, 5), per_channel=False),
            iaa.CoarseSaltAndPepper((0.03, 0.1), size_percent=(2, 5), per_channel=True)
        ])
        #iaa.Grayscale(alpha=(0.0, 1.0)),
        #sometimes(iaa.ElasticTransformation(alpha=(0.5, 3.5), sigma=0.25)), # move pixels locally around (with random strengths)
        #sometimes(iaa.PiecewiseAffine(scale=(0.01, 0.05))), # sometimes move parts of the image around
        #sometimes(iaa.PerspectiveTransform(scale=(0.01, 0.1)))
    ],
    random_order=True
)

for PATH_DATA_DIR in PATH_DATA_DIRS:
	for num in RANGES:
		for filename in os.listdir(PATH_DATA_DIR):
			if filename[-3:] == "png":
				bgr_img = cv2.imread(os.path.join(PATH_DATA_DIR, filename))
				b,g,r = cv2.split(bgr_img)       # get b,g,r
				image = cv2.merge([r,g,b])     # switch it to rgb
				for i in range(num):
					#image = imageio.imread(os.path.join(PATH_DATA_DIR, filename))
					image_aug = seq.augment_image(image)  # done by the library  
					name = filename[:-4]
					new_name = name+"_augmented_"+str(i)
					cv2.imwrite(os.path.join(PATH_DATA_DIR+str(num), new_name+".png"), image_aug)
					shutil.copyfile(os.path.join(PATH_DATA_DIR, name+".txt"), os.path.join(PATH_DATA_DIR+str(num), new_name+".txt"))
