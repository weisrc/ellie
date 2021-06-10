# Ellie
 Little search engine made with Tensorflow.

 The online hosted version will hopefully be available [here](https://ellie.weis.studio). Nope, not anymore sadly ;(

## Getting started

Clone this repo, download and extract the machine learning models and run!

```sh
git clone [repo_url]
conda activate
cd [repo]/src
# install the models
mkdir src/data
python app.py
# the app should start on port 8080
```

## Requirements

- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) (optional) 
- Python 3 (comes with Miniconda)
- [Universal Sentence Encoder Multilingual](https://tfhub.dev/google/universal-sentence-encoder-multilingual/3) (tensorflow model)
- [Fastext model](https://fasttext.cc/)
- A linux machine (WSL works too!)
More in `src/requirements`

Your file tree should look like...
```sh
src/models
├── fasttext.ftz # fastext model
└── use # universal sentence encoder model
    ├── assets
    ├── saved_model.pb
    └── variables
        ├── variables.data-00000-of-00001
        └── variables.index
```
