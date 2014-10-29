#!/usr/bin/python

'''
This program fetches datasets from the R package 'AppliedPredictiveModeling'
from CRAN and converts .RData files to .csv files.
'''

import os
from urllib import urlopen
import tarfile
import shutil
import pandas as pd
import rpy2.robjects as robjects
import pandas.rpy.common as com

APM_URL = ('http://cran.r-project.org/src/contrib/'
            'AppliedPredictiveModeling_1.1-6.tar.gz')
APM_ARCHIVE = 'AppliedPredictiveModeling_1.1-6.tar.gz'
APM_NAME = 'AppliedPredictiveModeling'

def mkdir_dataset():
    '''create the directory "datasets" under main directory'''
    here = os.path.dirname(__file__)
    datasets_folder = os.path.abspath(os.path.join(here, 'datasets'))

    if not os.path.exists(datasets_folder):
        print "Creating datasets folder: " + datasets_folder
        os.makedirs(datasets_folder)
    else:
        print "Using existing datasets folder:" + datasets_folder

    return datasets_folder

def download_pack(datasets_folder):
    '''download R package from CRAN'''
    print "Downloading AppliedPredictiveModeling from %s (2 MB)" % APM_URL

    archive_path = os.path.join(datasets_folder, APM_ARCHIVE)
    file_path = os.path.join(datasets_folder, APM_NAME)

    opener = urlopen(APM_URL)
    open(archive_path, 'wb').write(opener.read())

    print "Decomposing %s" % archive_path

    tarfile.open(archive_path, "r:gz").extractall(path=datasets_folder)

    print "Checking that the AppliedPredictiveModeling file exists..."
    assert os.path.exists(file_path)
    print "=> Success!"

    os.remove(archive_path)

def get_datafiles(datasets_folder):
    '''extract data files from the downloaded package'''
    print "Extract .RData files from the package..."

    src_path = os.path.join(datasets_folder, APM_NAME, 'data/.')
    dst_path = os.path.join(datasets_folder, '.')

    for root, dirs, files in os.walk(src_path):
        for name in files:
            file_path = os.path.join(root, name)
            shutil.move(file_path, dst_path)

    shutil.rmtree(os.path.join(datasets_folder, APM_NAME))

def convert_datafiles(datasets_folder):
    '''convert .RData files to .csv files and clean up'''
    print "Convert .RData to .csv and clean up .RData files..."

    for root, dirs, files in os.walk(datasets_folder):
        for name in files:
            # sort out .RData files
            if name.endswith('.RData'):
                name_ = os.path.splitext(name)[0]
                name_path = os.path.join(datasets_folder, name_)
                # creat sub-directory
                if not os.path.exists(name_path):
                    os.makedirs(name_path)
                file_path = os.path.join(root, name)
                robj = robjects.r.load(file_path)
                # check out subfiles in the data frame
                for var in robj:
                    myRData = com.load_data(var)
                    # convert to DataFrame
                    if not isinstance(myRData, pd.DataFrame):
                        myRData = pd.DataFrame(myRData)
                    var_path = os.path.join(datasets_folder,name_,var+'.csv')
                    myRData.to_csv(var_path)
                os.remove(os.path.join(datasets_folder, name)) # clean up

    print "=> Success!"

if __name__ == "__main__":
    datasets_folder = mkdir_dataset()
    download_pack(datasets_folder)
    get_datafiles(datasets_folder)
    convert_datafiles(datasets_folder)
