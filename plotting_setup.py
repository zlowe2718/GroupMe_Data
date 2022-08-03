import math
import matplotlib.pyplot as plt
import numpy as np


# start plotting
def set_labels(d):
    labels = []
    for name in d:
        labels.append(name)
    return labels


def rects_per_type(lists_by_type, label_by_type, fig, ax):
    x = np.arange(0, len(lists_by_type[0]) * 2, 2)
    width = .4
    bars = len(lists_by_type)

    for i in range(bars):
        rect = ax.bar(x - width * (bars - 1) * (1/2) + width * i,
                      lists_by_type[i], width, label=label_by_type[i])
        autolabel(rect, ax)


def rects(bay_list, bay_label, fig, ax):
    x = np.arange(0, len(bay_list) * 2, 2)
    width = .6

    rects1 = ax.bar(x, bay_list, width, label=bay_label)
    autolabel(rects1, ax)


def set_title_and_others(title, labels, fig, ax):
    ax.set_title(title)
    ax.set_xticks(np.arange(0, 2 * len(labels), 2))
    ax.set_xticklabels(labels)
    ax.legend()
    fig.tight_layout()


def autolabel(rects, ax):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')


def bayesian_rating(bayesian_dict, name):
    n = []
    for key, value in bayesian_dict[name].items():
        n.append(value)
    if sum(n) == 0:
        return 0

    K = len(n)
    z = 1.96
    N = sum(n)
    first_part = 0.0
    second_part = 0.0
    for k in range(K):
        first_part += k * (n[k] + 1) / (N + K)
        second_part += k * k * (n[k]+1) / (N+K)
    score = first_part - z * math.sqrt((second_part - first_part ** 2) / (N+K+1))
    return score
