import os
import numpy as np
import tensorflow as tf
import argparse
import pickle
import copy
import sys
from Text_Load import TextLoader
from model import Model
#demo chatbot , prints output to the console
def get_paths(input_path):
    if os.path.isfile(input_path):
        model_path = input_path
        save_dir = os.path.dirname(model_path)
    return model_path, os.path.join(save_dir, 'config.pkl'), os.path.join(save_dir, 'chars_vocab.pkl')
def sample_main(args):
    model_path, config_path, vocab_path = get_paths(args.save_dir)
    with open(config_path, 'rb') as f:
        saved_args = pickle.load(f)
    with open(vocab_path, 'rb') as f:
        chars, vocab = pickle.load(f)
    print("Creating model...  ")
    saved_args.batch_size = args.beam_width
    net = Model(saved_args,True)
    config = tf.ConfigProto()
    with tf.Session(config=config) as sess:
        tf.global_variables_initializer().run()
        saver = tf.train.Saver(net.save_variables_list())
        print("Restoring weights...  ")
        saver.restore(sess, model_path)
        chatbot(net, sess, chars, vocab, args.n, args.beam_width,
                args.relevance, args.temperature, args.topn)
def chatbot(net, sess, chars, vocab, max_length, beam_width, relevance, temperature, topn):
    states = initial_state_with_relevance_masking(net, sess, relevance)
    while True:
        user_input = input('\n> ')
        user_command_entered, reset, states, relevance, temperature, topn, beam_width = process_user_command(
            user_input, states, relevance, temperature, topn, beam_width)
        if reset: states = initial_state_with_relevance_masking(net, sess, relevance)
        if not user_command_entered:
            states = forward_text(net, sess, states, relevance, vocab, sanitize_text(vocab, "> " + user_input + "\n>"))
            computer_response_generator = beam_search_generator(sess=sess, net=net,
                initial_state=copy.deepcopy(states), initial_sample=vocab[' '],
                early_term_token=vocab['\n']
                forward_args={'relevance':relevance, 'mask_reset_token':vocab['\n'], 'forbidden_token':vocab['>'],
                                'temperature':temperature, 'topn':topn})
            for i, char_token in enumerate(computer_response_generator):
                out_chars.append(chars[char_token])
                print(possibly_escaped_char(out_chars), end='', flush=True)
                states = forward_text(net, sess, states, relevance, vocab, chars[char_token])
                if i >= max_length: break
            states = forward_text(net, sess, states, relevance, vocab, sanitize_text(vocab, "\n> "))
def forward_text(net, sess, states, relevance, vocab, prime_text=None):
    if prime_text is not None:
      for char in prime_text:
        states = net.forward_model(sess, states, vocab[char])
    return states
def scale_prediction(prediction, temperature):
    if (temperature == 1.0): return prediction 
    np.seterr(divide='ignore')
    scaled_prediction = np.log(prediction) / temperature
    scaled_prediction = scaled_prediction - np.logaddexp.reduce(scaled_prediction)
    scaled_prediction = np.exp(scaled_prediction)
    np.seterr(divide='warn')
    return scaled_prediction
def forward_with_mask(sess, net, states, input_sample, forward_args):
    relevance = forward_args['relevance']
    mask_reset_token = forward_args['mask_reset_token']
    forbidden_token = forward_args['forbidden_token']
    temperature = forward_args['temperature']
    topn = forward_args['topn']
    prob, states = net.forward_model(sess, states, input_sample)
    prob[forbidden_token] = 0
    prob = prob / sum(prob)
    prob = scale_prediction(prob, temperature)
    return prob, states
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', type=int, default=500)
    parser.add_argument('--beam_width', type=int, default=2)
    parser.add_argument('--temperature', type=float, default=1.0)
    args = parser.parse_args()
    sample_main(args)



if __name__ == '__main__':
    main()
