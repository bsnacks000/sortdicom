""" test the processor module
"""

import unittest 
from unittest import mock
import pydicom 
import os 
import shutil
from pprint import pprint 
from . import DATA_DIR
from collections import OrderedDict
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
        os.remove(os.path.join(self.output_dir, 'newfile.dcm'))

    def test_build_dicom_unique_identifier_returns_correct_mapping(self): 
        
        dicomfilepath = os.path.join(
            DATA_DIR, 'patientA', '4947-DIG DIAG MAMMOGR-94476', '000000.dcm')

        uid = processor._build_dicom_unique_identifier(dicomfilepath)
        self.assertEqual(uid,'TCGA-AO-A0JB_L_MLO_20010607.dcm')


    def test_duplicate_labels(self): 
        input_val = OrderedDict([
            ('key0', 'value0.dcm'),
            ('key1', 'value1.dcm'), 
            ('key2', 'value1.dcm'), 
            ('key3', 'value2.dcm'),
            ('key4', 'value2.dcm'),
            ('key5', 'value2.dcm'),
            ('key6', 'value3.dcm'),
            ('key7', 'value3.dcm'),
            ('key8', 'value4.dcm'), 
            ('key9', 'value5.dcm'), 
            ('key91', 'value5.dcm'), 
            
            ]) 
        result = processor._label_duplicates(input_val)
        expected = {'key0': 'value0_1.dcm',
            'key1': 'value1_1.dcm',
            'key2': 'value1_2.dcm',
            'key3': 'value2_1.dcm',
            'key4': 'value2_2.dcm',
            'key5': 'value2_3.dcm',
            'key6': 'value3_1.dcm',
            'key7': 'value3_2.dcm',
            'key8': 'value4_1.dcm',
            'key9': 'value5_1.dcm',
            'key91': 'value5_2.dcm'}
        self.assertDictEqual(dict(result), expected)

    @mock.patch('sortdicom.handler.DicomFileHandler.load', return_value='')
    @mock.patch('sortdicom.handler.DicomFileHandler.get_dicom_header_tag', return_value='')
    def test_build_dicom_unique_identifier_raises_BlankDicomHeaderError_if_no_header(self, mock_get_header_tag, mock_load): 

        with self.assertRaises(processor.BlankDicomHeaderError):
            uid = processor._build_dicom_unique_identifier()


    @mock.patch('sortdicom.handler.DicomFileHandler.load', side_effect=pydicom.errors.InvalidDicomError)
    def test_sortdicom_raise_on_read_allows_dicom_error(self, mock_handler):

        with self.assertRaises(pydicom.errors.InvalidDicomError): 
            result = processor.sortdicom(self.patientA_filepath)



    def test_sortdicom_works_on_single_patient_folder_without_copy(self): 
        #pass
        result = processor.sortdicom(self.patientA_filepath)
        expected = ['TCGA-AO-A0JB_L_CC_20010607_1.dcm',
            'TCGA-AO-A0JB_L_CC_20010607_2.dcm',
            'TCGA-AO-A0JB_L_MLO_20010607_1.dcm',
            'TCGA-AO-A0JB_L_MLO_20010607_2.dcm',
            'TCGA-AO-A0JB_R_CC_20010607_1.dcm',
            'TCGA-AO-A0JB_R_CC_20010607_2.dcm',
            'TCGA-AO-A0JB_R_MLO_20010607_1.dcm',
            'TCGA-AO-A0JB_R_MLO_20010607_2.dcm']
        self.assertListEqual(list(result.values()), expected) 
    
    def test_sortdicom_writes_to_output_dir(self):
        
        processor.sortdicom(self.patientA_filepath, self.output_dir) 
        files = os.listdir(self.output_dir) 
        expected = ['TCGA-AO-A0JB_L_CC_20010607_1.dcm',
            'TCGA-AO-A0JB_L_CC_20010607_2.dcm',
            'TCGA-AO-A0JB_L_MLO_20010607_1.dcm',
            'TCGA-AO-A0JB_L_MLO_20010607_2.dcm',
            'TCGA-AO-A0JB_R_CC_20010607_1.dcm',
            'TCGA-AO-A0JB_R_CC_20010607_2.dcm',
            'TCGA-AO-A0JB_R_MLO_20010607_1.dcm',
            'TCGA-AO-A0JB_R_MLO_20010607_2.dcm']
        for e in expected: 
            self.assertIn(e,files)

        
        [os.remove(os.path.join(self.output_dir,f)) for f in files if f != '.gitkeep']

    
    def test_sortdicom_creates_output_dir_if_not_exists(self):
        new_output_dir = os.path.join(DATA_DIR, 'test_output_dir') 
        processor.sortdicom(self.patientA_filepath,new_output_dir) 

        files = os.listdir(new_output_dir) 
        expected = ['TCGA-AO-A0JB_L_CC_20010607_1.dcm',
            'TCGA-AO-A0JB_L_CC_20010607_2.dcm',
            'TCGA-AO-A0JB_L_MLO_20010607_1.dcm',
            'TCGA-AO-A0JB_L_MLO_20010607_2.dcm',
            'TCGA-AO-A0JB_R_CC_20010607_1.dcm',
            'TCGA-AO-A0JB_R_CC_20010607_2.dcm',
            'TCGA-AO-A0JB_R_MLO_20010607_1.dcm',
            'TCGA-AO-A0JB_R_MLO_20010607_2.dcm']
        for e in expected: 
            self.assertIn(e,files)
        
        #[os.remove(os.path.join(new_output_dir,f)) for f in files if f != '.gitkeep']
        shutil.rmtree(new_output_dir)


    def test_sortdicom_handles_multiple_patients(self):
        expected = [
            'TCGA-AO-A0JB_L_CC_20010607_1.dcm',
            'TCGA-AO-A0JB_L_CC_20010607_2.dcm',
            'TCGA-AO-A0JB_L_MLO_20010607_1.dcm',
            'TCGA-AO-A0JB_L_MLO_20010607_2.dcm',
            'TCGA-AO-A0JB_R_CC_20010607_1.dcm',
            'TCGA-AO-A0JB_R_CC_20010607_2.dcm',
            'TCGA-AO-A0JB_R_MLO_20010607_1.dcm',
            'TCGA-AO-A0JB_R_MLO_20010607_2.dcm',
            'TCGA-AO-A0JI_L_CC_20010505_1.dcm',
            'TCGA-AO-A0JI_L_CC_20010505_2.dcm',
            'TCGA-AO-A0JI_L_CC_20010505_3.dcm',
            'TCGA-AO-A0JI_L_CC_20010505_4.dcm',
            'TCGA-AO-A0JI_L_MLO_20010505_1.dcm',
            'TCGA-AO-A0JI_L_MLO_20010505_2.dcm',
            'TCGA-AO-A0JI_L_MLO_20010505_3.dcm',
            'TCGA-AO-A0JI_L_MLO_20010505_4.dcm']

        result = processor.sortdicom(DATA_DIR)
        for e in expected: 
            self.assertIn(e, list(result.values()))
        

   