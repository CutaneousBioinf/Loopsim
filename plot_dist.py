#!/usr/bin/env python3
"""Plot ratio distribution"""

import pandas as pd
import numpy as np
import seaborn as sb
import matplotlib as mp


def main():
    ratio_dist = pd.read_csv("ratio_dist")
    plt = sb.distplot(ratio_dist)
    plt.axvline(0.034299968818210166)
    fig = plt.get_figure()
    fig.savefig("plt.jpg")


if __name__ == "__main__":
    main()
