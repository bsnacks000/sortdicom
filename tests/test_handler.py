import unittest  
import pydicom 
import os

from . import DATA_DIR
from sortdicom.handler import DicomFileHandler

dicomfilepath = os.path.join(DATA_DIR, 'patientA', '4947-DIG DIAG MAMMOGR-94476', '000000.dcm')

class TestHandler(unittest.TestCase):

    def setUp(self): 
        self.dfh = DicomFileHandler()
        self.dicomfilepath = os.path.join(
            DATA_DIR, 'patientA', '4947-DIG DIAG MAMMOGR-94476', '000000.dcm')

    def tearDown(self): 
        self.dfh.ds = None 
    
    def test_dicom_file_handler_init(self):
        self.assertTrue(hasattr(self.dfh, 'ds'))
        self.assertIsNone(self.dfh.ds) 

    def test_dicom_file_handler_clean_tag_removes_special_chars(self): 
        
        test_string = 'HE$)(LLO/: T)H*&$*ERE'  
        expected = 'HELLO-.-THERE'
        test = self.dfh._clean_tag(test_string)
        self.assertEqual(test, expected)

    def test_dicom_file_handler_load_correct_file(self):
        self.dfh.load(self.dicomfilepath)
        self.assertTrue(isinstance(self.dfh.ds, pydicom.dataset.FileDataset))

    def test_dicom_load_bad_filepath_raises_IOError(self): 
        with self.assertRaises(IOError):
            self.dfh.load('blah')    

    def test_dicom_load_incorrect_type_raises_InvalidDicomError(self):

        with self.assertRaises(pydicom.errors.InvalidDicomError):
            self.dfh.load(os.path.join(DATA_DIR, 'dummyfile.csv'))

    def test_dicom_list_header_mappings(self): 

        expected = ['mrn', 'laterality', 'view', 'date', 'sequence_info', 'modality']
        mapping = self.dfh.list_header_mappings()
        
        for e in expected:
            self.assertIn(e, mapping)
    
    def test_dicom_header_tag_extracts_values_using_dicom_file(self):
        self.dfh.load(self.dicomfilepath)   

        laterality = self.dfh.get_dicom_header_tag('laterality')
        mrn = self.dfh.get_dicom_header_tag('mrn')
        view = self.dfh.get_dicom_header_tag('view')
        date = self.dfh.get_dicom_header_tag('date')
        sequence_info = self.dfh.get_dicom_header_tag('sequence_info')
        modality = self.dfh.get_dicom_header_tag('modality')
        
        self.assertEqual(laterality, 'L')
        self.assertEqual(mrn, 'TCGA-AO-A0JB')
        self.assertEqual(view, 'MLO')
        self.assertEqual(date, '20010607')
        self.assertEqual(sequence_info, 'DIG-DIAG-MAMMOGR')
        self.assertEqual(modality, 'MG')

    def test_invalid_tagname_raises_ValueError(self):
        
        with self.assertRaises(ValueError):
            self.dfh.get_dicom_header_tag('blah')