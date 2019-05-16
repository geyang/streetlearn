import os
from glob import glob
from termcolor import cprint
from os.path import expanduser, dirname
from tqdm import tqdm
import numpy as np

# %%
import cv2


def blob2image(image_blob):
    """
    https://codeyarns.com/2015/01/23/how-to-specify-opencv-color-type-in-python/

    In openCV, the image read pipeline seems to be defined by flags

    .. code:: c

        enum {
            /* 8bit, color or not */
            CV_LOAD_IMAGE_UNCHANGED  =-1,
            /* 8bit, gray */
            CV_LOAD_IMAGE_GRAYSCALE  =0,
            /* ?, color */
            CV_LOAD_IMAGE_COLOR      =1,
            /* any depth, ? */
            CV_LOAD_IMAGE_ANYDEPTH   =2,
            /* ?, any color */
            CV_LOAD_IMAGE_ANYCOLOR   =4
        };

    :param image_blob:
    :return: Size(H, W, C) (208, 416, 3)
    """
    img_array = np.frombuffer(image_blob, np.uint8)
    return cv2.imdecode(img_array, 2 | 4)


def inside(coord, x0, y0, w, h):
    x, y = coord
    return x0 <= x <= x0 + w and y0 <= y <= y0 + h


# %% test fn<inside>
assert inside([0, 0], -0.5, -0.5, 1, 1)
assert not inside([0, 0], -0.5, -0.5, 1, 0.2)
assert not inside([0, 0], -0.5, -0.5, 0.2, 0.2)


def chunk(array, chunk_size=100):
    l = 0
    while l < len(array):
        yield array[l: l + chunk_size]
        l += chunk_size


