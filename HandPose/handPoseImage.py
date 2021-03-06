from __future__ import division
import cv2
import time
import numpy as np


class HandPose:
    def __init__(self, model, nPoints, pose_pair, input_source):
        self.input_source = input_source  # the input file name (index, if using a camera)
        self.protofile, self.weightfile = model  # model and weights for the neural network
        self.nPoints = nPoints  # number of key points
        self.POSE_PAIRS = pose_pair
        self.threshold = 0.1

    def window_size(self, frame):
        # to generate the input dimensions from the frame dimension generated by VideoCapture
        frameWidth = frame.shape[1]
        frameHeight = frame.shape[0]
        aspect_ratio = frameWidth / frameHeight
        inHeight = 368
        inWidth = int(((aspect_ratio * inHeight) * 8) // 8)

        return inHeight, inWidth  # input dimensions

    def draw_skeleton(self, frame, frameCopy, output):
        # take the video frame and the output generated by the model
        # and create the skeleton using the pairs defined in sef.POSE_PAIR
        points = []
        for i in range(self.nPoints):
            # confidence map of corresponding body's part.
            probMap = output[0, i, :, :]  # extract the probability map for the ith feature
            probMap = cv2.resize(probMap, (frame.shape[1], frame.shape[0]))
            # Find global maxima of the probMap.
            minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)

            if prob > self.threshold:
                cv2.circle(frameCopy, (int(point[0]), int(point[1])), 6, (0, 255, 255), thickness=-1,
                           lineType=cv2.FILLED)
                cv2.putText(frameCopy, "{}".format(i), (int(point[0]), int(point[1])), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 0, 255), 2, lineType=cv2.LINE_AA)
                # Add the point to the list if the probability is greater than the threshold
                points.append((int(point[0]), int(point[1])))
            else:
                points.append(None)

        for pair in POSE_PAIRS:
            partA = pair[0]
            partB = pair[1]
            if points[partA] and points[partB]:
                cv2.line(frame, points[partA], points[partB], (0, 255, 255))
                # draw lines connecting the points of the pair and draw the circles
                cv2.circle(frame, points[partA], 5, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
                cv2.circle(frame, points[partB], 5, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)

        return frame, frameCopy

    def forward(self):
        frame = cv2.imread(self.input_source)
        frameCopy = np.copy(frame)
        inHeight, inWidth = self.window_size(frame)
        net = cv2.dnn.readNetFromCaffe(self.protofile, self.weightfile)
        t = time.time()
        inpBlob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (inWidth, inHeight), (0, 0, 0),
                                        swapRB=False, crop=False)
        net.setInput(inpBlob)
        output = net.forward()
        print("time taken by network : {:.3f}".format(time.time() - t))
        frame, frameCopy = self.draw_skeleton(frame, frameCopy, output)
        cv2.imshow('Output-Keypoints', frameCopy)
        cv2.imshow('Output-Skeleton', frame)
        cv2.imwrite('Output-Keypoints.jpg', frameCopy)
        cv2.imwrite('Output-Skeleton.jpg', frame)
        print("Total time taken : {:.3f}".format(time.time() - t))
        cv2.waitKey(0)


if __name__ == '__main__':
    input_source = "right-frontal.jpg"
    protoFile = "hand/pose_deploy.prototxt"
    weightsFile = "hand/pose_iter_102000.caffemodel"
    nPoints = 22
    POSE_PAIRS = [[0, 1], [1, 2], [2, 3], [3, 4], [0, 5], [5, 6], [6, 7], [7, 8], [0, 9], [9, 10], [10, 11], [11, 12],
                  [0, 13], [13, 14], [14, 15], [15, 16], [0, 17], [17, 18], [18, 19], [19, 20]]
    gen = HandPose((protoFile, weightsFile), nPoints, POSE_PAIRS, input_source=input_source)
    gen.forward()
