"""A very simple MNIST classifier.
See extensive documentation at
https://www.tensorflow.org/get_started/mnist/beginners
"""

# Just disables the warning, doesn't enable AVX/FMA
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import numpy as np
from numpy import genfromtxt


import argparse
import sys

from tensorflow.examples.tutorials.mnist import input_data

import tensorflow as tf



def main(_):
  # Import data
  ##mnist = input_data.read_data_sets(FLAGS.data_dir)
  train_data = genfromtxt('easylines.csv', skip_header=1)
  label_data = genfromtxt('easylabels.csv')
  
  assert train_data.shape[0] == label_data.shape[0]
  
  dataset = tf.data.Dataset.from_tensor_slices((train_data, label_data))


  # Create the model
  x = tf.placeholder(tf.float32, [None, 3])
  W = tf.Variable(tf.zeros([3, 2]))
  b = tf.Variable(tf.zeros([2]))
  y = tf.nn.softmax(tf.matmul(x, W) + b)

  # Define loss and optimizer
  y_ = tf.placeholder(tf.float32, [None, 2])

  # The raw formulation of cross-entropy,
  #
  #   tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(tf.nn.softmax(y)),
  #                                 reduction_indices=[1]))
  #
  # can be numerically unstable.
  #
  # So here we use tf.losses.sparse_softmax_cross_entropy on the raw
  # outputs of 'y', and then average across the batch.
  cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y), reduction_indices=[1]))
  train_step = tf.train.GradientDescentOptimizer(0.1).minimize(cross_entropy)


  init = tf.global_variables_initializer()

  sess = tf.Session()
  sess.run(init)
  # Train
  for i in range(1000):
    sess.run(train_step, feed_dict={x: train_data, y_: label_data})
    randomize = np.arange(len(train_data))
    np.random.shuffle(randomize)
    train_data = train_data[randomize]
    label_data = label_data[randomize]

  # Test trained model
  correct_prediction = tf.equal(tf.argmax(y,1), tf.argmax(y_,1))
  accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
  print(sess.run(accuracy, feed_dict={x: train_data,
                                      y_: label_data}))

if __name__ == '__main__':
  tf.app.run(main=main)

