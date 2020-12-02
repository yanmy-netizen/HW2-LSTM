from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf
import tensorflow.contrib.layers as layers

def build_fcn(minimap, screen, info, msize, ssize, num_action):
  # Extract features
  l1_regularizer = layers.l1_regularizer(scale=0.0005)
  l2_regularizer = layers.l2_regularizer(scale=0.005)
  mconv1 = layers.conv2d(tf.transpose(minimap, [0, 2, 3, 1]),
                         num_outputs=16,
                         kernel_size=5,
                         stride=1,
                         padding='same',
                         activation_fn=tf.nn.relu,
                         scope='mconv1')
  mconv2 = layers.conv2d(mconv1,
                         num_outputs=32,
                         kernel_size=3,
                         stride=1,
                         padding='same',
                         activation_fn=tf.nn.relu,
                         scope='mconv2')
  sconv1 = layers.conv2d(tf.transpose(screen, [0, 2, 3, 1]),
                         num_outputs=16,
                         kernel_size=5,
                         stride=1,
                         padding='same',
                         activation_fn=tf.nn.relu,
                         scope='sconv1')
  sconv2 = layers.conv2d(sconv1,
                         num_outputs=32,
                         kernel_size=3,
                         stride=1,
                         padding='same',
                         activation_fn=tf.nn.relu,
                         scope='sconv2')
  info_fc = layers.fully_connected(layers.flatten(info),
                                   num_outputs=256,
                                   activation_fn=tf.tanh,
                                   #weights_regularizer=l1_regularizer,
                                   scope='info_fc')
#   info_spatial = layers.fully_connected(layers.flatten(info),
#                                    num_outputs=8,
#                                    activation_fn=tf.tanh,
#                                    weights_regularizer=l1_regularizer,
#                                    scope='info_spatial')  
#   info_spatial = np.expand_dims(info_spatial, axis=1)
#   info_spatial = np.expand_dims(info_spatial, axis=1)
#   for i in range(len(info_spatial)):
#       for j in range(msize):
#           for k in range (msize):
#               info_spatial[i][j][k] = info_spatial[i][0][0]

  # Compute spatial actions
  feat_conv = tf.concat([mconv2, sconv2], axis=3)
  print("feat_conv")
  print(feat_conv.shape)
  
  spatial_action = layers.conv2d(feat_conv,
                                 num_outputs=1,
                                 kernel_size=1,
                                 stride=1,
                                 padding='same',
                                 activation_fn=tf.nn.relu,
                                 scope='spatial_action')
  spatial_action = tf.nn.softmax(layers.flatten(spatial_action))
  print("spatial")
  print(spatial_action.shape)
  
  # Compute non spatial actions and value
  feat_fc = tf.concat([layers.flatten(mconv2), layers.flatten(sconv2), info_fc], axis=1)
  feat_fc = layers.fully_connected(feat_fc,
                                   num_outputs=256,
                                   activation_fn=tf.nn.relu,
                                   #weights_regularizer=l2_regularizer,
                                   scope='feat_fc')
  print(feat_fc.shape)
  
  cell = tf.nn.rnn_cell.BasicLSTMCell(256)
  feat_fc1 = tf.expand_dims(feat_fc, 0)
  print(feat_fc1.shape)
  istate = cell.zero_state(1, dtype = tf.float32)
  output_rnn, states = tf.nn.dynamic_rnn(cell, feat_fc1, initial_state = istate)
  print(output_rnn.shape)
  output_rnn = tf.reduce_sum(output_rnn, 0)
  print(output_rnn.shape)
  non_spatial_action = layers.fully_connected(output_rnn,
                                              num_outputs=num_action,
                                              activation_fn=tf.nn.softmax,
                                              scope='non_spatial_action')
  print("hzjsb")
  print(non_spatial_action.shape)
  value = tf.reshape(layers.fully_connected(output_rnn,
                                            num_outputs=1,
                                            activation_fn=None,
                                            scope='value'), [-1])
  print(value.shape)
  print("sbhzj")

  return spatial_action, non_spatial_action, value