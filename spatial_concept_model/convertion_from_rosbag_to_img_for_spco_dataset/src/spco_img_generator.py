#! /usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import subprocess
import os
import spco2_placescnn as places365
import sys
from tqdm import tqdm


class ImageFeatureServer():

    def image_server(self, PLACE_IMAGE_DATA, PLACE_IMG_DATA):
        files = os.listdir(PLACE_IMAGE_DATA)
        for i in tqdm(range(len(files))):
            self.frame = cv2.imread(PLACE_IMAGE_DATA + "/{}.png".format(i+1)) ##

            convert_img = places365.Image.fromarray(self.frame)  # convert into PIL
            input_img = places365.V(self.tf(convert_img).unsqueeze(0))
            logit = self.model.forward(input_img)
            h_x = places365.F.softmax(logit, 1).data.squeeze()

            # save image feature
            fp = open(PLACE_IMG_DATA + '/ft' + str(i+1) + '.csv', 'a')
            h_x_numpy = h_x.to('cpu').detach().numpy().copy()
            fp.write(','.join(map(str, h_x_numpy)))
            fp.write('\n')
            fp.close()
            print("save new feature")

            probs, idx = h_x.sort(0, True)
            probs = probs.numpy()
            idx = idx.numpy()

    def load_network_model(self):
        # load the labels
        self.classes, self.labels_IO, self.labels_attribute, self.W_attribute = places365.load_labels()

        # load the model
        self.model = places365.load_model()

        # load the transformer
        self.tf = places365.returnTF()  # image transformer

        # get the softmax weight
        self.params = list(self.model.parameters())
        self.weight_softmax = self.params[-2].data.numpy()
        self.weight_softmax[self.weight_softmax < 0] = 0

        return (True)

    def __init__(self):
        self.image_save = True  # rospy.get_param('~image_save')#true

        if self.load_network_model() == False:
            print("error")

        self.frame = []


if __name__ == "__main__":
    srv = ImageFeatureServer()
    arg1 = sys.argv[1]
    arg2 = sys.argv[2]
    srv.image_server(arg1, arg2)
