# NIPS-Data-Wrangling
Wrangling data from various sources to make a coagulated DataSet of NIPS Research Papers
# NIPS Reasearch Papers Downloader

This python program can be used to automatically download (tested as on Dec 17, 2022) research papers published in NIPS (https://proceedings.neurips.cc/) between YEAR_MIN and YEAR_MAX. The code will also create a dataset containing ***Author, Year, Paper title, Abstract, Paper Text*** for each research paper which can be used for data analyses. 

#### UPDATE :  Implemented multiprocessing to speed up the process (from 3+ hrs to <15 mins )

## Usage

Step 1 : Clone repository - run the below code from command line

``` 
git clone https://github.com/snehamishra4321/NIPS-Data-Wrangling.git
```

Step 2 : Install requirements

```
pip install -r requirements.txt
```

Step 3 : Modify download_nips_dataset.py

Following attributes can be updated as per requirement.
* DOWNLOAD_PAPERS - change to ***True*** to download all research papers locally
* YEAR_MIN - Start year from which papers need to be downloaded (min 1988)
* YEAR_MIN - End year from which papers need to be downloaded (max 2021)

Step 4 : Run the program

```
python3 download_nips_dataset.py
```

## Contact

Please reach me out at sneha.mishra4321@gmail.com for any queries / collaborations.
