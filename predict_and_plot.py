from misc.postprocessing import nms, plot_bounding_boxes
from train.helpers import *
from train.config import Params
from data import dataloaders
from architectures.models import SSDNet

from my_tests import test_anchor_mapping

import cv2
import numpy as np

import torch
import torch.nn as nn


def model_output_pipeline(params_path):
    #device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    device = torch.device("cpu")

    params = Params(params_path)

    if params.model_id == 'ssdnet':
        model = SSDNet.SSD_Head(params.n_classes)
    model.to(device)

    checkpoint = torch.load('misc/experiments/{}/model_checkpoint'.format(params.model_id))
    model.load_state_dict(checkpoint['model_state_dict'])
    print('Model loaded successfully')

    _, valid_loader = dataloaders.get_dataloaders(params)
    sig = nn.Sigmoid()

    anchors, grid_sizes = create_anchors()
    anchors, grid_sizes = anchors, grid_sizes

    model.eval()
    with torch.no_grad():
        for (batch_images, batch_targets) in valid_loader:
            batch_images = batch_images.to(device)

            # predictions[0] = B x #anchors x 4
            # predictions[1] = B x #anchors x 3 -> [0.2, 0.1, 0.9], [0.01, 0.01, 0.8]
            # are elements of predictions really on GPU?
            predictions = model(batch_images)

            # move everything to cpu for plotting
            batch_images = batch_images.cpu()
            predictions[0] = [activations_to_bboxes(
                x, anchors, grid_sizes).cpu() for x in predictions[0]]
            predictions[1] = predictions[1].cpu()

            assert predictions[0][0].is_cuda is False

            for idx in range(len(batch_images)):
                current_image = (batch_images[idx] * 255).numpy().astype(np.uint8)

                current_image_bboxes = (batch_targets[0][idx] * 320).numpy().astype(int)
                current_image_class_ids = batch_targets[1][idx].numpy()

                current_prediction_bboxes = (predictions[0][idx] * 320).numpy().astype(int)
                current_prediction_class_confidences = predictions[1][idx].sigmoid().numpy()

                # assert everything here is on CPU
                plot_model_outputs(current_image, current_image_bboxes, current_image_class_ids,
                                   current_prediction_bboxes, current_prediction_class_confidences, anchors)
                # return
            return


def plot_model_outputs(current_image, current_image_bboxes, current_image_class_ids,
                       current_prediction_bboxes, current_prediction_class_confidences, anchors):
    """
    ???
    """
    keep_indices = []
    for idx, one_hot_pred in enumerate(current_prediction_class_confidences):
        max_confidence = np.amax(one_hot_pred)
        if max_confidence > 0.5:
            keep_indices.append(idx)
    print('Number of bboxes predicted: ', len(keep_indices))
    print('KEPT INDECES', keep_indices)
    keep_indices = np.array(keep_indices)
    if len(keep_indices) != 0:
        kept_bboxes = current_prediction_bboxes[keep_indices]
    else:
        kept_bboxes = np.array([])

    anchor_mapping_part(current_image, current_image_bboxes, current_image_class_ids,
                        current_prediction_bboxes, current_prediction_class_confidences, anchors)

    # print ground truth
    plot_bounding_boxes(current_image, current_image_bboxes, 'Ground truth', 1)

    # print predicted bboxes
    plot_bounding_boxes(current_image, kept_bboxes, 'Raw preditctions (before NMS)')

    # apply nms and print again
    post_nms_bboxes = nms(kept_bboxes)
    plot_bounding_boxes(current_image, post_nms_bboxes, 'Post NMS predictions')


def anchor_mapping_part(current_image, current_image_bboxes, current_image_class_ids,
                        current_prediction_bboxes, current_prediction_class_confidences, anchors):

    overlaps = jaccard(torch.FloatTensor(current_image_bboxes),
                       hw2corners(anchors[:, :2], anchors[:, 2:]))

    # print("OVERLAPS", overlaps)
    corner_anchors = hw2corners(anchors[:, :2], anchors[:, 2:])

    # map each anchor to the highest IOU obj, gt_idx - ids of mapped objects
    matched_gt_bbox, matched_gt_class_ids, matched_pred_bbox, pos_idx = map_to_ground_truth(
        overlaps, current_image_bboxes, current_image_class_ids, current_prediction_bboxes)

    test_anchor_mapping.test(current_image, corner_anchors, matched_gt_bbox,
                             matched_pred_bbox, current_prediction_class_confidences, current_image_bboxes, pos_idx)


model_output_pipeline('misc/experiments/ssdnet/params.json')
