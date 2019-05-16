# Reduced StreetLearn Datasets

The datasets here are saved in numpy, making them much more portable
than what was in the original DeepMind streetlearn dataset. 

The folder structure looks like below: 

```
├── README.md
├── manhattan
│   ├── coords.npy
│   ├── figures
│   ├── trajs.npy
│   └── view_512 # -----------------> chunks
├── manhattan-medium
│   ├── coords.npy
│   ├── figures
│   ├── trajs.npy
│   └── view_512 # -----------------> chunks
├── manhattan-small
│   ├── coords.npy
│   ├── figures
│   ├── trajs.npy
│   └── view_512 # -----------------> chunks
├── manhattan-tiny
│   ├── coords.npy
│   ├── figures
│   ├── trajs.npy
│   └── view_512 # -----------------> chunks
└── pittsburgh
    ├── coords.npy
    └── view_512
```

The `trajs.npy` file contains trajectories sampled from that 
dataset.


