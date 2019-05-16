import os
from termcolor import cprint
from os.path import expanduser
import numpy as np

from streetlearn import chunk

if __name__ == "__main__":
    # %%
    from contextlib import closing
    import plyvel
    from streetlearn.buff import streetlearn_pb2 as street
    from tqdm import tqdm

    # to protect from accidental runs
    exit()

    # %%
    db_path = expanduser("~/fair/streetlearn/data/manhattan_512")
    os.makedirs("figures", exist_ok=True)

    coords = []
    compressed_images = []
    with closing(plyvel.DB(db_path, create_if_missing=False)) as db:
        for k, v in tqdm(db):
            if k == b'panos_connectivity':
                pass
            else:
                pano = street.Pano()
                pano.ParseFromString(v)
                coords.append(dict(lat=pano.coords.lat, lng=pano.coords.lng))
                compressed_images.append(pano.compressed_image)
                del pano

    # %%
    os.makedirs("../processed-data/manhattan/view_512", exist_ok=True)
    np.save("../processed-data/manhattan/coords.npy", np.array(coords))
    for i, _ in enumerate(tqdm(chunk(compressed_images, chunk_size=2000))):
        np.save("../processed-data/manhattan/view_512/chunk_{:04d}.npy".format(i), np.array(_))
    cprint('saving finished', "green")
    # %%
    db_path = expanduser("~/fair/streetlearn/data/pittsburgh_512")
    os.makedirs("figures", exist_ok=True)

    coords = []
    compressed_images = []
    with closing(plyvel.DB(db_path, create_if_missing=False)) as db:
        for k, v in tqdm(db):
            if k == b'panos_connectivity':
                pass
            else:
                pano = street.Pano()
                pano.ParseFromString(v)
                coords.append(dict(lat=pano.coords.lat, lng=pano.coords.lng))
                compressed_images.append(pano.compressed_image)
                del pano
    # %%
    os.makedirs("../processed-data/pittsburgh/view_512", exist_ok=True)
    np.save("../processed-data/pittsburgh/coords.npy", np.array(coords))
    for i, _ in enumerate(tqdm(chunk(compressed_images, chunk_size=2000))):
        np.save("../processed-data/pittsburgh/view_512/chunk_{:04d}.npy".format(i), np.array(_))
    cprint('saving finished', "green")
