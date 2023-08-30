#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 17:04:06 2023

@author: adamsun

Augment sentences in dataset for pretraining
"""

import pandas as pd
import re
import json
import random
import os
import time

from SoundsLike.SoundsLike import Search

# Read sentences
min_len = 4
data = pd.read_csv('mtsamples.csv')
transcriptions = data["transcription"]
all_medical_sentences = []
for transcript in data["transcription"]:
    m = re.sub(r'\b[A-Z]+\b', '', str(transcript))
    m = re.sub('[:,]', '', m)
    all_medical_sentences += [sentence.strip()
                              for sentence in m.split(".") if len(sentence.split(' ')) > min_len]
    # print(all_medical_sentences)

with open("homo_dict.json", "r") as f:
    homo_dict = json.load(f)
# Load random conversations
with open("CasualConversations_transcriptions.json") as f:
    data = json.load(f)
all_conversational_lines = []
for data_line in data:
    data_transcript = data_line['transcription']
    data_transcript = re.sub("[\<\[].*?[\>\]]", "", data_transcript)
    data_transcript = re.sub('[:,]', '', data_transcript)
    all_conversational_lines += [x.strip() for x in re.split(
        '[.?]', data_transcript) if len(x.split(' ')) > min_len]
    # print(all_conversational_lines)

with open("medical_dict.json", "r") as f:
    medical_dict = json.load(f)

# Augment all_medical_sentences to randomly include lines from all_conversational_lines, and include fillers etc

print(len(all_conversational_lines), len(all_medical_sentences))
# 523,033 181,387

filler_words = [
    "let's",
    "absolutely",
    "actual",
    "actually",
    "amazing",
    "anyway",
    "apparently",
    "approximately",
    "badly",
    "basically",
    "begin",
    "certainly",
    "clearly",
    "completely",
    "definitely",
    "easily",
    "effectively",
    "entirely",
    "especially",
    "essentially",
    "exactly",
    "extremely",
    "fairly",
    "frankly",
    "frequently",
    "fully",
    "generally",
    "hardly",
    "heavily",
    "highly",
    "hopefully",
    "just",
    "largely",
    "like",
    "literally",
    "maybe",
    "might",
    "most",
    "mostly",
    "much",
    "necessarily",
    "nicely",
    "obviously",
    "ok",
    "okay",
    "particularly",
    "perhaps",
    "possibly",
    "practically",
    "precisely",
    "primarily",
    "probably",
    "quite",
    "rather",
    "real",
    "really",
    "relatively",
    "right",
    "seriously",
    "significantly",
    "simply",
    "slightly",
    "so",
    "specifically",
    "start",
    "strongly",
    "stuff",
    "surely",
    "things",
    "too",
    "totally",
    "truly",
    "try",
    "typically",
    "ultimately",
    "usually",
    "very",
    "virtually",
    "well",
    "whatever",
    "whenever",
    "wherever",
    "whoever",
    "widely",
]


def delete_words(line):
    line_list = line.split(" ")
    prev_len = len(line_list)
    num_deleted_words = random.randint(1, max(1, int(len(line_list)/10)))
    word_poses = random.sample(range(len(line_list)), num_deleted_words)
    for word_pose in word_poses:
        line_list[word_pose] = ""
    line = " ".join(line_list)
    line = re.sub(' +', ' ', line)
    after_len = len(line_list)
    # print(f"deleted {num_deleted_words} words, prev {prev_len}, now {after_len}")
    return line

def add_repetition(line):
    line_list = line.split(" ")
    num_repetition_words = random.randint(1, max(1, min(int(len(line_list)), 5)))
    rep_pos = random.randint(0, 2)
    # three kinds
    # C, A, B, C
    # A, B, C, B, C
    # A, A, B, C
    rep_words = line_list[-num_repetition_words:]
    if rep_pos == 0: # add repetition ahead
        line_list = rep_words + line_list
    elif rep_pos == 1:
        line_list = line_list + rep_words
    else:
        sub_set = [x for x in line_list if x not in rep_words]
        line_list = sub_set + line_list
    line = " ".join(line_list)
    # print(f"added repetition with {rep_words}, to {line}")
    return line


def add_filler_words(line):
    tik = time.time()
    line_list = line.split(" ")
    num_filler_words = random.randint(1, max(1, int(len(line_list)/30)))
    for _ in range(num_filler_words):
        random_filler_word = random.choice(filler_words)
        # print(f"addding filler word {random_filler_word}")
        random_pos = random.randint(0, len(line_list))
        # print(random_filler_word)
        line = " ".join(line_list[:random_pos]) + " " + \
            random_filler_word + " " + " ".join(line_list[random_pos:])
        line_list = line.split(" ")
    tok = time.time()
    print(f"add filler words took {tok - tik}s")
    return line


def homonym_word(line):
    tiktik = time.time()
    line_list = line.split(" ")
    num_homonym = random.randint(1, max(1, int(len(line_list))))
    words = random.sample(line_list, num_homonym)
    for idx, word in enumerate(words):
        # random_pos = random.randint(0, len(line_list)-1)
        # while random_pos in tried_poses:
        #     if tried_poses == len(line_list):
        #         break
        #     random_pos = random.randint(0, len(line_list)-1)
        # tried_poses.append(random_pos)
        try:
            tik = time.time()
            homonyms = homo_dict[word]
            tok = time.time()
            print(f"searching homophones used {tok - tik} s")
            for homo in homonyms:
                if homo.lower() != word.lower():
                    homonym = homo
                    # print(f"homonym pair: {line_list[random_pos]}, {homonym}")
                    break
            homonym = word
        except:
            homonym = word
        line_list[idx] = homonym
    # print(line_list)
    toktok = time.time()
    print(f"made homonyms take {toktok - tiktik} s")
    return " ".join(line_list)

def add_medical(line):
    add_prob = random.randint(0, 5)
    line_list = line.split(" ")
    if add_prob == 0:
        medical_word = random.sample(list(medical_dict.keys()), 1)[0]
        random_pos = random.randint(0, len(line_list))
        line = " ".join(line_list[:random_pos]) + " " + \
            medical_word + " " + " ".join(line_list[random_pos:])
        if medical_dict[medical_word]:
            homo_medical_word = random.sample(medical_dict[medical_word], 1)[0]
            corrupt_line = " ".join(line_list[:random_pos]) + " " + \
                homo_medical_word + " " + " ".join(line_list[random_pos:])
        else:
            corrupt_line = line
    else:
        return line, line
    
    return line, corrupt_line



def do_nothing(line):
    return line

agument_methods_plus = {'add': add_filler_words, 'rep': add_repetition, 'delete': delete_words, 'homo': homonym_word, 'med': add_medical}

agument_methods = {'add': add_filler_words, 'rep': add_repetition, 'delete': delete_words, 'homo': homonym_word}

agument_methods_1 = {'add': add_filler_words, 'rep': add_repetition, 'delete': delete_words, 'homo': do_nothing}

agument_methods_2 = {'add': add_filler_words, 'rep': add_repetition, 'delete': do_nothing, 'homo': do_nothing}

agument_methods_3 = {'add': add_filler_words, 'rep': do_nothing, 'delete': do_nothing, 'homo': do_nothing}

agument_methods_4 = {'add': do_nothing, 'rep': do_nothing, 'delete': do_nothing, 'homo': do_nothing}

agument_methods_oarm = {'add': add_filler_words, 'rep': add_repetition, 'delete': do_nothing, 'homo': do_nothing, 'med': add_medical}
agument_methods_oam = {'add': add_filler_words, 'rep': do_nothing, 'delete': do_nothing, 'homo': do_nothing, 'med': add_medical}
agument_methods_oadm = {'add': add_filler_words, 'rep': do_nothing, 'delete': delete_words, 'homo': do_nothing, 'med': add_medical}
agument_methods_oahm = {'add': add_filler_words, 'rep': do_nothing, 'delete': do_nothing, 'homo': homonym_word, 'med': add_medical}

def generate_json_data(all_conversational_lines, all_medical_sentences):
    data_dict = {}
    cur_agument_methods = agument_methods_oahm
    while all_medical_sentences:
        # print(len(all_medical_sentences))
        if len(all_conversational_lines) > 0 and len(all_medical_sentences) > 0:
            set_idx = random.randint(0, 20)
        elif len(all_conversational_lines) == 0:
            set_idx = 0
        else:
            set_idx = 1
        if set_idx == 0:
            conversation_line = random.choice(all_conversational_lines)
            all_conversational_lines.remove(conversation_line)
            res = {'RAW': "", 'ASR': conversation_line}
        else:
            medical_line = random.choice(all_medical_sentences)
            all_medical_sentences.remove(medical_line)
            num_agument = random.randint(0, len(cur_agument_methods))
            # print(f"We chose {num_agument} ways to augment")
            if num_agument:
                # print(list(agument_methods.keys()))
                methods = random.sample(
                    list(cur_agument_methods.keys()), num_agument)
                for method in methods:
                    if method == 'med':
                        medical_line, line = cur_agument_methods[method](medical_line)
                        print(f"add medical, {medical_line}, {line}")
                    else:
                        line = cur_agument_methods[method](medical_line)
            else:
                line = medical_line
            res = {'RAW': medical_line, 'ASR': line}
        data_dict[str(len(data_dict)+1)] = res
    return data_dict


cur_dir = os.getcwd()
# data_folder = 'narr_rehearsals'
# folder = os.path.join(cur_dir, data_folder)
epoches = (len(all_medical_sentences) // 1000) + 1
for epoch in range(1, epoches+1):
    print(epoch)
    if epoch == epoches:
        # print(f"{(epoch-1)*2883}:{len(all_conversational_lines)}",
        #       f"{(epoch-1)*1000}:{len(all_medical_sentences)}")
        data_dict = generate_json_data(
            all_conversational_lines[(epoch-1)*2883:], all_medical_sentences[(epoch-1)*1000:])
    else:
        data_dict = generate_json_data(
            all_conversational_lines[(epoch-1)*2883:epoch*2883], all_medical_sentences[(epoch-1)*1000:epoch*1000])
        # print(f"{(epoch-1)*2883}:{epoch*2883}",
        #       f"{(epoch-1)*1000}:{epoch*1000}")
    with open(os.path.join(cur_dir, f'augmented_v3_OAHM_{epoch}.json'), 'w') as convert_file:
        convert_file.write(json.dumps(data_dict, indent=2))


# with open(os.path.join(cur_dir, 'augmented.json'), 'w') as convert_file:
#     convert_file.write(json.dumps(data_dict, indent=2))
