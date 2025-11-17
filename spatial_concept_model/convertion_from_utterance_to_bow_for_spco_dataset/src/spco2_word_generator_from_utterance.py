#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import os
import pandas as pd
import csv
import openai
from tqdm import tqdm

# dataフォルダまでの絶対パスを取得
## 現在のディレクトリ
current_dir = os.getcwd()
# 1つ上のディレクトリ
parent_dir = os.path.dirname(current_dir)
# "/data" を付ける
PATH = os.path.join(parent_dir, 'data')
print(PATH)

utterance_save_dir = os.path.join(PATH, "utterance")
os.makedirs(utterance_save_dir, exist_ok=True)  # フォルダがなければ作成


class SpCo2WordGeneratorFromUtterance():
    def __init__(self):
        pass

    # 1つのutteranceから複数単語に変換
    def place_sentence_generator(self):

        # utteranceファイルの数を数える
        files = os.listdir(utterance_save_dir)

        for i in tqdm(range(len(files))):
            save_tmp_path = PATH + "/tmp/" + str(i + 1)
            if not os.path.exists(save_tmp_path):
                os.makedirs(save_tmp_path)
            for j in range(i + 1):
                with open(save_tmp_path + '/Otb.csv', 'a') as f:
                    writer = csv.writer(f)
                    # ファイルから読み込む
                    with open(utterance_save_dir + f"/{j+1}.txt", "r", encoding="utf-8") as file:
                        content = file.read()
                    
                    # ’を'に置換（Unicodeのスマートクォート対応）
                    content = content.replace('’', "'").replace('‘', "'")
                    
                    table = str.maketrans('', '', '.,\"')
                    cleaned = content.translate(table) # ピリオド、コンマ、ダブルクオーテーションマークの削除
                    t = cleaned.split()
                    writer.writerow(t)

    def load_api_key(self, file_path):
        """
        Load the API key from the file.
        """

        with open(file_path, "r") as f:
            openai.api_key = f.read().strip()

    def save_utterance_data(self, utterance, index):
        # 書き込むファイル名（同じディレクトリに作成されます）
        file_name = utterance_save_dir + f"/{index}.txt"
        # ファイルに書き込む
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(utterance)

        print(f"テキストが '{file_name}' に保存されました。")
        
        return
    
    def generation_utterance(self, place_word):
        file_path = "../prompt/prompt.txt" # プロンプトを指定
        with open(file_path, "r") as f:
            prompt = f.read()
        system = prompt.format(LOCATION_NAME=place_word)
        message = [{"role": "system", "content": system}]

        #APIにリクエストを送信
        response = openai.ChatCompletion.create(
            model="gpt-4o-2024-08-06",
            messages=message,
            temperature=1.5
        )

        utterance = response['choices'][0]['message']['content']
        print(f"Here is utterance: {utterance}\n")

        time.sleep(5)

        return utterance

    def main(self):
        loop = 12
        self.load_api_key("../access_keys/OPENAI_API_KEY.key")

        # 場所名のlistを読み込む
        df = pd.read_csv(PATH + "/place_word_list.csv", header=None)
        place_list = df[0].tolist()
        print(f"place list: {place_list}")

        for p in tqdm(range(len(place_list))):
            for l in range(loop):
                # ユーザーの発話文生成
                utterance = self.generation_utterance(place_list[p])
                # utteranceデータの保存
                self.save_utterance_data(utterance, (l+1)+(p*loop))
        
        self.place_sentence_generator()

    
if __name__ == '__main__':
    word_generator = SpCo2WordGeneratorFromUtterance()
    word_generator.main()
