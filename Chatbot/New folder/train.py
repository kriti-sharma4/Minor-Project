import numpy as np
import tensorflow as tf
import argparse
import time, datetime
import os
import pickle
import sys
from Text_Load import TextLoader
from model import Model

def train(args):
    data_loader = TextLoader(args.data_dir, args.batch_size, args.seq_length)
    args.vocab_size = data_loader.vocab_size
    load_model = False
    if  os.path.exists(args.save_dir):
        os.mkdir(args.save_dir)
    model = Model(args)
    print("Total trainable parameters: {:,d}".format(model.trainable_parameter_count()))
    config = tf.ConfigProto(log_device_placement=False)
    with tf.Session(config=config) as sess:
        tf.global_variables_initializer().run()
        saver = tf.train.Saver(model.save_variables_list(), max_to_keep=3)
        if (load_model):
            print("Loading saved parameters")
            saver.restore(sess, ckpt.model_checkpoint_path)
        global_epoch_fraction = sess.run(model.global_epoch_fraction)
        global_seconds_elapsed = sess.run(model.global_seconds_elapsed)
        data_loader.cue_batch_pointer_to_epoch_fraction(global_epoch_fraction)
        initial_batch_step = int((global_epoch_fraction
                - int(global_epoch_fraction)) * data_loader.total_batch_count)
        epoch_range = (int(global_epoch_fraction),
                args.num_epochs + int(global_epoch_fraction))
        writer = tf.summary.FileWriter(args.save_dir, graph=tf.get_default_graph())
        outputs = [model.cost, model.final_state, model.train_op, model.summary_op]
        global_step = epoch_range[0] * data_loader.total_batch_count + initial_batch_step
        avg_loss = 0
        avg_steps = 0
        try:
            for e in range(*epoch_range):
                state = sess.run(model.zero_state)
                batch_range = (initial_batch_step, data_loader.total_batch_count)
                initial_batch_step = 0
                for b in range(*batch_range):
                    global_step += 1
                    start = time.time()
                    x, y = data_loader.next_batch()
                    feed = {model.input_data: x, model.targets: y}
                    model.add_state_to_feed_dict(feed, state)
                    train_loss, state, _, summary = sess.run(outputs, feed)
                    elapsed = time.time() - start
                    global_seconds_elapsed += elapsed
                    writer.add_summary(summary, e * batch_range[1] + b + 1)
                    if avg_steps < 100: avg_steps += 1
                    avg_loss = 1 / avg_steps * train_loss + (1 - 1 / avg_steps) * avg_loss
                    #print("{:,d} / {:,d} (epoch {:.3f} / {}), loss {:.3f} (avg {:.3f}), {:.3f}s" \
                        #.format(b, batch_range[1], e + b / batch_range[1], epoch_range[1],
                         #   train_loss, avg_loss, elapsed))
                    if (e * batch_range[1] + b + 1) % args.save_every == 0 \
                            or (e == epoch_range[1] - 1 and b == batch_range[1] - 1):
                        save_model(sess, saver, model, args.save_dir, global_step,
                                data_loader.total_batch_count, global_seconds_elapsed)  
        finally:
            writer.flush()
            global_step = e * data_loader.total_batch_count + b
            save_model(sess, saver, model, args.save_dir, global_step,
                    data_loader.total_batch_count, global_seconds_elapsed)


            
def save_model(sess, saver, model, save_dir, global_step, steps_per_epoch, global_seconds_elapsed):
    global_epoch_fraction = float(global_step) / float(steps_per_epoch)
    checkpoint_path = os.path.join(save_dir, 'model.ckpt')
    sess.run(tf.assign(model.global_epoch_fraction, global_epoch_fraction))
    sess.run(tf.assign(model.global_seconds_elapsed, global_seconds_elapsed))
    saver.save(sess, checkpoint_path, global_step = global_step)
    print("\rSaved model to {} (epoch fraction {:.3f}).   ".format(checkpoint_path, global_epoch_fraction))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, default='data/scotus')
    parser.add_argument('--save_dir', type=str, default='models/new_save')
    parser.add_argument('--block_size', type=int, default=1024)
    parser.add_argument('--num_blocks', type=int, default=2)
    parser.add_argument('--num_layers', type=int, default=3)
    parser.add_argument('--model', type=str, default='gru')
    parser.add_argument('--batch_size', type=int, default=40)
    parser.add_argument('--num_epochs', type=int, default=50)
    parser.add_argument('--save_every', type=int, default=5000)
    parser.add_argument('--grad_clip', type=float, default=5.)
    parser.add_argument('--learning_rate', type=float, default=1e-5)
    parser.add_argument('--decay_rate', type=float, default=0.975)
    parser.add_argument('--decay_steps', type=int, default=100000)
    parser.add_argument('--set_learning_rate', type=float, default=-1)
    args = parser.parse_args()
    train(args)

if __name__ == '__main__':
    main()