class StreetLearnDataset:
    _images = None
    coords = None
    compressed_images = None

    def __init__(self, path, view_size=(64, 64)):
        chunks = glob(path + "/view_512/*")
        chunks.sort()

        self.coords = np.load(path + '/coords.npy', allow_pickle=True)
        self.compressed_images = np.concatenate(
            [np.load(p, allow_pickle=True) for p in tqdm(chunks, desc="reading...")])
        try:
            self.trajs = np.load(path + "/trajs.npy", allow_pickle=True)
        except FileNotFoundError:
            self.trajs = None
        if self.trajs is not None:
            cprint('trajectories is loaded!', 'green')

        self.lng_lat = np.array([[c['lng'], c['lat']] for c in self.coords])
        self.lng = self.lng_lat[:, 0]
        self.lat = self.lng_lat[:, 1]
        self.inds = np.arange(len(self.coords))
        # todo: select entire region on init.

    def select_bbox(self, x0, y0, w, h):
        self.bbox = x0, y0, w, h
        inside_mask = np.array([inside(_, x0, y0, w, h) for _ in self.lng_lat])
        self.inside_inds = np.arange(len(self.coords))[inside_mask]
        self.inside_coords = self.coords[self.inside_inds]
        return self

    @property
    def images(self):
        if not self._images:
            self._images = np.array(
                [self.street_view(ind) for ind in tqdm(self.inside_inds, desc="decompress images...")])
        return self._images

    def save_dataset(self, path):
        os.makedirs(path + "/view_512", exist_ok=True)
        np.save(path + "/coords.npy", self.inside_coords)
        for i, _ in enumerate(tqdm(chunk(self.compressed_images[self.inside_inds], chunk_size=2000))):
            np.save(path + "/view_512/chunk_{:04d}.npy".format(i), np.array(_))
        print('data is now saved at', end='')
        cprint(path, "green")

    def make_pair_dataset(self):
        return DataSet()

    def make_transition_pairs(self):
        return dict(x=None, goal=None, img=None, img_goal=None)

    def show_full_map(self, file, show=None):
        import matplotlib.pyplot as plt

        frame_box = np.array([60, 3 * 23.75])
        fig = plt.figure(figsize=frame_box * (self.lng_lat.max(axis=0) - self.lng_lat.min(axis=0)), dpi=300)
        plt.scatter(self.lng, self.lat, s=0.5, facecolor="gray", lw=0)
        plt.title('Manhattan')
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['top'].set_visible(False)
        plt.xlabel('Latitude')
        plt.ylabel('Longitude')
        if file is not None:
            os.makedirs(dirname(file), exist_ok=True)
            plt.savefig(file, bbox_inches="tight")
        if show is not False:
            fig.show()

    def show_bbox(self, file, show=None):
        import matplotlib.pyplot as plt
        from matplotlib import patches

        frame_box = np.array([60, 3 * 23.75])
        fig = plt.figure(figsize=frame_box * (self.lng_lat.max(axis=0) - self.lng_lat.min(axis=0)), dpi=300)
        plt.scatter(self.lng, self.lat, s=0.5, facecolor="gray", lw=0)
        plt.scatter(*self.lng_lat[self.inside_inds].T, s=1, facecolor="#23aaff", lw=0)
        rect = patches.Rectangle(self.bbox[:2], *self.bbox[2:], linewidth=4, edgecolor='r', facecolor="none", alpha=0.7)
        plt.gca().add_patch(rect)
        plt.title('Greenwich Village (Small)')
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['top'].set_visible(False)
        plt.xlabel('Latitude')
        plt.ylabel('Longitude')
        if file is not None:
            os.makedirs(dirname(file), exist_ok=True)
            plt.savefig(file, bbox_inches="tight")
        if show is not False:
            fig.show()

    def show_blowout(self, title="", file=None, fig=None, frame_box=(3, 3.75), s=2, color="#23aaff", box_alpha=0.7,
                     show=None, set_lim=True):
        import matplotlib.pyplot as plt
        from matplotlib import patches

        fig = fig or plt.figure(figsize=np.array(frame_box) * self.bbox[2:] / self.bbox[2], dpi=300)
        plt.scatter(self.lng, self.lat, s=0.5, facecolor="gray", lw=0)
        plt.scatter(*self.lng_lat[self.inside_inds].T, s=s, facecolor=color, edgecolors=(1, 1, 1, 0.7), lw=0.5,
                    zorder=2)
        rect = patches.Rectangle(self.bbox[:2], *self.bbox[2:], linewidth=4, edgecolor='r', facecolor="none",
                                 alpha=box_alpha)
        plt.gca().add_patch(rect)
        plt.title(title, fontsize=7, pad=-0.15)
        if set_lim:
            plt.xlim(self.bbox[0] - 0.003, self.bbox[0] + self.bbox[2] + 0.003)
            plt.ylim(self.bbox[1] - 0.001, self.bbox[1] + self.bbox[3] + 0.001)
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['top'].set_visible(False)
        plt.xlabel('Latitude')
        plt.ylabel('Longitude')
        if file is not None:
            os.makedirs(dirname(file), exist_ok=True)
            plt.savefig(file, bbox_inches="tight")
        if show is not False:
            fig.show()

    def sample(self, batch_n=None):
        """sample gps location and indices

        :param batch_n:
        :return: Pos(lng, lat), index
        """
        if batch_n is None:
            ind = np.random.rand()
            return self.lng_lat[ind], ind
        else:
            inds = np.random.rand()
            return self.lng_lat[inds], inds

    pairwise_ds = None

    def neighbor(self, inds, r=1.6e-4, ord=1, mask=None):
        l = len(self.lng_lat)
        if self.pairwise_ds is None:
            magic = [[[1, 0.75]]]  # projective correction
            self.pairwise_ds = np.linalg.norm(
                (self.lng_lat[None, :, :] - self.lng_lat[:, None, :]) * magic,
                ord=ord, axis=-1)
            self.pairwise_ds[np.eye(l, dtype=bool)] = float('inf')
        mask = np.ones(l, dtype=bool) if mask is None else mask
        ns_inds = [self.inds[np.logical_and(mask, self.pairwise_ds[ind] < r)] for ind in inds]
        ds = [ds[_] for ds, _ in zip(self.pairwise_ds[inds], ns_inds)]
        return [self.lng_lat[_] for _ in ns_inds], ds, ns_inds

    def street_view(self, index):
        return blob2image(self.compressed_images[index]) / 255

    def no_orphans(self, traj, r, T):
        """finds neighbor in the entire dataset for the orphan"""
        if len(traj) > 1:
            return traj

        orphan = traj[0]
        [ns], [ds], [ns_inds] = self.neighbor([orphan], r=r)
        if len(ns):
            p = np.exp(-ds) / T
            ind = np.random.choice(ns_inds, p=p / p.sum())
            return [orphan, ind]
        else:  # take the orphan out and mark with None
            return None

    def traj_gen(self, H=2, r=0.8e-4, T=1, no_orphans=True):
        """

        :param H: maximum horizon for the sampled trajectories.
        :param r: cut-off radius for the neighbor
        :param T: temperature for the Boltzmann distribution
        :return:
        """
        pool = {*self.inds}
        covered = np.ones(len(pool), dtype=bool)
        while len(pool):
            ind = np.random.choice([*pool])
            pool.remove(ind)
            covered[ind] = False
            traj = [ind]
            while True:
                [ns], [ds], [ns_inds] = self.neighbor([ind], r=r, mask=covered)
                if len(ns_inds):
                    # pick closest
                    p = np.exp(-ds) / T
                    ind = np.random.choice(ns_inds, p=p / p.sum())
                    pool.remove(ind)
                    covered[ind] = False
                    if len(traj) == H:
                        yield self.no_orphans(traj, r, T) if no_orphans else traj
                        traj = [ind]
                    else:
                        traj.append(ind)
                else:
                    yield self.no_orphans(traj, r, T) if no_orphans else traj
                    break


if __name__ == "__main__":
    # %%
    from contextlib import closing
    import plyvel
    from streetlearn.buff import streetlearn_pb2 as street
    from tqdm import tqdm

    # to protect from accidental runs
    exit()


    # %%
    def chunk(array, chunk_size=100):
        l = 0
        while l < len(array):
            yield array[l: l + chunk_size]
            l += chunk_size


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