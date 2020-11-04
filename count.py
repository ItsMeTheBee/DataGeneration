from collections import Counter
import os

PATH = "/home/vision/atWork/DataGen/DataGenBBoxes/labels/"

CHECK = ["0", "1","2","3","4","5","6","7","8","9","10","11","12","13","14"]

NAMES = ["small_black_alu",
"small_grey_alu",
"large_black_alu", 
"large_grey_alu",
"bolt", 
"small_nut", 
"large_nut", 
"plastic_tube", 
"bearing_box",
"bearing", 
"axis", 
"distance_tube", 
"motor",
"blue_container",
"red_container"]

count_dict = dict()
for num in CHECK:
	count_dict[num] = 0

img_count = 0
for filename in os.listdir(PATH):
	if filename.endswith(".txt"):
		img_count = img_count + 1
		f = open(PATH + filename)
		lines = f.read()
		lines = lines.replace("\n", " ")
		numbers = lines.split(" ")
		for num in CHECK:
			count_dict[num] = count_dict[num] + numbers.count(num)


for num in CHECK:
	print(NAMES[int(num)], "occurance: ",count_dict[num])
	#print(NAMES[int(num)], "is visible in ", count_dict[num] / img_count, "percent of all images \n")
