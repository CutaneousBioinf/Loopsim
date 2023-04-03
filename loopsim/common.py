"""stuff needed across modules in this package, but we don't want it to be at the module level"""

from detect_delimiter import detect

delimiter = ""  # this will be set by the main cli call


def detect_delimiter(filename):
    with open(filename) as f:
        firstline = f.readline()
        return detect(firstline)
