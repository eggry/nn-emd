# import plot
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)
import time
import struct
from glob import glob
import gzip

import numpy as np
import nn.tensor.Variable as var
import nn.tensor.Operator as op
import nn.tensor.Activation as activation
from nn.tensor.util import learning_rate_exponential_decay

VERSION = 'TENSOR_Adam_RELU'

def load_mnist(path, kind='train'):
    """Load MNIST data from `path`"""
    labels_path = os.path.join(path, '%s-labels-idx1-ubyte.gz' % kind)
    images_path = os.path.join(path, '%s-images-idx3-ubyte.gz' % kind)

    with gzip.open(labels_path, 'rb') as lbpath:
        lbpath.read(8)
        buffer = lbpath.read()
        labels = np.frombuffer(buffer, dtype=np.uint8)

    with gzip.open(images_path, 'rb') as imgpath:
        imgpath.read(16)
        buffer = imgpath.read()
        images = np.frombuffer(buffer, dtype=np.uint8).reshape(len(labels), 784).astype(np.float64)

    return images, labels


def load_mnist_size(path, size=1000, kind='train'):
    """Load MNIST data from `path`"""
    labels_path = os.path.join(path, '%s-labels-idx1-ubyte.gz' % kind)
    images_path = os.path.join(path, '%s-images-idx3-ubyte.gz' % kind)

    with gzip.open(labels_path, 'rb') as lbpath:
        lbpath.read(8)
        buffer = lbpath.read()
        labels = np.frombuffer(buffer, dtype=np.uint8)

    with gzip.open(images_path, 'rb') as imgpath:
        imgpath.read(16)
        buffer = imgpath.read()
        images = np.frombuffer(buffer, dtype=np.uint8).reshape(len(labels), 784).astype(np.float64)

    return images[:size, ], labels[:size]


def inference(x, output_num):
    conv1_out = op.Conv2D((5, 5, 1, 12), input_variable=x, name='conv1', padding='VALID').output_variables
    relu1_out = activation.Relu(input_variable=conv1_out, name='relu1').output_variables
    # dropout1_out = op.DropOut(input_variable=relu1_out, name='dropout1', phase='train', prob=0.7).output_variables
    pool1_out = op.MaxPooling(ksize=2, input_variable=relu1_out, name='pool1').output_variables

    conv2_out = op.Conv2D((3, 3, 12, 24), input_variable=pool1_out, name='conv2').output_variables
    relu2_out = activation.Relu(input_variable=conv2_out, name='relu2').output_variables
    # dropout2_out = op.DropOut(input_variable=relu2_out, name='dropout2', phase='train', prob=0.7).output_variables
    pool2_out = op.MaxPooling(ksize=2, input_variable=relu1_out, name='pool2').output_variables

    fc_out = op.FullyConnect(output_num=output_num, input_variable=pool2_out, name='fc').output_variables
    return fc_out


def inference_lenet5(x, output_num):
    conv1_out = op.Conv2D((5, 5, 1, 12), input_variable=x, name='conv1', padding='VALID').output_variables
    relu1_out = activation.Relu(input_variable=conv1_out, name='relu1').output_variables
    # dropout1_out = op.DropOut(input_variable=relu1_out, name='dropout1', phase='train', prob=0.7).output_variables
    pool1_out = op.MaxPooling(ksize=2, input_variable=relu1_out, name='pool1').output_variables

    conv2_out = op.Conv2D((3, 3, 12, 24), input_variable=pool1_out, name='conv2', padding='VALID').output_variables
    relu2_out = activation.Relu(input_variable=conv2_out, name='relu2').output_variables
    # dropout2_out = op.DropOut(input_variable=relu2_out, name='dropout2', phase='train', prob=0.7).output_variables
    pool2_out = op.MaxPooling(ksize=2, input_variable=relu2_out, name='pool2').output_variables

    fc_out = op.FullyConnect(output_num=output_num, input_variable=pool2_out, name='fc').output_variables
    return fc_out


batch_size = 64
global_step = 0
# set method
for k in var.GLOBAL_VARIABLE_SCOPE:
    s = var.GLOBAL_VARIABLE_SCOPE[k]
    if isinstance(s, var.Variable) and s.learnable:
        s.set_method_adam()

# img_placeholder = var.Variable((batch_size, 28, 28, 1), 'secure-input')
img_placeholder = var.Variable((batch_size, 28, 28, 1), 'input')
# label_placeholder = var.Variable([batch_size, 1], 'secure-label')
label_placeholder = var.Variable([batch_size, 1], 'label')

# set train_op
prediction = inference_lenet5(img_placeholder, 10)
sf = op.SoftmaxLoss(prediction, label_placeholder, 'sf')

images, labels = load_mnist('../datasets/mnist')
test_images, test_labels = load_mnist('../datasets/mnist', kind='t10k')
# print(test_images.shape[0])

# save train curve config
loss_collect = []
acc_collect = []

total_train_time = 0

