#!/usr/bin/env python

import csv
import os
import numpy as np

PATH = "../data"

class InferenceObject2PositionDistIndex():

    def __init__(self):
        pass

    def inference(self):

        pi, xi, phi, object_name_list = self.read_data()
        target_list_index = list(range(len(object_name_list)))
        # target_list = ["yellow", "blue"]
        # target_list_index = [object_name_list.index(target_list[i]) for i in range(len(target_list))]

        """
        i_tのクロスモーダル推論
        P(i_t | o_t) = ∫ P(i_t | C_t) P(C_t | o_t) dC_t
        1. P(C_t | o_t) = P(C_t | π, o_t, ξ) = P(C_t | π) P(o_t | ξ, C_t)
        2. P(i_t | C_t, Φ)
        3. 周辺化した上で結果を出力させる
        命令された物体の名前と物体の辞書を対応させて、object_name_vectorを生成
        """

        # target = object_name_list.index(target_name)
        # object_name_vector = np.zeros(len(object_name_list))
        # np.put(object_name_vector, [target], 1)

        prob_i_t_list = []
        print(len(xi[0])) # 24とかが出るはず

        ## P(i_t | o_t)の計算
        for i in range(len(xi[0])):
            object_name_vector = np.zeros(len(object_name_list))
            np.put(object_name_vector, [i], 1)

            prob_i_t = [0.0 for i in range(len(phi[0]))]  # 位置分布のindexリスト作成
            for j in range(len(phi[0])):
                for c in range(pi.size):
                    prob = object_name_vector.dot(xi[c].T) * pi[c] * phi[c][j]
                    # P(o_t | ξ_c) P(C | pi) P (i_t | phi_c)
                    prob_i_t[j] += prob

            prob_i_t_r = [float(k) / sum(prob_i_t) for k in prob_i_t]  # 正規化
            prob_i_t_a = self.round_probabilities_to_sum_1(prob_i_t_r)
            # print("Result of inference:")
            # print("{}\n".format(prob_i_t_r))

            prob_i_t_list.append(prob_i_t_a)
        
        print(prob_i_t_list)
        target_prob_i_t = [prob_i_t_list[target_list_index[i]] for i in range(len(target_list_index))]
        # print(len(prob_i_t_list))
        self.save_data(target_prob_i_t, object_name_list)
    
    # 最大余剰法で合計を1にする
    def round_probabilities_to_sum_1(self, probs, digits=3):
        scale = 10 ** digits
        probs = np.array(probs)
        scaled = np.round(probs * scale).astype(int)
        diff = scale - np.sum(scaled)

        # 誤差の調整: 誤差を誤差が最も大きい要素に加える/引く
        residuals = probs * scale - np.round(probs * scale)
        sorted_indices = np.argsort(residuals)[::-1]  # 誤差が大きい順（正負含む）

        for i in range(abs(diff)):
            idx = sorted_indices[i % len(probs)]
            scaled[idx] += int(np.sign(diff))

        # 小数に戻す
        return (scaled / scale).tolist()


    def read_data(self):
        ## データの読み込み
        # π
        with open(PATH + '/params/pi.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                pass
        pi_s_data = row
        del pi_s_data[-1]
        pi = np.array(pi_s_data, dtype=np.float64)
        # print("pi_s :{}\n".format(pi))

        # ξ
        xi = []
        with open(PATH + '/params/Xi.csv') as f:
            reader = csv.reader(f)
            for row in reader:
                del row[-1]
                xi.append(np.array(row, dtype=np.float64))
        xi = np.array(xi)
        # print("xi: {}\n".format(xi))

        # Φ
        phi = []
        with open(PATH + '/params/phi.csv') as f:
            reader = csv.reader(f)
            for row in reader:
                del row[-1]
                phi.append(np.array(row, dtype=np.float64))
        phi = np.array(phi)

        # 物体の単語辞書
        with open(PATH + '/params/Object_W_list.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                pass
            object_name_list = row
            # del object_name_list[-1]
        # print(object_name_list)
        return pi, xi, phi, object_name_list

    def save_data(self, prob, object_name_list):
        # 推論結果を保存
        FilePath = PATH + '/result/'
        if not os.path.exists(FilePath):
            os.makedirs(FilePath)
        
        # with open(FilePath + 'result_object_2_position_dist_index.csv', 'w', newline='') as csvfile:
        #     writer = csv.writer(csvfile)
        #     for row in prob:
        #         writer.writerow(row)
        # 書き込み
        with open(FilePath + 'result_object_2_position_dist_index.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for i in range(len(object_name_list)):
                obj_name = object_name_list[i]
                prob_row = prob[i] if i < len(prob) else []
                writer.writerow([obj_name] + prob_row)
    
if __name__ == "__main__":
  i = InferenceObject2PositionDistIndex()
  i.inference()



