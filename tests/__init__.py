""" check if we have test data else bail on the tests 
Should have patientA and patientB dicom files
"""
import os 

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

d = os.listdir(DATA_DIR)
if 'patientA' not in d or 'patientB' not in d:
    raise RuntimeError('Cannot run tests missing patientA and patientB data folders')

check_paths = [path for path in os.walk(DATA_DIR)]
dicom_test_files = []

for path in check_paths:
    for p in path[-1]:
        if '.dcm' in p:
            dicom_test_files.append(p)

if len(dicom_test_files) == 0:
    raise RuntimeError('Cannot run tests. No dcm files detected in test folder')