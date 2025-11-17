# crossmodal_inference_for_spco


*   Maintainer: Shoichi Hasegawa ([hasegawa.shoichi@em.ci.ritsumei.ac.jp](mailto:hasegawa.shoichi@em.ci.ritsumei.ac.jp)).
*   Author: Shoichi Hasegawa ([hasegawa.shoichi@em.ci.ritsumei.ac.jp](mailto:hasegawa.shoichi@em.ci.ritsumei.ac.jp)).


## inference_object_to_position_dist_index.pyの使い方
1. /crossmodal_inference_for_spco/data/paramsに以下のファイルを配置する (spco2_learn_concepts_non_gmapping.pyで学習されたもので、推論に使用したいパラメータ (最も尤度の高いパーティクルが保持するパラメータなど))
- index.csv
- mu.csv
- Object_W_list.csv
- particle0.csv
- phi.csv
- pi.csv
- sig.csv
- theta.csv
- W_list.csv
- W.csv
- Xi.csv

2. python inference_object_to_position_dist_index.pyを実行

3. data/resultにresult_object_2_position_dist_index.csvが生成され、各物体の出現確率の推論結果が記載される

## inference_place_word_to_position_dist_index.pyの使い方
1. /crossmodal_inference_for_spco/data/paramsに以下のファイルを配置する (spco2_learn_concepts_non_gmapping.pyで学習されたもので、推論に使用したいパラメータ (最も尤度の高いパーティクルが保持するパラメータなど))
- index.csv
- mu.csv
- Object_W_list.csv
- particle0.csv
- phi.csv
- pi.csv
- sig.csv
- theta.csv
- W_list.csv
- W.csv
- Xi.csv

2. python inference_place_word_to_position_dist_index.pyを実行

3. data/resultにresult_place_word_2_position_dist_index.csvが生成され、各場所名の出現確率の推論結果が記載される