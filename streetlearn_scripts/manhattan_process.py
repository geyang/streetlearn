# %%
# % load_ext autoreload
# % autoreload 2
from params_proto import cli_parse, Proto
from tqdm import trange


@cli_parse
class StreetLearnArgs:
    seed = Proto(1, help="random seed for numpy, 1 shows have good connectivity.")
    traj_coverage = Proto(4, help="the coverage rate for the trajectories, 4 is good")
    H = 10
    r = 2.5e-4
    T = 1


if __name__ == "__main__":
    # %%
    import numpy as np
    import matplotlib.pyplot as plt
    from os.path import expanduser
    from streetlearn import StreetLearnDataset, inside
    # %%
    import os

    os.chdir(expanduser('~/fair/streetlearn/streetlearn_scripts'))


    def make_xl():
        dataset = StreetLearnDataset(path="../processed-data/manhattan")
        prefix = "../processed-data/manhattan-xl"
        dataset.show_full_map(prefix + '/figures/full.png')
        dataset.select_bbox(-73.997, 40.726, 0.02, 0.016)
        dataset.show_bbox(prefix + '/figures/bounding_box.png', show=True)
        dataset.show_blowout("NYC-XL", prefix + '/figures/blow_out.png', show=True, frame_box=(3, 3.35))
        dataset.save_dataset(path=prefix)


    def make_large():
        dataset = StreetLearnDataset(path="../processed-data/manhattan")
        prefix = "../processed-data/manhattan-large"
        dataset.show_full_map(prefix + '/figures/full.png')
        dataset.select_bbox(-73.997, 40.726, 0.01, 0.008)
        dataset.show_bbox(prefix + '/figures/bounding_box.png', show=True)
        dataset.show_blowout("NYC-large", prefix + '/figures/blow_out.png', show=True)
        dataset.save_dataset(path=prefix)


    def make_medium():
        dataset = StreetLearnDataset(path="../processed-data/manhattan")
        prefix = "../processed-data/manhattan-medium"
        dataset.show_full_map(prefix + '/figures/full.png')
        dataset.select_bbox(-73.998, 40.7269, 0.00651, 0.00475)
        dataset.show_bbox(prefix + '/figures/bounding_box.png', show=True)
        dataset.show_blowout("NYC-medium", prefix + '/figures/blow_out.png', show=True)
        dataset.save_dataset(path=prefix)


    def make_small():
        dataset = StreetLearnDataset(path="../processed-data/manhattan")
        prefix = "../processed-data/manhattan-small"
        dataset.show_full_map(prefix + '/figures/full.png')
        dataset.select_bbox(-73.9966, 40.7282, 0.0042, 0.0035)
        dataset.show_bbox(prefix + '/figures/bounding_box.png', show=True)

        x = 0.003
        y = 0.0035 * 0.15
        remove_1 = (-73.9966 + x, 40.7282, 0.0042 - x, y)
        remove_2 = (-73.9966 + x, 40.7282 + 0.0035 - y, 0.0042 - x, y)

        dataset.select_bbox(-73.9966, 40.7282, 0.0042, 0.0035, exclude=[remove_1, remove_2])

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


    def visualize_trajectories(prefix):
        np.random.seed(StreetLearnArgs.seed)

        dataset = StreetLearnDataset(path=prefix)
        dataset.select_all()

        fig = plt.figure(figsize=(3, 3), dpi=300)
        ax = fig.add_axes([0.025, 0, 0.975, 0.95])
        ax.set_axis_off()

        dataset.show_blowout(f"NYC-{prefix.split('-')[-1]}", fig=fig, frame_box=(3, 3.35), box_alpha=0.0,
                             s=0.25, color="white", show=False, set_lim=False)

        trajs = [τ
                 for _ in range(StreetLearnArgs.traj_coverage)
                 for τ in dataset.traj_gen(H=StreetLearnArgs.H, r=StreetLearnArgs.r, T=StreetLearnArgs.T)
                 if τ is not None]

        from matplotlib import cm
        cmap = cm.get_cmap('viridis')

        # fig = plt.figure(figsize=(3, 3), dpi=300)
        for i, traj in enumerate(trajs):
            poses = dataset.lng_lat[traj]
            plt.plot(*poses.T, color="#23aaff", lw=2.5, zorder=-1, alpha=(0.3 + i / len(trajs)) / 1.3 * 0.4)

        plt.gcf().set_size_inches(2, 2.15)
        plt.savefig(prefix + "/figures/trajectories.png", )
        plt.show()

        np.save(prefix + "/trajs.npy", trajs)
        print('saved')

        from ml_logger import logger
        with logger.PrefixContext(prefix):
            logger.log_text(f"""
                seed: {StreetLearnArgs.seed}
                coverage: {StreetLearnArgs.traj_coverage}
                prefix: {prefix} 
                size: {len(dataset.lng)}
                bbox: {dataset.bbox}
                """, "summary.md", dedent=True, overwrite=True)


    def show_street_view():
        prefix = "../processed-data/manhattan-xl"
        dataset = StreetLearnDataset(path=prefix, view_mode='omni-gray', view_size=(64, 64))
        from ml_logger import logger
        logger.configure(prefix=prefix, register_experiment=False)
        for traj_ind in trange(10):
            frame_stack = []
            for ind in dataset.trajs[traj_ind]:
                img = dataset.street_view(ind, None, "omni-rgb")
                frame_stack.append(img)
            size = img.shape[1]
            logger.log_video(frame_stack, f"videos/size_{size}/manhattan-xl_{traj_ind:04d}.mp4", fps=5)
            logger.log_video(frame_stack, f"videos/size_{size}/manhattan-xl_{traj_ind:04d}.gif", fps=5)
        print('done')


    # make_xl()
    # make_large()
    # make_medium()
    make_small()
    # make_tiny()

    for prefix in [
        #     "../processed-data/manhattan-xl",
        #     "../processed-data/manhattan-large",
        #     "../processed-data/manhattan-medium",
        "../processed-data/manhattan-small",
        #     "../processed-data/manhattan-tiny"
    ]:
        visualize_trajectories(prefix)

    show_street_view()
