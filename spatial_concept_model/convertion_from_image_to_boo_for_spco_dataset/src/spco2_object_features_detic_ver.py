#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Standard Library
from __future__ import unicode_literals
import codecs
import cv2
from cv_bridge import CvBridge, CvBridgeError
import os
import csv

# Third Party
import numpy as np
import rospy
import actionlib
import detic_ros_msgs.msg as detic_ros_msgs


# dataフォルダまでの絶対パスを取得
## 現在のディレクトリ
current_dir = os.getcwd()
# 1つ上のディレクトリ
parent_dir = os.path.dirname(current_dir)
# "/data" を付ける
path = os.path.join(parent_dir, 'data')
print(path)

detect_image_save_dir = os.path.join(path, "detect_image")
os.makedirs(detect_image_save_dir, exist_ok=True)  # フォルダがなければ作成

tmp_boo_save_dir = os.path.join(path, "tmp_boo")
os.makedirs(tmp_boo_save_dir, exist_ok=True)  # フォルダがなければ作成


object_dictionary = [
    "apple", "orange", "sheep_doll", "pig_doll", "slipper", 
    "cup", "towel", "truck_toy", "juice_bottle", "cracker_box", 
    "alarm_clock", "hat", "rubber_gloves", "drill", "keyboard",
    "hammer", "scissors", "screwdriver", "toaster", "trash_bin",
    "backpack", "pencil_case", "headset", "frypan"]


class ObjectFeatureServer():
    def __init__(self):
        self.detect_object_info = []
        self.detect_image = 0
        self.object_list = []
        self.Object_BOO = []
        self.cv_bridge = CvBridge()
        self.frame = 0
        self.client = actionlib.SimpleActionClient("/detic/action/detection_with_det_image", detic_ros_msgs.DeticWithDetImgAction)
        self.client.wait_for_server()

        rospy.loginfo("[Service spco_data/object] Ready")

        files = os.listdir(path + "/reconstructed_image")
        for i in range(len(files)):
            self.frame = cv2.imread(path + "/reconstructed_image" + "/{}.png".format(i + 1))
            raw_img = self.cv_bridge.cv2_to_compressed_imgmsg(self.frame)
            self.object_server(i + 1, raw_img)

        self.save_dictionary_data()

    def object_server(self, step, image):
        goal = detic_ros_msgs.DeticWithDetImgGoal(0, image)
        self.client.send_goal_and_wait(goal)
        result = self.client.get_result()

        self.detect_object_info = result.boxes.boxes
        self.detect_image = result.detect_image
        # print(type(self.detect_object_info))

        if len(self.detect_object_info) == 0:
            if step == 1:
                # 最初の教示で物体が検出されなかったとき
                self.object_list = [[]]
                self.Object_BOO = [[0] * len(object_dictionary)]
                self.save_boo_data(step)
                self.object_list = []
                return

            else:
                # 最初の教示以降の教示で物体が検出されなかったとき
                object_list = []
                self.object_list.append(object_list)
                self.make_object_boo()
                self.save_boo_data(step)
                self.object_list = []
                return

        self.save_detection_img(step, self.detect_image)
        self.extracting_label()
        self.make_object_boo()
        self.save_boo_data(step)
        self.object_list = []
        # print("object_list: {}\n".format(self.object_list))
        # print("dictionary: {}\n".format(object_dictionary))
        # print("Bag-of-Objects: {}\n".format(self.Object_BOO))

    def extracting_label(self):
        object_list = []
        for i in range(len(self.detect_object_info)):
            object_list.append(self.detect_object_info[i].name)
            # print(object_list)
        self.object_list.append(object_list)
        # print(self.object_list)
        return
    
    def make_object_boo(self):
        # print(self.object_list)
        self.Object_BOO = [[0 for i in range(len(object_dictionary))] for n in range(len(self.object_list))]
        # print(self.Object_BOO)
        for n in range(len(self.object_list)):
            for j in range(len(self.object_list[n])):
                for i in range(len(object_dictionary)):
                    if object_dictionary[i] == self.object_list[n][j]:
                        self.Object_BOO[n][i] = self.Object_BOO[n][i] + 1
        # print(self.Object_BOO)
        return

    def save_detection_img(self, step, image):
        detect_img = self.cv_bridge.compressed_imgmsg_to_cv2(image)
        cv2.imwrite(detect_image_save_dir + "/" + str(step) + ".png", detect_img)
        return

    def save_boo_data(self, step):
        # # 全時刻の観測された物体のリストを保存
        # FilePath = SPCO_DATA_PATH + "/tmp_boo/Object.csv"
        # with open(FilePath, 'w') as f:
        #     writer = csv.writer(f)
        #     writer.writerows(self.object_list)
        #
        # # 教示ごとに観測された物体のリストを保存
        # FilePath = SPCO_DATA_PATH + "/tmp_boo/" + str(step) + "_Object.csv"
        # with open(FilePath, 'w') as f:
        #     writer = csv.writer(f)
        #     writer.writerows(self.object_list)

        # 教示ごとのBag-Of-Objects特徴量を保存
        FilePath = tmp_boo_save_dir + "/" + str(step) + "_Object_BOO.csv"
        with open(FilePath, 'w') as f:
            writer = csv.writer(f)
            writer.writerows(self.Object_BOO)

        # # 教示ごとの物体の辞書を保存
        # FilePath = SPCO_DATA_PATH + "/tmp_boo/" + str(step) + "_Object_W_list.csv"
        # with open(FilePath, 'w') as f:
        #     writer = csv.writer(f, lineterminator='\n')
        #     writer.writerow(object_dictionary)

        return

    def save_dictionary_data(self):
        with open(tmp_boo_save_dir + "/Object_W_list.csv", 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(object_dictionary)
        pass


if __name__ == '__main__':
    rospy.init_node('spco2_object_features', anonymous=False)
    srv = ObjectFeatureServer()
    # rospy.spin()
