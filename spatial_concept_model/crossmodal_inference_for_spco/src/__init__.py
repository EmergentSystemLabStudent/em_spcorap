#!/usr/bin/env python
# -*- coding: utf-8 -*-
import roslib.packages

SPCO_DATA_PATH = str(roslib.packages.get_pkg_dir("spco_dataset_generator")) + "/data/output/test/"

PLACE_IMAGE_DATA = SPCO_DATA_PATH + "image/"
PLACE_IMG_DATA = SPCO_DATA_PATH + "img/"
PLACE_IMG_PRE_DATA = SPCO_DATA_PATH + "img_pre/"
PLACE_WORD_DATA = SPCO_DATA_PATH + "tmp/"
POSITION_DATA = SPCO_DATA_PATH
OBJECT_PRE_FREQUENCY_DATA = SPCO_DATA_PATH + "tmp_boo_pre/"
OBJECT_FREQUENCY_DATA = SPCO_DATA_PATH + "tmp_boo/"

place_names = ["living", "bedroom", "kitchen", "bathroom", "entrance", "study_room"]
# robot_poses = [[0.38, 0.35], [2.93, -1.19], [-0.17, -0.29]] #sim
# robot_poses = [[2.48, 0.18], [-0.96, -0.16], [-0.10, 1.08]] #real_v1
robot_poses = [[0.76, -2.41], [0.53, 0.99], [1.69, 0.09]]  # real_v2
object_dictionary = ['plate', 'bowl', 'pitcher_base', 'banana', 'apple', 'orange', 'cracker_box', 'pudding_box',
                     'chips_bag', 'coffee', 'muscat', 'fruits_juice', 'pig_doll', 'sheep_doll', 'penguin_doll',
                     'airplane_toy', 'car_toy', 'truck_toy', 'tooth_paste', 'towel', 'cup', 'treatments', 'sponge',
                     'bath_slipper', 'dolphin_shaped_sponge', 'flog_shaped_sponge']

# object_dictionary = ["plate", "bowl", "pitcher_base", "banana", "apple", "orange", "cracker_box", "pudding_box",
#                      "chips_bag", "coffee", "muscat",
#                      "fruits_juice", "penguin_doll", "sheep_doll", "pig_doll", "airplane_toy", "car_toy", "truck_toy",
#                      "tooth_paste", "towel", "cup",
#                      "treatments", "sponge", "bath_slipper"]
