# -*- coding: utf-8 -*-

from collections import defaultdict
from copy import deepcopy
import gzip
import sys, json
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import mvskoke as mv

# verbs_to_test = ['vyetv',
#                  'tvcetv',
#                  "letketv",
#                  "vpeletv",
#                  "vpoketv",
#                  "hvlketv",
#                  "hompetv",
#                  "vfvnketv",
#                  "hvoketv",
#                  "hueretv",
#                  "hvkihketv",
#                  "akkvretv",
#                  "folothoketv",
#                  "enlopicetv",
#                  "etepvkocetv",
#                  "hvkvnceropotketv",
#                  "vwvnayetv",
#                  "ak-vpoketv",
#                  "opunvyetv",
#                  "etekelketv"


#                 #  'mēcetv',
#                 #  'fēketv',
#                 #  'wvnvyetv',
#                  ]
verbs_to_test = [
    "vyetv",
    "vwvnayetv",
    "vwvnvyetv",
    "hayetv",
    "vpoketv",
    "fēketv",
    "esketv",
    "letketv",
    "hompetv",
    "vfvnketv",
    "tvmketv",
    "yefolketv",
    "hvkihketv",
    "akketv",
    "wakketv",
    "akhottetv",
    "fekhonnetv",
    "kerretv",
    "lentappetv",
    "liketv",
    "lvoketv",
    "cvpkuecetv",
    "hueretv",
]


def test_lgrade():
    print("L-grade test:")
    for word in verbs_to_test:
        verb = mv.Verb(word)
        print(f"\t{verb} -> {verb.l()}")


def test_hgrade():
    print("H-grade test:")
    for word in verbs_to_test:
        verb = mv.Verb(word)
        print(f"\t{verb} -> {verb.h()}")


with open(
    os.path.join(os.path.dirname(__file__), "../mvskoke/mvskoke_dic.json"),
    "r",
    encoding="utf-8",
) as f:
    mvskoke_dict = json.load(f)

active_verbs = [x for x in mvskoke_dict if x["headword"].endswith("etv")]
three_or_more = [
    x
    for x in active_verbs
    if len(x["senses"]) > 0 and "of three or more" in x["senses"][0]["definition"]
]
one = [
    x
    for x in active_verbs
    if len(x["senses"]) > 0 and "of one" in x["senses"][0]["definition"]
]
two = [
    x
    for x in active_verbs
    if len(x["senses"]) > 0
    and "of two" in x["senses"][0]["definition"]
    and "of two or more" not in x["senses"][0]["definition"]
]
two_or_more = [
    x
    for x in active_verbs
    if len(x["senses"]) > 0 and "of two or more" in x["senses"][0]["definition"]
]

one_set = {x["headword"] for x in one}
two_set = {x["headword"] for x in two}
two_or_more_set = {x["headword"] for x in two_or_more}
three_or_more_set = {x["headword"] for x in three_or_more}

print(f"Active Verbs: {len(active_verbs)}")
v_objs = [mv.Verb(x["headword"], x["pronunciations"]) for x in active_verbs]

# test_lgrade()
# for word in verbs_to_test:
#     mv.Verb(word).show_all_grades()
test_hgrade()


verb_clusters = dict()
for verb in three_or_more:
    print(verb["headword"])
    if "see" in verb.keys():
        related_words = verb["see"]
        verb_clusters[verb["headword"]] = {x["headword"] for x in related_words}

defective_3 = {x: y for x, y in verb_clusters.items() if len(y) < 2}
verb_clusters = dict()
for verb in two:
    print(verb["headword"])
    if "see" in verb.keys():
        related_words = verb["see"]
        verb_clusters[verb["headword"]] = {x["headword"] for x in related_words}
defective_2 = {x: y for x, y in verb_clusters.items() if len(y) < 2}
verb_clusters = dict()
for verb in two_or_more:
    print(verb["headword"])
    if "see" in verb.keys():
        related_words = verb["see"]
        verb_clusters[verb["headword"]] = {x["headword"] for x in related_words}
defective_2_or_more = {x: y for x, y in verb_clusters.items() if len(y) < 1}

