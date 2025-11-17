# SpCoRAP

## Description
This repository provides Spatial Concepts-based Prompts with Large Language Models for Robot Action Planning (SpCoRAP).

* **Maintainer:** Shoichi Hasegawa (hasegawa.shoichi@em.ci.ritsumei.ac.jp)  
* **Author:** Shoichi Hasegawa (hasegawa.shoichi@em.ci.ritsumei.ac.jp)

---

## Table of Contents
- [Requirements](#requirements)
- [Getting Started](#getting-started)
- [How to Use](#how-to-use)
- [Prompts Folder Structure](#prompts-folder-structure)
- [References](#references)

---

## Requirements
**Required:**
- Ubuntu: 20.04
- ROS: Noetic
- Python: 3.8

**Confirmed Environment:**
```
Ubuntu: 20.04 LTS
ROS: Noetic
Python: 3.8.10
```

---

## Getting Started
```shell
git clone https://gitlab.com/general-purpose-tools-in-emlab/probabilistic-generative-models/spatial-concept-models/em_spcorap.git
```

```shell
cd em_spcorap
pip install -r requirements.txt
```

For LLM-based planning, this study uses FlexBE (a Smash-based behavior engine). Clone and build the following two repositories:
- [flexbe_app](https://github.com/FlexBE/flexbe_app/tree/2ef95e2314e296ac838f757f3ed65bf85cabb196)
- [flexbe_behavior_engine](https://github.com/team-vigir/flexbe_behavior_engine/tree/8e2ca45fbdb68818599944d2d155f9367b607c5c)

---

## How to Use

### Spatial Concept Models
This section explains the spatial concept model programs used in this study. The process consists of four major steps: **data collection**, **data conversion**, **learning**, and **inference**.

#### Preparation for Observed Data by a Robot
In the simulation experiment of this study, a robot is placed in a home environment built on Gazebo, and data is collected using rosbag. The map itself should be created using your robot’s mapping tool.

A portion of the rosbag files used in this study is available as samples. These can be used to verify the operation of SpCoRAP:
[https://drive.google.com/drive/folders/15hbax2xDYlx29VukOD4_np8CygtVAbcm?usp=sharing](https://drive.google.com/drive/folders/15hbax2xDYlx29VukOD4_np8CygtVAbcm?usp=sharing)  

---

### Data Conversion

#### Conversion from rosbag to images for SpCo dataset
Usage of `convertion_from_rosbag_to_img_for_spco_dataset` (for generating image feature data):
1. Place the rosbag folder under `/convertion_from_rosbag_to_img_for_spco_dataset/data` with the following structure:
```
rosbag
  ├ bathroom_sink
  │   ├ bathroom_sink_1.bag
  │   ├ ...
  ├ bed
  │   ├ bed_1.bag
  │   ├ ...
  ├ bedroom_closet
      ├ bedroom_closet_1.bag
      ├ ...
```
2. Run: `python main.py`
3. Folders `data/video` and `data/image` are generated. The first image of each bag file is stored in `data/reconstructed_image` in the order **bathroom_sink → bed → bedroom_closet**. These reconstructed images are then used to extract image features stored in `data/img`.

---

#### Conversion from rosbag to pose for SpCo dataset
Usage of `convertion_from_rosbag_to_pose_for_spco_dataset` (for generating position data):
1. Place rosbag folders under `/convertion_from_rosbag_to_pose_for_spco_dataset/data` in the same structure as above.
2. Run: `python rosbag2pose_ieee_access2025.py`
3. `data/position_exp.csv` is generated, containing five rows for each class (bathroom_sink → bed → bedroom_closet). A `data/position` directory is also created, containing each position as a CSV file.

---

#### Conversion from images to BoO (Bag of Objects) for SpCo dataset
Usage of `convertion_from_image_to_boo_for_spco_dataset`:
1. Place reconstructed images under:
```
reconstructed_image
  ├ 1.png
  ├ 2.png
  ├ ...
  ├ 15.png
```
2. Launch object detector: `roslaunch detic_ros node.launch`
- [This code is here.](https://gitlab.com/general-purpose-tools-in-emlab/object-detector/em_detic_ros/-/tree/hasegawa_ieee_access2025?ref_type=heads)
3. Run: `python spco2_object_features_detic_ver.py`
4. `data/detect_image` and `data/tmp_boo` are generated.

---

#### Conversion from utterances to BoW (Bag of Words) for SpCo dataset
1. Place `place_word_list.csv` in the `data` folder (first column: list of place names).
2. Run: `python spco2_word_generator_from_utterance.py`
3. `data/utterance` and `data/tmp` are generated.

---

### Learning the Spatial Concept Model
- Adjust paths in `__init__.py`, `spco2_learn_concepts_non_gmapping.py`, and `spco2_visualizer.py` to your environment.
- Store converted data in the specified paths inside `spco2_learn_concepts_non_gmapping.py`.
- Run learning: `python spco2_learn_concepts_non_gmapping.py`
  - learning result is `/spco2_boo/rgiro_spco2_slam/data/output/test/max_likelihood_param/`
  - you can use final step parameter of max_likelihood_param for inference.
- Visualize learned results using `python spco2_visualizer.py`, which displays Gaussian distributions in Rviz.

---

### Cross-modal Inference
#### Object → Position Distribution
Usage of `inference_object_to_position_dist_index.py`:
1. Place the following learned parameter files into `/crossmodal_inference_for_spco/data/params`:
```
index.csv
mu.csv
Object_W_list.csv
particle0.csv
phi.csv
pi.csv
sig.csv
theta.csv
W_list.csv
W.csv
Xi.csv
```
2. Run: `python inference_object_to_position_dist_index.py`
3. The inference results are saved to `data/result/result_object_2_position_dist_index.csv`.

#### Place Word → Position Distribution
Usage of `inference_place_word_to_position_dist_index.py`:
1. Store the same set of parameter files in the params folder.
2. Run: `python inference_place_word_to_position_dist_index.py`
3. Results saved to `data/result/result_place_word_2_position_dist_index.csv`.

---

## LLM-based Planning with Learned Probabilistic Distribution Parameters

### Setting Data
`spcorap_planner_for_distribution.py` is the main code that runs on FlexBE. Place the following files in the folders specified inside the script (all except the OpenAI API key are included as samples):
- OPENAI_API_KEY.key
- robot_behavior_info.yml
- prompt.txt
- W_list.csv
- pi.csv
- phi.csv
- W.csv
- Object_W_list.csv
- Xi.csv

### Execution Procedure
1. Launch FlexBE: `roslaunch flexbe_app_default.launch`
2. In **Behavior Dashboard**, select **Load Behavior**
3. Choose **spcorap_for_distribution**
4. The state machine will appear in **StateMachine Editor**
5. Start execution in the **Runtime Control** panel by clicking **Start Execution** (green button)

### Other Notes
This study uses Toyota’s Human Support Robot (HSR). Action skill programs are based on libraries distributed to HSR users and cannot be publicly released.

However, open-source HSR-related programs are available and can be used to implement navigation and manipulation:
- https://github.com/hsr-project

The object detection program is based on the following repository:
- https://gitlab.com/general-purpose-tools-in-emlab/object-detector/em_detic_ros

---

## Prompts Folder Structure
The `prompts` folder contains the following prompt files. Use them as needed:

### commonsense_placement
- **commonsense_placement_prompt_for_object_placement_real.txt**  
  Prompt for real-world object placement using commonsense reasoning.
- **commonsense_placement_prompt_for_object_placement_sim.txt**  
  Prompt for simulated object placement using commonsense reasoning.

### comparison_methods
#### nlmap-based prompt + LLM
- **prompt.txt**  
  NLMap-based prompt combined with an LLM.

#### nlmap + LLM
- **prompt.txt**  
  NLMap method combined with an LLM.

#### spcorap
- **prompt.txt**  
  SpCoRAP-based method.

### instruction_generator
#### location_reference_instruction
- **referring_place_name_instruction_for_put_away.txt**  
  Instruction prompt referring to place names for put-away tasks.
- **referring_place_name_instruction_for_search.txt**  
  Instruction prompt referring to place names for search tasks.

#### surrounding_reference_instruction
- **referring_surrounding_objects_instruction_for_put_away.txt**  
  Instruction prompt referring to surrounding objects for put-away tasks.
- **referring_surrounding_objects_instruction_for_search.txt**  
  Instruction prompt referring to surrounding objects for search tasks.

---

## References