with open('logs/%s_log.txt' % VERSION, 'w') as logf:
    for epoch in range(2):
        # random shuffle
        order = np.arange(images.shape[0])
        np.random.shuffle(order)
        _images = images[order]
        _labels = labels[order]

        # batch
        batch_loss = 0
        batch_acc = 0

        val_acc = 0
        val_loss = 0

        # train
        train_acc = 0
        train_loss = 0

        start_time = time.perf_counter()

        for i in range(int(images.shape[0] / batch_size)):
            learning_rate = learning_rate_exponential_decay(5e-4, epoch, 0.1, 10)

            # feed
            img_placeholder.data = _images[i * batch_size:(i + 1) * batch_size].reshape([batch_size, 28, 28, 1])
            # print(img_placeholder.data.shape)
            # img_placeholder.name = "input_layer"
            label_placeholder.data = _labels[i * batch_size:(i + 1) * batch_size]

            # forward
            _loss = sf.loss.eval()
            _prediction = sf.prediction.eval()

            batch_loss += _loss
            train_loss += _loss

            for j in range(batch_size):
                if np.argmax(_prediction[j]) == label_placeholder.data[j]:
                    batch_acc += 1
                    train_acc += 1

            # backward
            img_placeholder.diff_eval()

            for k in var.GLOBAL_VARIABLE_SCOPE:
                s = var.GLOBAL_VARIABLE_SCOPE[k]
                if isinstance(s, var.Variable) and s.learnable:
                    s.apply_gradient(learning_rate=learning_rate, decay_rate=0.0004, batch_size=batch_size)
                if isinstance(s, var.Variable):
                    s.diff = np.zeros(s.shape)
                global_step += 1

            if i % 50 == 0 and i != 0:
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + \
                      "  %s epoch: %d ,  batch: %5d , avg_batch_acc: %.4f  avg_batch_loss: %.4f  learning_rate %f" % (
                      VERSION, epoch,
                      i, batch_acc / float(
                          batch_size), batch_loss / batch_size, learning_rate))
                logf.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " %s epoch: %d ,  batch: %5d , avg_batch_acc: %.4f  avg_batch_loss: %.4f  learning_rate %f\n" %
                           (VERSION, epoch, i, batch_acc / float(batch_size), batch_loss / batch_size, learning_rate))
                loss_collect.append(batch_loss / batch_size)
                acc_collect.append(batch_acc / float(batch_size))

            batch_loss = 0
            batch_acc = 0

        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "  epoch: %5d , train_acc: %.4f  avg_train_loss: %.4f" % (
            epoch, train_acc / float(int(images.shape[0] / batch_size) * batch_size), train_loss / images.shape[0]))
        logf.write(time.strftime("%Y-%m-%d %H:%M:%S",
                            time.localtime()) + "  epoch: %5d , train_acc: %.4f  avg_train_loss: %.4f\n" % (
                  epoch, train_acc / float(int(images.shape[0] / batch_size) * batch_size),
                  train_loss / images.shape[0]))

        end_time = time.perf_counter()
        total_train_time += (end_time - start_time)
        print("epoch %d training time %f " % (epoch, (end_time - start_time)))

        # validation

        for i in range(int(test_images.shape[0] / batch_size)):
            img_placeholder.data = test_images[i * batch_size:(i + 1) * batch_size].reshape([batch_size, 28, 28, 1])
            label_placeholder.data = test_labels[i * batch_size:(i + 1) * batch_size]

            for k in var.GLOBAL_VARIABLE_SCOPE:
                s = var.GLOBAL_VARIABLE_SCOPE[k]
                if isinstance(s, var.Variable):
                    s.wait_bp = False
                if isinstance(s, op.Operator):
                    s.wait_forward = True
                if isinstance(s, op.Operator) and hasattr(s, 'phase'):  # == 'train':
                    s.phase = 'test'

            _loss = sf.loss.eval()
            _prediction = sf.prediction.eval()

            val_loss += _loss

            for j in range(batch_size):
                if np.argmax(sf.softmax[j]) == label_placeholder.data[j]:
                    val_acc += 1

        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "  epoch: %5d , val_acc: %.4f  avg_val_loss: %.4f" % (
            epoch, val_acc / float(int(test_images.shape[0] / batch_size) * batch_size),
            val_loss / test_images.shape[0]))
        logf.write(time.strftime("%Y-%m-%d %H:%M:%S",
                            time.localtime()) + "  epoch: %5d , val_acc: %.4f  avg_val_loss: %.4f" % (
                  epoch, val_acc / float(int(test_images.shape[0] / batch_size) * batch_size),
                  val_loss / test_images.shape[0]))

        for k in var.GLOBAL_VARIABLE_SCOPE:
            s = var.GLOBAL_VARIABLE_SCOPE[k]
            if isinstance(s, op.Operator) and hasattr(s, 'phase'):  # == 'test':
                s.phase = 'train'

# print("total training time is %f" % total_train_time)