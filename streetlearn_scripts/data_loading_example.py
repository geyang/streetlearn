from os.path import expanduser

from streetlearn import StreetLearnDataset


if __name__ == '__main__':
    path = expanduser(f"~/fair/streetlearn/processed-data/manhattan-large")
    d = StreetLearnDataset(path)
    d.select_bbox(-73.997, 40.726, 0.01, 0.008)
    d.show_bbox(show=True)
    d.show_blowout("NYC-large", show=True)

    # 1. get data
    # 2. build graph
    # 3. get start and goal
    # 4. make plans
    print(d)
