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

## Processed-Dataset Details:

```yaml
prefix: ../processed-data/manhattan-tiny 
seed: 1
coverage: 4
size: 53
bbox: (-73.99694545618935, 40.728918740015985, 0.0019080027486779727, 0.0014344303765838617)
```

```yaml
prefix: ../processed-data/manhattan-small 
seed: 1
coverage: 4
size: 255
bbox: (-73.99698090623339, 40.72730617544701, 0.003970809291459432, 0.0034904597927223335)
```

```yaml
prefix: ../processed-data/manhattan-medium 
seed: 1
coverage: 4
size: 501
bbox: (-73.99797906458758, 40.72690367880115, 0.006481507781984419, 0.004746123629082888)
```

```yaml
prefix: ../processed-data/manhattan-large 
seed: 1
coverage: 4
size: 1495
bbox: (-73.99699947982805, 40.726008639817245, 0.00999942365351103, 0.007986187313427706)
```

```yaml
prefix: ../processed-data/manhattan-xl 
seed: 1
coverage: 4
size: 5355
bbox: (-73.99699947982805, 40.72600072316067, 0.019993416963771438, 0.015995486385776303)
```
