from os.path import expanduser

from streetlearn import StreetLearnDataset


class Args:
    pad = 0.1


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import numpy as np

    path = expanduser(f"~/fair/streetlearn/processed-data/manhattan-large")
    d = StreetLearnDataset(path)
    d.select_bbox(-73.997, 40.726, 0.01, 0.008)
    d.show_blowout("NYC-large", show=True)

    a = d.bbox[0] + d.bbox[2] * Args.pad, d.bbox[1] + d.bbox[3] * Args.pad
    b = d.bbox[0] + d.bbox[2] * (1 - Args.pad), d.bbox[1] + d.bbox[3] * (1 - Args.pad)
    start, goal = d.locate_closest(*a), d.locate_closest(*b)
    print(start, goal)

    fig = plt.figure(figsize=(6, 5))
    plt.scatter(*d.lng_lat[start], marker="o", s=100, linewidth=3,
                edgecolor="black", facecolor='none', label="start")
    plt.scatter(*d.lng_lat[goal], marker="x", s=100, linewidth=3,
                edgecolor="none", facecolor='red', label="end")
    plt.legend(loc="upper left", bbox_to_anchor=(0.95, 0.7), framealpha=1,
               frameon=False, fontsize=12)
    d.show_blowout("NYC-large", fig=fig, box_color='gray', box_alpha=0.3, show=True, set_lim=True)

    # 1. get data
    # 2. build graph
    # 3. get start and goal
    # 4. make plans

    print(d)
