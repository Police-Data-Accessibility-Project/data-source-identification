# ML URL Classifier

## Getting Started
1. Clone this repository
    ```bash
    git clone https://github.com/Police-Data-Accessibility-Project/data-source-identification.git pdap-data-source-identification
    cd pdap-data-source-identification/ml-url-classifier
    ```
2. Add an annotated dataset JSON file to the `data/` directory
    (see the ## Load Data section of this notebook for the expected JSON file structure)
3. Install [Anaconda](https://docs.anaconda.com/anaconda/install/index.html)
4. Create a conda environment
    ```bash
    conda env create -n PDAP -f environment.yml
    ```
5. Activate the environment (if not already active)
    ```bash
    conda env activate -n PDAP
    ```
6. Run this Jupyter notebook
    ```
    ctrl + shift + alt + Enter
    ```