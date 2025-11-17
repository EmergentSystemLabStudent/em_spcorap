#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Standard Library
import os
import re
from tqdm import tqdm
import shutil
import subprocess


counter = 1

# dataフォルダまでの絶対パスを取得
## 現在のディレクトリ
current_dir = os.getcwd()
# 1つ上のディレクトリ
parent_dir = os.path.dirname(current_dir)
# "/data" を付ける
path = os.path.join(parent_dir, 'data')
print(path)

save_reconstructed_image_path = os.path.join(path, "reconstructed_image")
os.makedirs(save_reconstructed_image_path, exist_ok=True)  # 念のためディレクトリ作成

# ソートのための関数
def extract_number(file_name):
    match = re.search(r'(\d+)', file_name)
    return int(match.group(1)) if match else -1

# 処理をしていくフォルダの順番
order_list = ["sofa_table_area", "entrance_shelf", "bathroom_sink", "laundry_area", "bedroom_closet", "bed", "study_desk", "dining_table", "kitchen_sink"]

for i in tqdm(range(len(order_list))):
    target_path = path + "/rosbag/" + order_list[i]
    files = os.listdir(target_path)

    # 数字でソート (bed_1.bag, bed_2.bag, ...というようにする)
    sorted_file_list = sorted(files, key=extract_number)
    print(sorted_file_list)

    # 各bagファイルごとにpositionのcsvファイルを取得
    for j in tqdm(range(len(sorted_file_list))):
        print(sorted_file_list[j]) # bagファイルの名前 (ex. bed_1.bag)

        #### rosbag2video
        # 保存先のディレクトリパスを事前に作成
        video_save_dir = os.path.join(path, "video", order_list[i])
        os.makedirs(video_save_dir, exist_ok=True)  # フォルダがなければ作成

        # 保存先のファイル名
        file_name = sorted_file_list[j].replace('.bag', '') + ".mp4"
        video_save_path = os.path.join(video_save_dir, file_name)

        # rosbag2video.pyのコマンド記載
        command = [
            "python", 
            "rosbag2video.py", 
            "-o", 
            video_save_path, 
            "-t", 
            "/hsrb/head_rgbd_sensor/rgb/image_rect_color/compressed", 
            path + f"/rosbag/{order_list[i]}/{sorted_file_list[j]}"
            ]

        # コマンドの実行 & 結果を保存
        subprocess.run(command)

        #### video2image
        # 保存先のディレクトリパスを事前に作成
        image_save_dir = os.path.join(path, "image", order_list[i], sorted_file_list[j].replace('.bag', ''))
        os.makedirs(image_save_dir, exist_ok=True)  # フォルダがなければ作成

        # video2img.pyのコマンド記載
        command = [
            "python", 
            "video2img.py", 
            video_save_path, 
            image_save_dir
            ]

        # コマンドの実行 & 結果を保存
        subprocess.run(command)

        image_files = os.listdir(image_save_dir)
        sorted_image_file_list = sorted(image_files, key=extract_number)
        print(sorted_image_file_list)

        # 先頭の画像のみを移動させる
        image_path = image_save_dir + "/" + sorted_image_file_list[0]
        new_image_name = f"{counter}.png"
        save_re_image_file_path = os.path.join(save_reconstructed_image_path, new_image_name)
        shutil.copy(image_path, save_re_image_file_path)
        print(f"Saved from image to reconstructed image folder")
        counter += 1
        
#### 再構築した画像データセットをPlacesCNNにつっこみ、特徴量を得る
# 保存先のディレクトリパスを事前に作成
img_save_dir = os.path.join(path, "img")
os.makedirs(img_save_dir, exist_ok=True)  # フォルダがなければ作成

command = [
    "python", 
    "spco_img_generator.py",  
    save_reconstructed_image_path, 
    img_save_dir
    ]

# コマンドの実行 & 結果を保存
subprocess.run(command)