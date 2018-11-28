import tensorflow as tf
from tensorflow.python.ops import rnn_cell
from tensorflow.python.ops import nn_ops
from tensorflow.python.ops import variable_scope as vs
from tensorflow.python.framework import ops
from tensorflow.contrib import rnn
from tensorflow.python.util.nest import flatten
import numpy as np

class Model():
    def __init__(self, args, infer=False): 
        self.args = args
        if infer:
            args.batch_size = 1
            args.seq_length = 1
            cell_fn = rnn_cell.BasicRNNCell
        self.lr = tf.Variable(args.learning_rate, trainable=False)
        self.ep_frac= tf.Variable(0.0, trainable=False)
        self.sec_passed = tf.Variable(0.0, trainable=False)
        cell = PartitionedRNNCell(cell_fn, partitions=args.num_blocks,
            partition_size=args.block_size, layers=args.num_layers)
        self.input_data = tf.placeholder(tf.int32, [args.batch_size, args.seq_length])
        #self.zero_state = cell.zero_state(args.batch_size, tf.float32)
        self.initial_state = _rnn_state_placeholders(self.zero_state)
        with tf.variable_scope('rnnlm'):
            softmax_w = tf.get_variable("softmax_w", [layer_size, args.vocab_size])
            softmax_b = tf.get_variable("softmax_b", [args.vocab_size])
       
        outputs, self.final_state = tf.nn.dynamic_rnn(cell, inputs,
                initial_state=self.initial_state, scope='rnnlm'
        output = tf.reshape(outputs, [-1, layer_size])
        if infer:
           
            self.probs = tf.nn.softmax(self.logits)
        else:
            self.targets = tf.placeholder(tf.int32, [args.batch_size, args.seq_length])
            loss = nn_ops.sparse_softmax_cross_entropy_with_logits(
                labels=tf.reshape(self.targets, [-1]), logits=self.logits)
            self.cost = tf.reduce_mean(loss)
            


            tvars = tf.trainable_variables() 
            grads, _ = tf.clip_by_global_norm(tf.gradients(self.cost, tvars),
                     args.grad_clip)
            optimizer = tf.train.AdamOptimizer(self.lr) 
            self.train_op = optimizer.apply_gradients(zip(grads, tvars)
            self.summary_op = tf.summary.merge_all()

class PartitionedRNNCell(rnn_cell.RNNCell):
    def __init__(self, cell_fn, partition_size=128, partitions=1, layers=2):
        super(PartitionedRNNCell, self).__init__(
        self._cells = []
        for i in range(layers):
          self._cells.append([cell_fn(partition_size) for _ in range(partitions)])
        self._partitions = partitions
    @property
    def state_size(self):
        return np.array(((layer[0].state_size,) * len(layer)) for layer in self._cells)
    @property
    def output_size(self):
        return self._cells[-1][0].output_size * len(self._cells[-1])
    def call_fn(self, inputs, state):
        layer_input = inputs
        new_states = []
        for l, layer in enumerate(self._cells):
            if l > 0:
              offset_width = layer[0].output_size // 2
              axis=1, name='concat_offset_%d' % l)
            p_outputs = []
            p_states = []
            for p, p_inp in enumerate(p_inputs):
              with vs.variable_scope("cell_%d_%d" % (l, p)):
              	#output=append[p_in]
                p_state = state[l][p]
                cell = layer[p]
                p_out, new_p_state = cell(p_inp, p_state)
                p_outputs.append(p_out)
                p_states.append(new_p_state)
            new_states.append(tuple(p_states))
            layer_input = tf.concat(p_outputs, axis=1, name='concat_%d' % l)
        new_states = tuple(new_states)
        return layer_input, new_states

 def add_state_to_feed_dict(self, feed_dict, state):
        for i, tensor in enumerate(flatten(state)):
            feed_dict[self._flattened_initial_state[i]] = tensor

  def save_variables_list(self):
        save_vars = set(tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope='rnnlm'))
        save_vars.update({self.lr, self.global_epoch_fraction, self.global_seconds_elapsed})
        return list(save_vars)

    def forward_model(self, sess, state, input_sample):
        shaped_input = np.array([[input_sample]], np.float32)
        inputs = {self.input_data: shaped_input}
        self.add_state_to_feed_dict(inputs, state)
        [probs, state] = sess.run([self.probs, self.final_state], feed_dict=inputs)
        return probs[0], state
