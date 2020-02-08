import torch
import torch.optim as optim


def layer_specific_adam(model, params):
    print("AMS grad is false")
    return optim.Adam([
        {'params': model.backbone.parameters(), 'lr': params.learning_rate * params.decay_rate},
        {'params': model.out0.parameters()},
        {'params': model.out1.parameters()},
        {'params': model.out2.parameters()},
        {'params': model.down_conv2.parameters()},
        {'params': model.out3.parameters()},
        {'params': model.down_conv3.parameters()},
        {'params': model.out4.parameters()},
        {'params': model.down_conv4.parameters()},
    ], lr=params.learning_rate, weight_decay=params.weight_decay, amsgrad=False)


def layer_specific_sgd(model, params):
    return optim.SGD([
        {'params': model.backbone.parameters(), 'lr': params.learning_rate * params.decay_rate},
        {'params': model.out0.parameters()},
        {'params': model.out1.parameters()},
        {'params': model.out2.parameters()},
        {'params': model.down_conv2.parameters()},
        {'params': model.out3.parameters()},
        {'params': model.down_conv3.parameters()},
        {'params': model.out4.parameters()},
        {'params': model.down_conv2.parameters()},
    ], lr=params.learning_rate, weight_decay=params.weight_decay, momentum=0.9)


def plain_adam(model, params):
    return optim.Adam(model.parameters(), lr=params.learning_rate, weight_decay=params.weight_decay)
