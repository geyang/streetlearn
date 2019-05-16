# %%
# % load_ext autoreload
# % autoreload 2
from params_proto import cli_parse, Proto
from tqdm import tqdm, trange


@cli_parse
class StreetLearnArgs:
    seed = Proto(0, help="random seed for numpy")


if __name__ == "__main__":
    # %%
    import numpy as np
    from PIL import Image
    import cv2
    import matplotlib.pyplot as plt
    from os.path import expanduser
    from glob import glob
    import pandas as pd
    from streetlearn import inside, StreetLearnDataset
    # %%
    import os

    os.chdir(expanduser('~/fair/streetlearn/streetlearn_scripts'))


    def full_trajectories(create_trajectories=False):
        """

        :param create_trajectories: Takes a long time to create the trajectories.
        :return:
        """
        dataset = StreetLearnDataset(path="../processed-data/manhattan")
        prefix = "../processed-data/manhattan"

        if create_trajectories:
            dataset.select_all()

            fig = plt.figure(figsize=(3, 3), dpi=300)
            ax = fig.add_axes([0.025, 0, 0.975, 0.95])
            ax.set_axis_off()

            trajs = [_ for _ in tqdm(dataset.traj_gen(H=10, r=1.9e-4, T=0.1), desc="traj_gen") if _ is not None]

            np.save(prefix + "/trajs.npy", trajs)
        else:
            trajs = dataset.trajs

        import matplotlib.pyplot as plt
        fig = plt.figure(figsize=(5, 7.2), dpi=300)
        for i, traj in enumerate(tqdm(trajs, desc="plotting trajectores")):
            poses = dataset.lng_lat[traj]
            # plt.plot(*poses.T, color="#23aaff", lw=2.5, zorder=-1, alpha=(0.3 + i / len(trajs)) / 1.3)
            plt.plot(*poses.T, color="#23aaff" if i % 2 == 0 else "red", lw=2.5, zorder=-1,
                     alpha=(0.3 + i / len(trajs)) / (1.3 if i % 2 == 0 else 5))

        plt.title('NYC Trajectories')
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['top'].set_visible(False)
        os.makedirs(prefix + "/figures", exist_ok=True)
        plt.savefig(prefix + "/figures/trajectories.png")
        plt.show()
        print('done')


    def make_medium():
        dataset = StreetLearnDataset(path="../processed-data/manhattan")
        prefix = "../processed-data/manhattan-medium"
        dataset.show_full_map(prefix + '/figures/full.png')
        dataset.select_bbox(-73.997, 40.726, 0.02, 0.016)
        dataset.show_bbox(prefix + '/figures/bounding_box.png', show=True)
        dataset.show_blowout("NYC-medium", prefix + '/figures/blow_out.png', show=True, frame_box=(3, 3.35))
        dataset.save_dataset(path=prefix)


    def make_small():
        dataset = StreetLearnDataset(path="../processed-data/manhattan")
        prefix = "../processed-data/manhattan-small"
        dataset.show_full_map(prefix + '/figures/full.png')
        dataset.select_bbox(-73.997, 40.726, 0.01, 0.008)
        dataset.show_bbox(prefix + '/figures/bounding_box.png', show=True)
        dataset.show_blowout("NYC-small", prefix + '/figures/blow_out.png', show=True)
        dataset.save_dataset(path=prefix)


    def make_tiny():
        dataset = StreetLearnDataset(path="../processed-data/manhattan")
        prefix = "../processed-data/manhattan-tiny"
        # dataset.show_full_map(prefix + '/figures/full.png')
        dataset.select_bbox(-73.997, 40.7289, 0.002, 0.0015)
        dataset.show_bbox(prefix + '/figures/bounding_box.png', show=True)
        dataset.show_blowout("NYC-tiny", prefix + '/figures/blow_out.png', frame_box=(3, 2.6),
                             show=True)
        dataset.save_dataset(path=prefix)


    def tiny_trajectories():
        np.random.seed(StreetLearnArgs.seed)

        prefix = "../processed-data/manhattan-tiny"
        dataset = StreetLearnDataset(path=prefix)
        dataset.select_bbox(-73.997, 40.7289, 0.002, 0.0015)

        fig = plt.figure(figsize=(3, 3), dpi=300)
        ax = fig.add_axes([0.05, 0, 0.90, 0.85])
        ax.set_axis_off()

        dataset.show_blowout("NYC-tiny", fig=fig, frame_box=(3, 2.6), box_alpha=0.05,
                             s=0.5, color="white", show=False, set_lim=False)

        trajs = [_ for _ in dataset.traj_gen(H=10, r=1.6e-4, T=0.1) if _ is not None]

        from matplotlib import cm
        cmap = cm.get_cmap('viridis')

        # fig = plt.figure(figsize=(3, 3), dpi=300)
        for i, traj in enumerate(trajs):
            print(traj)
            poses = dataset.lng_lat[traj]
            # plt.plot(*poses.T, color=cmap(i / len(trajs)), lw=2.5, zorder=-1)
            plt.plot(*poses.T, color="#23aaff", lw=2.5, zorder=-1, alpha=(0.7 + i / len(trajs)) / 1.7)

        plt.gcf().set_size_inches(1, 1.1)
        # plt.xlim(dataset.lng.min(), dataset.lng.max())
        # plt.ylim(dataset.lat.min(), dataset.lat.max())
        plt.savefig(prefix + "/figures/trajectories.png")
        plt.show()

        np.save(prefix + "/trajs.npy", trajs)
        print('done')


    def small_trajectories():
        np.random.seed(StreetLearnArgs.seed)

        prefix = "../processed-data/manhattan-small"
        dataset = StreetLearnDataset(path=prefix)
        dataset.select_bbox(-73.997, 40.726, 0.01, 0.008)

        fig = plt.figure(figsize=(3, 3), dpi=300)
        ax = fig.add_axes([0.025, 0, 0.975, 0.95])
        ax.set_axis_off()

        dataset.show_blowout("NYC-small", fig=fig, frame_box=(3, 2.6), box_alpha=0.0,
                             s=0.25, color="white", show=False, set_lim=False)

        trajs = [_ for _ in dataset.traj_gen(H=10, r=1.9e-4, T=0.1) if _ is not None]

        from matplotlib import cm
        cmap = cm.get_cmap('viridis')

        # fig = plt.figure(figsize=(3, 3), dpi=300)
        for i, traj in enumerate(trajs):
            print(traj)
            poses = dataset.lng_lat[traj]
            plt.plot(*poses.T, color="#23aaff", lw=2.5, zorder=-1, alpha=(0.3 + i / len(trajs)) / 1.3)

        plt.gcf().set_size_inches(1.5, 1.6)
        plt.savefig(prefix + "/figures/trajectories.png")
        plt.show()

        np.save(prefix + "/trajs.npy", trajs)
        print('done')


    def medium_trajectories():
        np.random.seed(StreetLearnArgs.seed)

        prefix = "../processed-data/manhattan-medium"
        dataset = StreetLearnDataset(path=prefix)
        dataset.select_bbox(-73.997, 40.726, 0.02, 0.016)

        fig = plt.figure(figsize=(3, 3), dpi=300)
        ax = fig.add_axes([0.025, 0, 0.975, 0.95])
        ax.set_axis_off()

        dataset.show_blowout("NYC-medium", fig=fig, frame_box=(3, 3.35), box_alpha=0.0,
                             s=0.25, color="white", show=False, set_lim=False)

        trajs = [_ for _ in dataset.traj_gen(H=10, r=1.9e-4, T=0.1) if _ is not None]

        from matplotlib import cm
        cmap = cm.get_cmap('viridis')

        # fig = plt.figure(figsize=(3, 3), dpi=300)
        for i, traj in enumerate(trajs):
            print(traj)
            poses = dataset.lng_lat[traj]
            plt.plot(*poses.T, color="#23aaff", lw=2.5, zorder=-1, alpha=(0.3 + i / len(trajs)) / 1.3)

        plt.gcf().set_size_inches(2, 2.15)
        plt.savefig(prefix + "/figures/trajectories.png", )
        plt.show()

        np.save(prefix + "/trajs.npy", trajs)
        print('done')


    def show_small_street_view():
        prefix = "../processed-data/manhattan-medium"
        dataset = StreetLearnDataset(path=prefix, view_mode='omni-gray', view_size=(64, 64))
        from ml_logger import logger
        logger.configure(prefix=prefix, register_experiment=False)
        for traj_ind in trange(10):
            frame_stack = []
            for ind in dataset.trajs[traj_ind]:
                img = dataset.street_view(ind, None, "omni-rgb")
                frame_stack.append(img)
            size = img.shape[1]
            logger.log_video(frame_stack, f"videos/size_{size}/manhattan-medium_{traj_ind:04d}.mp4", fps=5)
            logger.log_video(frame_stack, f"videos/size_{size}/manhattan-medium_{traj_ind:04d}.gif", fps=5)
        print('done')


    # full_trajectories()
    # make_medium()
    # make_small()
    # make_tiny()
    # medium_trajectories()
    # small_trajectories()
    # tiny_trajectories()
    show_small_street_view()