print("one entries: ", len(one))
print("two entries: ", len(two))
print("two or more entries: ", len(two_or_more))
print("three_or_more entries: ", len(three_or_more))
print("defective_2 entries: ", len(defective_2))
print("defective_2 or more entries: ", len(defective_2_or_more))
print("defective_3 entries: ", len(defective_3))
sample_obj = {"one": "", "two": "", "two_or_more": "", "three_or_more": ""}
# make a defaultdict that return sample_obj if key is not found
combined = defaultdict(lambda: deepcopy(sample_obj))
for current_set in [one, two, two_or_more, three_or_more]:
    for verb in current_set:
        word = verb["headword"]
        if word in one_set:
            combined[word] = combined[word]
            combined[word]["one"] = word
        if "see" in verb.keys():
            related_words = verb["see"]
            for related_word in related_words:
                combined[word]["one"] = (
                    related_word["headword"]
                    if related_word["headword"] in one_set
                    else combined[word]["one"]
                )
                combined[word]["two"] = (
                    related_word["headword"]
                    if related_word["headword"] in two_set
                    else combined[word]["two"]
                )
                combined[word]["two_or_more"] = (
                    related_word["headword"]
                    if related_word["headword"] in two_or_more_set
                    else combined[word]["two_or_more"]
                )
                combined[word]["three_or_more"] = (
                    related_word["headword"]
                    if related_word["headword"] in three_or_more_set
                    else combined[word]["three_or_more"]
                )
all_pluriform = set(combined.keys())
one_full = {x: y for x, y in combined.items() if x in one_set}
active_verbs_dict = defaultdict(lambda: deepcopy(sample_obj))
for verb in active_verbs:
    word = verb["headword"]
    if word in one_set or word not in all_pluriform:
        active_verbs_dict[word] = combined[word]
        if active_verbs_dict[word]["one"] == "":
            active_verbs_dict[word]["one"] = word
        active_verbs_dict[word]["raw_entry"] = verb

rest = [x for x in active_verbs if x["headword"] not in all_pluriform]
assert len(rest) + len(all_pluriform) == len(active_verbs)


def conjugate_verb(verb):
    if type(verb) == str:
        verb = active_verbs_dict[verb]
    conjugations = defaultdict(lambda: "")
    conjugations["raw_entry"] = verb["raw_entry"]
    conjugations["1p"] = mv.Verb(verb["one"])
    conjugations["2p"] = mv.Verb(verb["one"])
    conjugations["3p"] = mv.Verb(verb["one"])
    if verb["two"]:
        conjugations["2p"] = mv.Verb(verb["two"])
    if verb["two_or_more"]:
        conjugations["2p"] = mv.Verb(verb["two_or_more"])
        conjugations["3p"] = mv.Verb(verb["two_or_more"])
    if verb["three_or_more"]:
        conjugations["3p"] = mv.Verb(verb["three_or_more"])
    try:
        # First Person Singular
        conjugations["1ps_pres_basic"] = conjugations["1p"].stem + "is"
        conjugations["1ps_pres_tos"] = conjugations["1p"].stem + "iyē tos"
        conjugations["1ps_pres_ometv"] = conjugations["1p"].stem + "e towis"

        # Second Person Singular
        conjugations["2ps_pres_basic"] = [
            conjugations["1p"].stem + suffix
            for suffix in ["skes", "eckes", "eccces", "etces"]
        ]
        conjugations["2ps_pres_tos"] = [
            conjugations["1p"].stem + suffix + " tos"
            for suffix in ["skē", "eckē", "eccē", "etcē"]
        ]
        conjugations["2ps_pres_ometv"] = [
            conjugations["1p"].stem + "e to" + suffix
            for suffix in ["wetskes", "weckes", "wecces", "ntces", "nckes"]
        ]

        # Third Person Singular
        conjugations["3ps_pres_basic"] = conjugations["1p"].stem + "s"
        conjugations["3ps_pres_tos"] = conjugations["1p"].stem + "ē tos"
        conjugations["3ps_pres_ometv"] = conjugations["1p"].stem + "e tos"

        # First Person Plural 2
        conjugations["1pp_pres_basic"] = conjugations["2p"].stem + "ēs"
        conjugations["1pp_pres_tos"] = conjugations["2p"].stem + "eyē tos"
        conjugations["1pp_pres_ometv"] = conjugations["2p"].stem + "e towēs"

        # First Person Plural more
        conjugations["1pp+_pres_basic"] = conjugations["3p"].stem + "ēs"
        conjugations["1pp+_pres_tos"] = conjugations["3p"].stem + "eyē tos"
        conjugations["1pp+_pres_ometv"] = conjugations["3p"].stem + "e towēs"

        # Second Person Plural 2
        conjugations["2pp_pres_basic"] = [
            conjugations["2p"].stem + suffix for suffix in ["atskes", "ackes"]
        ]
        conjugations["2pp_pres_tos"] = [
            conjugations["2p"].stem + suffix + " tos" for suffix in ["atskē", "ackē"]
        ]
        conjugations["2pp_pres_ometv"] = [
            conjugations["2p"].stem + "e towa" + suffix for suffix in ["tskes", "ckes"]
        ]
        # Second Person Plural more
        conjugations["2pp+_pres_basic"] = [
            conjugations["3p"].stem + suffix for suffix in ["atskes", "ackes"]
        ]
        conjugations["2pp+_pres_tos"] = [
            conjugations["3p"].stem + suffix + " tos" for suffix in ["atskē", "ackē"]
        ]
        conjugations["2pp+_pres_ometv"] = [
            conjugations["3p"].stem + "e towa" + suffix for suffix in ["tskes", "ckes"]
        ]

        # Third Person Plural 2
        conjugations["3pp_pres_basic"] = conjugations["2p"].stem + "akes"
        conjugations["3pp_pres_tos"] = conjugations["2p"].stem + "akē tos"
        conjugations["3pp_pres_ometv"] = conjugations["2p"].stem + "e towakes"
        # Third Person Plural more
        conjugations["3pp+_pres_basic"] = conjugations["3p"].stem + "akes"
        conjugations["3pp+_pres_tos"] = conjugations["3p"].stem + "akē tos"
        conjugations["3pp+_pres_ometv"] = conjugations["3p"].stem + "e towakes"
    except Exception as e:
        print(e)
        breakpoint()
    return conjugations


