from setuptools import setup, find_packages

setup(name='streetlearn',
      packages=find_packages(),
      install_requires=[
          "jupyter",
          "matplotlib",
          "ml-logger",
          "numpy",
          "opencv-python",
          "pandas",
          "pillow",
          "plyvel",
          "seaborn",
          "tqdm"
      ],
      description='opensource-streetlearn-battery-included',
      author='Ge Yang<yangge1987@gmail.com>',
      url='https://github.com/episodeyang/streetlearn',
      author_email='yangge1987@gmail.com',
      version='0.0.0')
