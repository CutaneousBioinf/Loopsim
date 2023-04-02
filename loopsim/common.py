"""stuff needed across modules in this package"""


from detect_delimiter import detect

delimiter = ""  # this will be set by the main cli call


def detect_delimiter(filename):
    with open(filename) as f:
        firstline = f.readline()
        return detect(firstline)