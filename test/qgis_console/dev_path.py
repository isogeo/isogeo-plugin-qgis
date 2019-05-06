# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from os import path

# basic function to solve raw string problem
def raw_string(s):
    if isinstance(s, str):
        s = s.encode('string-escape')
    elif isinstance(s, unicode):
        s = s.encode('unicode-escape')
    else:
        raise TypeError
    return s


# fixture
target_nat = "\\TORCY\Data\SIG\SIG_DATA_SERVICE\DEMO\Evenements\GeoLittoral\n_azi_submersion_marine_s_092014\n_azi_submersion_marine_s.shp"
target_raw = r"\\TORCY\Data\SIG\SIG_DATA_SERVICE\DEMO\Evenements\GeoLittoral\n_azi_submersion_marine_s_092014\n_azi_submersion_marine_s.shp"
target_enc = target_nat.encode('utf8')
target_tra = r"{}".format(target_nat)
target_fct = raw_string(target_nat)

# types
print("Types and lengths")
print(type(target_nat), len(target_nat))
print(type(target_raw), len(target_raw))
print(type(target_enc), len(target_enc))
print(type(target_enc), len(target_fct))
print(type(target_tra), len(target_tra))

# exists?
print("\nos.path.exists")
print(path.exists(target_nat))
print(path.exists(target_raw))
print(path.exists(target_enc))
print(path.exists(target_fct))

# is file?
print("\nos.path.isfile")
print(path.isfile(target_nat))
print(path.isfile(target_raw))
print(path.isfile(target_enc))
print(path.isfile(target_fct))

# normed - is file?
print("\nos.path.normpath.isfile")
print(path.isfile(path.normpath(target_nat)))
print(path.isfile(path.normpath(target_raw)))
print(path.isfile(path.normpath(target_enc)))
print(path.isfile(path.normpath(target_fct)))

# realed - is file?
print("\nos.path.realpath.isfile")
print(path.isfile(path.realpath(target_nat)))
print(path.isfile(path.realpath(target_raw)))
print(path.isfile(path.realpath(target_enc)))
print(path.isfile(path.realpath(target_fct)))

# QGIS open
print("\nQGIS open")
try:
    open(target_raw)
except IOError:
    print("Missed something")
try:
    open(target_nat)
except IOError:
    print("Missed something")
try:
    open(target_enc)
except IOError:
    print("Missed something")
try:
    open(target_fct)
except IOError:
    print("Missed something")
