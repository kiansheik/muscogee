# -*- coding: utf-8 -*-
import json
from . import helpers
from copy import deepcopy


class Verb:
    def __init__(self, root, pronunciation=None):
        self.pronunciation = None
        if pronunciation:
            self.pronunciation = helpers.clean_symbols(pronunciation)
        self.root = helpers.clean_symbols(root)
        self.active = False
        self.stem = self.root
        if self.root.endswith("etv"):
            self.active = True
            self.stem = self.root[:-3]
        self.grade = None

    # apply l grade
    def l(self):
        # make deep copy
        new = deepcopy(self)
        new.grade = "l"
        return new

    # apply f grade
    def f(self):
        # make deep copy
        new = deepcopy(self)
        new.grade = "f"
        return new

    def h(self):
        # make deep copy
        new = deepcopy(self)
        new.grade = "h"
        return new

    def n(self):
        # make deep copy
        new = deepcopy(self)
        new.grade = "n"
        return new

    def show_all_grades(self):
        print("Original: ", self)
        print("L grade: ", self.l())
        # print("H grade: ", self.h())
        print("N grade: ", self.n())
        print("F grade: ", self.f())

    def to_dict(self):
        return {
            "root": self.root,
            "stem": self.stem,
            "pronunciation": self.pronunciation,
            "lgrade": str(self.l()),
            "hgrade": str(self.h()),
            "ngrade": str(self.n()),
            "fgrade": str(self.f()),
        }

    def __str__(self):
        stem = self.stem
        if self.grade == "l":
            stem = helpers.lgrade(self.stem)
        elif self.grade == "h":
            stem = helpers.hgrade(self.stem)
        elif self.grade == "n":
            stem = helpers.ngrade(self.stem)
        elif self.grade == "f":
            stem = helpers.fgrade(self.stem)
        conjugation = "" if self.grade else ("etv" if self.active else stem + "ē")
        return stem + conjugation

    def __repr__(self):
        return self.__str__()


class VerbEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Verb):
            return Verb.to_dict(obj)
        return super().default(obj)