all_conjugations = [conjugate_verb(verb) for verb in active_verbs_dict.values()]
liketv = conjugate_verb("liketv")

# make the quiz format
quiz = []
for verb in all_conjugations:
    if "raw_entry" in verb.keys():
        sound_url = (
            verb["raw_entry"]["pronunciations_audio"][0]["server_url"]
            if len(verb["raw_entry"]["pronunciations_audio"]) > 0
            else None
        )
        show1 = True
        show2 = True
        show3 = True
        if verb["1p"].stem == verb["2p"].stem and verb["1p"].stem == verb["3p"].stem:
            show2 = False
            show3 = False
        # If 1p and 3p are the same but 2p is different
        elif verb["2p"].stem == verb["3p"].stem and verb["1p"].stem != verb["2p"].stem:
            show3 = False
        # breakpoint()
        d = (
            verb["raw_entry"]["senses"][0]["definition"]
            if len(verb["raw_entry"]["senses"]) > 0
            else "Data not loaded..."
        )
        definition = f"{verb['1p'].root} - {d}"
        # { f: "Data not loaded...", m: "circunstancial", s: "ixé", o: "xé" },

        for key, value in [
            x
            for x in verb.items()
            if ("+" in x[0] and show3) or ("+" not in x[0] and not show3)
        ]:
            if key in ["1p", "2p", "3p", "raw_entry"]:
                continue
            if type(value) == str:
                values = [value]
            for v in values:
                quiz.append(
                    {
                        "surl": sound_url,
                        "f": v,
                        "m": key.split("_")[1],
                        "s": key.split("_")[0],
                        "o": None,
                        "d": definition,
                    }
                )
# write all_conjugations to a file
with open(
    os.path.join(os.path.dirname(__file__), "../../quiz/all_conjugations.json"),
    "w",
    encoding="utf-8",
) as f:
    json.dump(all_conjugations, f, cls=mv.VerbEncoder, ensure_ascii=False, indent=4)
    # also save the same json minified and gziped
with gzip.open(
    os.path.join(os.path.dirname(__file__), "../../quiz/quiz.json.gz"),
    "wt",
    encoding="utf-8",
) as f:
    json.dump(quiz, f, cls=mv.VerbEncoder, ensure_ascii=False)
