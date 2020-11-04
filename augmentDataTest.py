import numpy as np
import imgaug.augmenters as iaa
import imageio
import imgaug as ia
import os
from PIL import Image
import shutil
import cv2
import matplotlib.pyplot as plt

PATH_DATA_DIR = "/home/sally/work/darknet/data/train_atwork"


# Sometimes(0.5, ...) applies the given augmenter in 50% of all cases,
# e.g. Sometimes(0.5, GaussianBlur(0.3)) would blur roughly every second image.
often = lambda aug: iaa.Sometimes(0.7, aug)
sometimes = lambda aug: iaa.Sometimes(0.5, aug)
afewtimes = lambda aug: iaa.Sometimes(0.3, aug)


# Define our sequence of augmentation steps that will be applied to every image
# All augmenters with per_channel=0.5 will sample one value _per image_
# in 50% of all cases. In all other cases they will sample new values
# _per channel_.
seq = iaa.SomeOf((1, 2),
    [
        iaa.OneOf([
		iaa.CoarseDropout((0.0,0.1), size_percent=(0.1, 0.9)),
		iaa.CoarseDropout((0.0,0.1), size_percent=(0.1, 0.9), per_channel=True),
		iaa.SaltAndPepper((0, 0.1), per_channel=True),
		iaa.SaltAndPepper((0, 0.1), per_channel=False),
		iaa.AdditiveGaussianNoise(scale=(0, 0.15*255), per_channel=False),
    		iaa.AdditiveGaussianNoise(scale=(0, 0.15*255), per_channel=True),            
        ]),
        
        iaa.OneOf([
		iaa.GaussianBlur(sigma=(0.0, 2.0)),
		iaa.AverageBlur(k=(2, 7)),
		iaa.MotionBlur(k=8),            
        ]),

        iaa.OneOf([
            	iaa.Add((-30, 30), per_channel=0.5),
		iaa.AddToHueAndSaturation((-20, 20), per_channel=True),
		iaa.MultiplyBrightness(mul=(0.4, 1.3)),
		iaa.GammaContrast((0.5, 2.0)),
		iaa.GammaContrast((0.8, 1.2), per_channel=True),
		iaa.SigmoidContrast(gain=(3, 10), cutoff=(0.4, 0.6)),
		iaa.SigmoidContrast(gain=(3, 10), cutoff=(0.4, 0.6), per_channel=True),
		iaa.LinearContrast((0.4, 1.6)),
		iaa.LinearContrast((0.4, 1.6), per_channel=True)
        ])
     
    ],
    random_order=True
)



for filename in os.listdir(PATH_DATA_DIR):
    if filename[-3:] == "png":
        image = cv2.imread(os.path.join(PATH_DATA_DIR, filename))
        #b,g,r = cv2.split(bgr_img)       # get b,g,r
        #image = cv2.merge([r,g,b])     # switch it to rgb
        for i in range(2):
        #image = imageio.imread(os.path.join(PATH_DATA_DIR, filename))
            image_aug = seq.augment_image(image)  # done by the library  
            name = filename[:-4]
            new_name = name+"_augmented_"+str(i)
            cv2.imwrite(os.path.join(PATH_DATA_DIR, new_name+".png"), image_aug)
            shutil.copyfile(os.path.join(PATH_DATA_DIR, name+".txt"), os.path.join(PATH_DATA_DIR, new_name+".txt"))
