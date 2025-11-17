#!/usr/bin/env python

from flexbe_core import EventState, Logger
import openai
import json
import re
import yaml
import roslib.packages
import os
import csv
import numpy as np
import pandas as pd
import subprocess
import time
from pathlib import Path

class SpCoRAPPlannerForDistribution(EventState):
    """
    SpCoRAP

    -- model_name    string      Name of the model to use

    ># instruction   string      Instruction to the robot
    ># behavior_result   string  Result of the behavior

    #> argument      string      Argument of the behavior

    <= navigation
    <= object_detection
    <= pick
    <= place
    <= finished
    """

    prompt_tokens = 0
    completion_tokens = 0

    def __init__(self, model_name="o3-2025-04-16", method="spcorap"):
        super(SpCoRAPPlannerForDistribution, self).__init__(
                outcomes=["navigation", "object_detection", "pick", "place", "finished", "failed"],
                output_keys=["argument", "behavior_name", "save_data_path"],
                input_keys=["instruction", "behavior_result"])

        self.model_name = model_name
        self.method = method
        self.pattern_for_behavior_name = r"^\w+"
        self.pattern_for_argument = r"(?<=\().+?(?=\))"

        current_dir = Path(__file__).resolve().parent
        api_path = current_dir / "data" / "OPENAI_API_KEY.key"

        SpCoRAPPlannerForDistribution.load_api_key(api_path)
        robot_skill_path = current_dir / "data" / "prompt" / "robot_behavior_info.yml"
        spco_parameter_path = current_dir / "data" / "params"

        LOCATION_NAME_LIST, LOCATION_PROBABILITY_LIST, OBJECT_NAME_LIST, OBJECT_PROBABILITY_LIST, BEHAVIOR_LIST, INITIAL_POSITION = \
                SpCoRAPPlannerForDistribution.load_robot_behavior_info(robot_skill_path, spco_parameter_path)
        
        THE_NUMBER_OF_SPATIAL_AREA, SPATIAL_CONCEPTS_INDEX = SpCoRAPPlannerForDistribution.make_spatial_concept_index_information(spco_parameter_path)
        
        prompt = SpCoRAPPlannerForDistribution.load_prompt(current_dir / "data" / "prompt" / "prompt.txt")
        system = prompt.format(
            LOCATION_NAME_LIST=LOCATION_NAME_LIST,
            LOCATION_PROBABILITY_LIST=LOCATION_PROBABILITY_LIST,
            OBJECT_NAME_LIST=OBJECT_NAME_LIST,
            OBJECT_PROBABILITY_LIST=OBJECT_PROBABILITY_LIST,
            BEHAVIOR_LIST=BEHAVIOR_LIST,
            THE_NUMBER_OF_SPATIAL_AREA=THE_NUMBER_OF_SPATIAL_AREA,
            SPATIAL_CONCEPTS_INDEX=SPATIAL_CONCEPTS_INDEX
            )

        self.system = [{"role": "system", "content": system}]
        self.example_chat = [{"role": "user", "content": "Bring the candy to the bed."},
                        {"role": "assistant", "content": "navigation (kitchen)"},
                        {"role": "user", "content": "succeeded"},
                        {"role": "assistant", "content": "object_detection (candy)"},
                        {"role": "user", "content": "succeeded"},
                        {"role": "assistant", "content": "pick (candy)"},
                        {"role": "user", "content": "succeeded"},
                        {"role": "assistant", "content": "navigation (bed)"},
                        {"role": "user", "content": "succeeded"},
                        {"role": "assistant", "content": "place (bed)"},
                        {"role": "user", "content": "succeeded\nfinished"}]
        
        self.messages = self.system + self.example_chat

        self.already_got_instruction = False

    def on_enter(self, userdata):

        if not self.already_got_instruction:
            instruction = userdata.instruction
            Logger.loginfo(f"{instruction}")
            self.messages.append({"role": "user", "content": instruction})
            self.already_got_instruction = True

        else:
            behavior_result = userdata.behavior_result
            self.messages.append({"role": "user", "content": behavior_result})

    # ==================================================================================================
    #
    #   Flexbe Methods
    #
    # ==================================================================================================
    def execute(self, userdata):

        userdata.save_data_path = str(
            roslib.packages.get_pkg_dir("ieee_access_public_flexbe_states")) + f"/src/ieee_access_public_flexbe_states/result/{userdata.instruction}/"
        
        print("1")

        response = openai.chat.completions.create(
                                    model=self.model_name,
                                    messages=self.messages
                                    )

        print("2")

        self.messages.append({
            "role": "assistant", 
            "content": response.choices[0].message.content})

        print("3")

        context = response.choices[0].message.content

        print("4")

        self.prompt_tokens += response.usage.prompt_tokens
        self.completion_tokens += response.usage.completion_tokens

        Logger.loginfo(f"ChatGPT: {context}")
        self.save_chat(userdata.instruction, userdata.save_data_path)

        if context == "finished":
            output = self.calculating_gpt_cost(userdata.instruction, userdata.save_data_path)
            self.already_got_instruction = False
            self.messages = None
            return output

        phrases_to_check = ["navigation", "object_detection", "pick", "place"]
        for i, phrase in enumerate(phrases_to_check):
            if re.search(phrase, context):
                behavior_name = self.parse_behavior_name(context)
                break

            elif len(phrases_to_check) == i + 1:
                print("No specified phrases found in the text.\n")
                self.messages.append("No_specified_phrases_found_in_the_text")
                output = self.calculating_gpt_cost(userdata.instruction, userdata.save_data_path)
                self.already_got_instruction = False
                self.messages = None
                return "failed"

        argument = self.parse_argument_for_behavior(context)

        userdata.argument = argument

        if behavior_name == "navigation":
            userdata.behavior_name = "navigation"
            return "navigation"
        elif behavior_name == "object_detection":
            userdata.behavior_name = "object_detection"
            return "object_detection"
        elif behavior_name == "pick":
            userdata.behavior_name = "pick"
            return "pick"
        elif behavior_name == "place":
            userdata.behavior_name = "place"
            return "place"
        else:
            raise ValueError("Invalid behavior name.")

    def parse_behavior_name(self, context):
        """
        Parse the behavior name from the context.

        Args:
            context (str): The context of the conversation.

        Returns:
            behavior_name (str): The behavior name.
        """

        match = re.match(self.pattern_for_behavior_name, context)
        behavior_name = match.group(0)
        
        return behavior_name

    def parse_argument_for_behavior(self, context):
        """
        Parse the argument for the behavior from the context.

        Args:
            context (str): The context of the conversation.

        Returns:
            argument (str): The argument for the behavior.
        """

        match = re.search(self.pattern_for_argument, context)
        argument = match.group(0)
        
        return argument

    def save_chat(self, instruction, save_data_path):
        path = save_data_path
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(path + f"{instruction}.txt", 'w') as f:
            for m in self.messages:
                f.write(json.dumps(m))
                f.write('\n')

    def calculating_gpt_cost(self, instruction, save_data_path):
        
        if self.model_name == 'gpt-4o-2024-08-06' or self.model_name == 'gpt-4o':

            cost = self.prompt_tokens * 2.50 / 1000000 + self.completion_tokens * 10.00 / 1000000
            Logger.loginfo(f"Estimated Cost of {self.model_name}: {cost} USD")

        self.save_chat(instruction, save_data_path)
        return "finished"

    @staticmethod
    def load_api_key(file_path):
        """
        Load the API key from the file.
        """

        with open(file_path, "r") as f:
            openai.api_key = f.read().strip()

    @staticmethod
    def load_robot_behavior_info(robot_skill_path, spco_parameter_path):
        """
        Load the robot behavior information from the file.
        """
        
        LOCATION_NAME_LIST, OBJECT_NAME_LIST, pi, phi, theta_sw, xi = SpCoRAPPlannerForDistribution.load_spco_model_parameters(spco_parameter_path)

        # LOCATION_PROBABILITY_LIST
        LOCATION_PROBABILITY_LIST_STR = ""
        for l in range(len(LOCATION_NAME_LIST)):
            place_name_vector = np.zeros(len(LOCATION_NAME_LIST))
            np.put(place_name_vector, [l], 1)
            prob_it_wt_temp = [0.0 for i in range(len(phi[0]))]
            for j in range(len(phi[0])):
                for c in range(pi.size):
                    prob = place_name_vector.dot(theta_sw[c].T) * pi[c] * phi[c][j]
                    prob_it_wt_temp[j] += prob
            prob_it_wt_n = [float(k) / sum(prob_it_wt_temp) for k in prob_it_wt_temp]
            prob_it_wt = SpCoRAPPlannerForDistribution.round_probabilities_to_sum_1(prob_it_wt_n)
            print(f"{LOCATION_NAME_LIST[l]}: {prob_it_wt}, sum: {sum(prob_it_wt)}")
            LOCATION_PROBABILITY_LIST_STR += f"{LOCATION_NAME_LIST[l]}: {prob_it_wt}\n"
        LOCATION_PROBABILITY_LIST = LOCATION_PROBABILITY_LIST_STR[:-1]
        
        # OBJECT_PROBABILITY_LIST
        OBJECT_PROBABILITY_LIST_STR = ""
        for o in range(len(OBJECT_NAME_LIST)):
            object_name_vector = np.zeros(len(OBJECT_NAME_LIST))
            np.put(object_name_vector, [o], 1)
            prob_it_ot_temp = [0.0 for i in range(len(phi[0]))]
            for j in range(len(phi[0])):
                for c in range(pi.size):
                    prob = object_name_vector.dot(xi[c].T) * pi[c] * phi[c][j]
                    prob_it_ot_temp[j] += prob
            prob_it_ot_n = [float(k) / sum(prob_it_ot_temp) for k in prob_it_ot_temp]
            prob_it_ot = SpCoRAPPlannerForDistribution.round_probabilities_to_sum_1(prob_it_ot_n)
            print(f"{OBJECT_NAME_LIST[o]}: {prob_it_ot}, sum: {sum(prob_it_ot)}")
            
            OBJECT_PROBABILITY_LIST_STR += f"{OBJECT_NAME_LIST[o]}: {prob_it_ot}\n"
        OBJECT_PROBABILITY_LIST = OBJECT_PROBABILITY_LIST_STR[:-1]

        # INITIAL_POSITION
        with open(robot_skill_path, "r") as f:
            robot_behavior_info = yaml.load(f, Loader=yaml.SafeLoader)
        INITIAL_POSITION   = robot_behavior_info["INITIAL_POSITION"]
        
        # BEHAVIOR_LIST
        ## convert BEHAVIOR_LIST to a string
        BEHAVIOR_LIST      = robot_behavior_info["BEHAVIOR_LIST"]
        BEHAVIOR_LIST_STR = ""
        for key, value in BEHAVIOR_LIST.items():
            BEHAVIOR_LIST_STR += f"{key}: {value}\n"
        BEHAVIOR_LIST = BEHAVIOR_LIST_STR[:-1]

        return LOCATION_NAME_LIST, LOCATION_PROBABILITY_LIST, OBJECT_NAME_LIST, OBJECT_PROBABILITY_LIST, BEHAVIOR_LIST, INITIAL_POSITION

    @staticmethod
    def round_probabilities_to_sum_1(probs, digits=3):
        scale = 10 ** digits
        probs = np.array(probs)
        scaled = np.round(probs * scale).astype(int)
        diff = scale - np.sum(scaled)

        residuals = probs * scale - np.round(probs * scale)
        sorted_indices = np.argsort(residuals)[::-1]

        for i in range(abs(diff)):
            idx = sorted_indices[i % len(probs)]
            scaled[idx] += int(np.sign(diff))

        return (scaled / scale).tolist()

    @staticmethod
    def load_spco_model_parameters(spco_parameter_path):
        """
        Load the model parameters of the spatial concepts.
        """
        
        # place_name_list
        with open(spco_parameter_path / 'W_list.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                pass
            LOCATION_NAME_LIST = row
            LOCATION_NAME_LIST.pop(-1)
        # print(f"LOCATION_NAME_LIST: {LOCATION_NAME_LIST}")
        
        # pi
        with open(spco_parameter_path / 'pi.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                pass
        pi_s_data = row
        del pi_s_data[-1]
        pi = np.array(pi_s_data, dtype=np.float64)
        # print(f"pi: {pi}")

        # phi
        phi = []
        with open(spco_parameter_path / 'phi.csv') as f:
            reader = csv.reader(f)
            for row in reader:
                del row[-1]
                phi.append(np.array(row, dtype=np.float64))
        phi = np.array(phi)
        # print(f"phi: {phi}")

        # W
        theta_sw = []
        with open(spco_parameter_path / 'W.csv') as f:
            reader = csv.reader(f)
            for row in reader:
                del row[-1]
                theta_sw.append(np.array(row, dtype=np.float64))
        # print(f"theta_sw: {theta_sw}")

        # object_name_list
        with open(spco_parameter_path / 'Object_W_list.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                pass
            OBJECT_NAME_LIST = row
        print(f"OBJECT_NAME_LIST: {OBJECT_NAME_LIST}")

        # xi
        xi = []
        with open(spco_parameter_path / 'Xi.csv') as f:
            reader = csv.reader(f)
            for row in reader:
                del row[-1]
                xi.append(np.array(row, dtype=np.float64))
        xi = np.array(xi)
        # print("xi: {}\n".format(xi))

        return LOCATION_NAME_LIST, OBJECT_NAME_LIST, pi, phi, theta_sw, xi

    @staticmethod
    def make_spatial_concept_index_information(spco_parameter_path):
        """
        Make spatial concept index information for prompts.
        """
        
        with open(spco_parameter_path / 'pi.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                pass
        pi_s_data = row
        del pi_s_data[-1]
        pi = np.array(pi_s_data, dtype=np.float64)

        THE_NUMBER_OF_SPATIAL_AREA = len(pi)

        SPATIAL_CONCEPTS_INDEX = ""
        for s in range(THE_NUMBER_OF_SPATIAL_AREA):
            index = f"place{s+1}"
            SPATIAL_CONCEPTS_INDEX += index
            if s+1 < THE_NUMBER_OF_SPATIAL_AREA:
                SPATIAL_CONCEPTS_INDEX += ", "
        
        return THE_NUMBER_OF_SPATIAL_AREA, SPATIAL_CONCEPTS_INDEX

    @staticmethod
    def load_prompt(file_path):
        """
        Load the prompt from the file.
        """
        with open(file_path, "r") as f:
            prompt = f.read()

        return prompt
