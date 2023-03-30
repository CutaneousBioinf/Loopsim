"""Plot ratio distribution"""

import matplotlib as mp
import numpy as np
import pandas as pd
import seaborn as sb
from scipy import stats as st


def visualize():
    ratio_dist = pd.read_csv("../ratio_dist", header=None)
    plt = sb.distplot(ratio_dist)
    plt.axvline(0.034299968818210166, color="red")
    plt.set(xlabel="")
    # plt.legend()

    fig = plt.get_figure()
    fig.savefig("plt.jpg")

    print(ratio_dist)

    print(st.ttest_1samp(a=ratio_dist[0].to_numpy(), popmean=np.mean(ratio_dist[0])))
