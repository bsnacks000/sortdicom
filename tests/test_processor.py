""" test the processor module
"""

import unittest 
from unittest import mock
import pydicom 
import os 
import shutil
from pprint import pprint 
from . import DATA_DIR
import sortdicom.processor as processor

#_get_all_dicom_filepaths, 
# _copy_dicom_file, 
# _build_dicom_unique_identifier, 
# sortdicom


class TestProcessor(unittest.TestCase):

    def setUp(self): 
        self.patientA_filepath = os.path.join(DATA_DIR, 'patientA')
        self.patientB_filepath = os.path.join(DATA_DIR, 'patientB')
        self.output_dir = os.path.join(DATA_DIR, 'output')  
    
    def test_get_all_dicom_filepaths(self):

        # given a patient root return all dicom filepaths
        fpaths = processor._get_all_dicom_filepaths(self.patientA_filepath) 
        self.assertEqual(len(fpaths), 8)

        fpaths = processor._get_all_dicom_filepaths(self.patientB_filepath) 
        self.assertEqual(len(fpaths), 8)

        for f in fpaths: # test filter
            self.assertNotIn('dummyfile.csv', f)
    
    def test_copy_dicom_file(self):
        og_path = os.path.join(self.patientA_filepath, '4947-DIG DIAG MAMMOGR-94476', '000000.dcm') 
        processor._copy_dicom_file(og_path, 'newfile.dcm', self.output_dir) 
        
        self.assertIn('newfile.dcm', os.listdir(self.output_dir))

    def test_build_dicom_unique_identifier_returns_correct_mapping(self): 
        
        dicomfilepath = os.path.join(
            DATA_DIR, 'patientA', '4947-DIG DIAG MAMMOGR-94476', '000000.dcm')

        uid = processor._build_dicom_unique_identifier(dicomfilepath)
        self.assertEqual(uid,'TCGA-AO-A0JB_L_MLO_20010607_DIG-DIAG-MAMMOGR_MG_3.dcm')