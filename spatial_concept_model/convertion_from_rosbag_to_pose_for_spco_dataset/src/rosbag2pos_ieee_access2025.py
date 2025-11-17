import subprocess
import os
import pandas as pd
from tqdm import tqdm
import re

topic_name = "/global_pose/pose/position"

# 現在のディレクトリ
current_dir = os.getcwd()
# 1つ上のディレクトリ
parent_dir = os.path.dirname(current_dir)
# "/data" を付ける
path = os.path.join(parent_dir, 'data')
print(path)

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
    for j in range(len(sorted_file_list)):
        print(sorted_file_list[j])
        command = ["rostopic", "echo", "-b", target_path + f"/{sorted_file_list[j]}", "-p", topic_name]
        # 保存先のディレクトリパスを事前に作成
        save_dir = os.path.join(path, "position", order_list[i])
        os.makedirs(save_dir, exist_ok=True)  # フォルダがなければ作成

        # 保存先のファイル名
        file_name = sorted_file_list[j].replace('.bag', '') + ".csv"
        save_path = os.path.join(save_dir, file_name)

        # コマンドの実行 & 結果を保存
        with open(save_path, "wb") as f:
            subprocess.run(command, stdout=f)


# position_exp.csvの作成 (各場所エリアにつき12データずつ) for IEEE Access2025 -> 108データできる
## 各場所につきrosbagの数が12個なので、1bagにつき2つのタイムスタンプまで考慮するようにする. そうすれば24データになる.
for i in tqdm(range(len(order_list))):
    target_position_folder_path = path + "/position/"+ order_list[i]
    position_files = os.listdir(target_position_folder_path)
    
    # 数字でソート (bed_1.csv, bed_2.csv, ...というようにする)
    sorted_position_file_list = sorted(position_files, key=extract_number)
    print(sorted_position_file_list)
    
    for j in range(len(sorted_position_file_list)):
        # 元のCSVファイルを読み込む
        df = pd.read_csv(target_position_folder_path + f"/{sorted_position_file_list[j]}", skiprows=1)
        # new_df = df.iloc[0, 1:3] # xyデータの1行目まで読む
        values = df.iloc[0, 1:3].values  # [x, y]
        new_df = pd.DataFrame([values])  # ヘッダーは不要なのでcolumns指定しない

        if i == 0 and j == 0:
            new_df.to_csv(path + "/position_exp.csv", index=False, header=False)
        else:
            with open(path + "/position_exp.csv", 'a') as f:
                new_df.to_csv(f, index=False, header=False)





