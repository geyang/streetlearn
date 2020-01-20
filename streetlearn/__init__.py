import os
from glob import glob
from os.path import dirname, expanduser

import cv2
import numpy as np
from numpy.core._multiarray_umath import ndarray
from termcolor import cprint
from tqdm import tqdm


def blob2image(image_blob, size, gray_scale=False):
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
    img = cv2.imdecode(img_array, 2 | 4)
    if gray_scale:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if size is not None:  # see: https://stackoverflow.com/a/48121983/1560241
        img = cv2.resize(img, dsize=tuple(size), interpolation=cv2.INTER_CUBIC)
    if gray_scale:
        return img
    return img[..., [2, 1, 0]]  # return RGB instead of GBR


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
    lng_lat: ndarray
    coords = None
    compressed_images = None

    # ratio for the unit in y, per matplotlib's convention
    lat_correction = 1 / 0.74

    def __init__(self, path, view_size=None, view_mode=None):
        """

        :param path:
        :param view_size:
        :param view_mode: OneOf[None, 'omni-gray', 'omni-rgb', 'dir-gray', 'dir-rgb', ]. Only `omni-gray` is supported.
        """
        chunks = glob(path + "/view_512/*")
        chunks.sort()

        self.coords = np.load(path + '/coords.npy', allow_pickle=True)
        from ml_logger import logger
        logger.print(chunks, color='green')
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

        if view_size or view_mode:
            self.config_view_mode(view_size, view_mode)

    def select_all(self):
        return self.select_bbox(*self.get_bbox())

    def select_bbox(self, x0, y0, w, h, exclude=None):
        self.bbox = x0, y0, w, h
        inside_mask = np.array([inside(_, x0, y0, w, h) for _ in self.lng_lat])

        if exclude:
            for exclude_bbox in exclude:
                inside_mask = inside_mask > np.array([inside(_, *exclude_bbox) for _ in self.lng_lat])

        self.inside_inds = np.arange(len(self.coords))[inside_mask]
        self.inside_coords = self.coords[self.inside_inds]
        return self

    def get_bbox(self):
        min = self.lng_lat.min(axis=0)
        max = self.lng_lat.max(axis=0)
        return [*min, *(max - min)]

    def config_view_mode(self, size, mode):
        self.view_size = size
        self.view_mode = mode
        self._images = None

    _images = None

    @property
    def images(self):
        if self._images is None:
            self._images = np.array([
                self.street_view(ind, self.view_size, self.view_mode)
                for ind in tqdm(self.inside_inds, desc="decompress images...")])
        return self._images

    def save_dataset(self, path):
        os.makedirs(path + "/view_512", exist_ok=True)
        np.save(path + "/coords.npy", self.inside_coords)
        for i, _ in enumerate(tqdm(chunk(self.compressed_images[self.inside_inds], chunk_size=2000))):
            np.save(path + "/view_512/chunk_{:04d}.npy".format(i), np.array(_))
        print('data is now saved at', end='')
        cprint(path, "green")

    def show_full_map(self, file, show=None):
        import matplotlib.pyplot as plt

        frame_box = np.array([60, 3 * 23.75])
        fig = plt.figure(figsize=frame_box * (self.lng_lat.max(axis=0) - self.lng_lat.min(axis=0)), dpi=300)
        plt.scatter(self.lng, self.lat, s=0.5, facecolor="gray", lw=0)
        plt.title('Manhattan')
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['top'].set_visible(False)
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.gca().set_aspect(self.lat_correction)
        plt.tight_layout()
        if file is not None:
            os.makedirs(dirname(file), exist_ok=True)
            plt.savefig(file, bbox_inches="tight")
        if show is not False:
            fig.show()

    def show_bbox(self, file=None, show=None):
        import matplotlib.pyplot as plt
        from matplotlib import patches

        frame_box = np.array([60, 3 * 23.75])
        fig = plt.figure(figsize=frame_box * (self.lng_lat.max(axis=0) - self.lng_lat.min(axis=0)), dpi=300)
        # fig = plt.figure(figsize=np.array(frame_box) * self.bbox[2:] / self.bbox[2], dpi=300)
        plt.scatter(self.lng, self.lat, s=0.5, facecolor="gray", lw=0)
        plt.scatter(*self.lng_lat[self.inside_inds].T, s=1, facecolor="#23aaff", lw=0)
        rect = patches.Rectangle(self.bbox[:2], *self.bbox[2:], linewidth=4, edgecolor='r', facecolor="none", alpha=0.7)
        plt.gca().add_patch(rect)
        plt.title('Greenwich Village (Small)')
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['top'].set_visible(False)
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.gca().set_aspect(self.lat_correction)
        plt.tight_layout()
        if file is not None:
            os.makedirs(dirname(file), exist_ok=True)
            plt.savefig(file, bbox_inches="tight")
        if show is not False:
            fig.show()

    def show_blowout(self, title="", file=None, fig=None, frame_box=(3, 3.75), s=2,
                     color="#23aaff", box_color='red', box_alpha=0.7,
                     show=None, set_lim=True):
        import matplotlib.pyplot as plt
        from matplotlib import patches

        fig = fig or plt.figure(figsize=np.array(frame_box) * self.bbox[2:] / self.bbox[2], dpi=300)

        plt.scatter(self.lng, self.lat, s=0.5, facecolor="gray", lw=0)
        plt.scatter(*self.lng_lat[self.inside_inds].T, s=s, facecolor=color, edgecolors=(1, 1, 1, 0.7), lw=0.5,
                    zorder=2)
        rect = patches.Rectangle(self.bbox[:2], *self.bbox[2:], linewidth=4, edgecolor=box_color, facecolor="none",
                                 alpha=box_alpha)
        plt.gca().add_patch(rect)
        plt.title(title, fontsize=7, pad=-0.15)
        if set_lim:
            plt.xlim(self.bbox[0] - 0.003, self.bbox[0] + self.bbox[2] + 0.003)
            plt.ylim(self.bbox[1] - 0.001, self.bbox[1] + self.bbox[3] + 0.001)

        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['top'].set_visible(False)
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.gca().set_aspect(self.lat_correction)
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

    def locate(self, lng, lat, r=1.6e-4):
        magic = [1, self.lat_correction]
        ds = np.linalg.norm((self.lng_lat - [lng, lat]) * magic, ord=2, axis=-1)
        return np.arange(len(ds), dtype=int)[ds < r]

    def locate_closest(self, lng, lat):
        magic = [1, self.lat_correction]
        ds = np.linalg.norm((self.lng_lat - [lng, lat]) * magic, ord=2, axis=-1)
        ind = np.argmin(ds)
        return ind, ds[ind]

    pairwise_ds = None

    def neighbor(self, inds, r=1.6e-4, ord=1, mask=None):
        """ todo: refactor indices to be first.

        :param inds:
        :param r:
        :param ord:
        :param mask:
        :return: [self.lng_lat[_] for _ in ns_inds], ds, ns_inds
        """
        l = len(self.lng_lat)
        if self.pairwise_ds is None:
            cprint('computing pairwise distance matrix [{0} x {0}]'.format(l), 'yellow')
            magic = [1, self.lat_correction]
            self.pairwise_ds = np.linalg.norm(
                (self.lng_lat[None, :, :] - self.lng_lat[:, None, :]) * magic,
                ord=ord, axis=-1)
            cprint('✓done', 'green')
            self.pairwise_ds[np.eye(l, dtype=bool)] = float('inf')
        mask = np.ones(l, dtype=bool) if mask is None else mask
        ns_inds = [self.inds[np.logical_and(mask, self.pairwise_ds[ind] < r)] for ind in inds]
        ds = [ds[_] for ds, _ in zip(self.pairwise_ds[inds], ns_inds)]
        return [self.lng_lat[_] for _ in ns_inds], ds, ns_inds

    def street_view(self, index, size, mode: str):
        """
        returns decompressed 8-bit RGB data or Gray-scale. This is used to
        generate the cached images, which is then post-processed on the fly
        to float32 by the dataset class.

        We cache the files in 8-bit RGB (or gray-scale) because it is much
        smaller.

        :param index:
        :param size:
        :param mode: OneOf[None, 'omni-gray', 'omni-rgb', 'dir-gray',
            'dir-rgb', ]. Only `omni-*` are supported.
        :return:
        """
        assert mode.startswith("omni"), "only `omni-*` modes are supported."
        is_grayscale = mode.endswith('gray')
        return blob2image(self.compressed_images[index], size, is_grayscale)

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
        :param no_orphans: avoid having orphans in the dataset
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
