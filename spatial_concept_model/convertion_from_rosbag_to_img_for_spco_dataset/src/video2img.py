#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Standard Library
import cv2
import os
import sys

# Third Party
import rospy


class Video2Img():

    def __init__(self):
        pass

    def save_all_frames(self, video_path, dir_path):
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            return

        os.makedirs(dir_path, exist_ok=True)
        save_idx = 1  # ファイル名用の連番カウンタ

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            filename = os.path.join(dir_path, f"{save_idx}.png")
            cv2.imwrite(filename, frame)
            save_idx += 1


if __name__ == "__main__":
    video2img = Video2Img()
    arg1 = sys.argv[1]
    arg2 = sys.argv[2]
    video2img.save_all_frames(arg1, arg2)
