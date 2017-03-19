#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
sys.path.append('./signstream-xmlparser')
import analysis.signstream as ss

class Token(object):
    def __init__(self, ss_token):
        self.gloss = ss_token.get_text()
        self.start = ss_token.get_timecodes()[0]
        self.end   = ss_token.get_timecodes()[1]
        assert self.end > self.start

    def __str__(self):
        return "[{} {}]".format(self.gloss, self.end - self.start)

class HoldToken(Token):
    """Merged sign and HOLD"""
    def __init__(self, token, hold_ss_token):
        self.start = token.start
        self.end   = hold_ss_token.get_timecodes()[1]
        self.gloss = "{}/HOLD{}".format(
            token.gloss,
            hold_ss_token.get_timecodes()[1] - hold_ss_token.get_timecodes()[0] # hold length
        )

class Node(object):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.start = left.start
        self.end = right.end
        self.pause_length = right.start - left.end
        assert self.pause_length >= 0

    def _prepend_indent(self, s):
        return '\n'.join('  ' + line for line in s.split('\n'))

    def __str__(self):
        left_str = str(self.left)
        right_str = str(self.right)
        return "[{}\n{}\n{}]".format(
            self.pause_length,
            self._prepend_indent(str(self.left)),
            self._prepend_indent(str(self.right))
        )

def cleanup_utterance(utterance):
    """Convert SignStream tokens to lighter ones that only have the things we
       need, merge HOLDs into their preceding sign, and drop features besides
       the main gloss."""
    tokens = []
    for ss_token in utterance.get_tokens_for_field('main gloss'):
        if ss_token.get_text() == 'HOLD':
            tokens[-1] = HoldToken(tokens[-1], ss_token)
        else:
            tokens.append(Token(ss_token))
    return tokens

def process_gloss(cleaned):
    """Apply algorithm from Groçjean & Lane paper"""
    working = list(cleaned)
    while len(working) > 1:
        min_pause_len = float('Infinity')
        min_pause_pos = 0
        for i in range(len(working) - 1):
            pause_len = working[i + 1].start - working[i].end
            if pause_len < min_pause_len:
                min_pause_len = pause_len
                min_pause_pos = i
        merged = Node(working[i], working[i + 1])
        working = working[:i] + [merged] + working[i + 2:]
    return working[0]

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: {} <XML file>\n".format(sys.argv[0]))
        sys.exit(1)

    db = ss.SignStreamDatabase.read_xml(sys.argv[1])
    for person in db.get_participants():
        for utterance in person.get_utterances():
            tokens = cleanup_utterance(utterance)
            print 'Utterance:', ' '.join(t.gloss for t in tokens)
            tree = process_gloss(tokens)
            # if you want to further process the trees instead of just printing them, modify this
            print str(tree)
            print '\n\n'