""" Given an input directory will load .dcm files 
"""

import os 
import sys
import shutil 
import pathlib

from .handler import DicomFileHandler 

DEFAULT_TYPES = ["mrn", "laterality","view", "type", "date", "sequence_info", "modality", "instance_number"]

import logging 
l = logging.getLogger(__name__)


class BlankDicomHeaderError(Exception):
    """ thrown when a dicom file returns no header metadata
    """


def _get_all_dicom_filepaths(patient_root_dir=''):
    """ Given a patient root directory, walks through subfolders top down and 
    returns a list of absolute dicom_filepaths 
    """
    walk = os.walk(patient_root_dir)
    
    dicom_filepaths = []
    for w in walk: 
        dicom_files = [f for f in w[-1] if '.dcm' in f]  # extracts .dcm files 
        basepath = pathlib.Path(w[0])  # extracts the basepath 
        full_paths = [os.path.join(basepath, df) for df in dicom_files] # combines the basepath with each .dcm file 
        for f in full_paths:
            dicom_filepaths.append(f) # load into master list 
    
    return dicom_filepaths 
    


def _copy_dicom_file(original_dicom_filepath='', new_uid_name='', target_dir=''): 
    """ copy a dicom file from its original path, give a new name from the unique_identifier 
    and place in the target_dir 
    """
    outfile_path = os.path.join(target_dir, new_uid_name)
    shutil.copy(original_dicom_filepath, outfile_path)


def _build_dicom_unique_identifier(dicom_filepath='', headers=None):
    """ Builds a unique identifier string for a single dicom file. The headers kwarg defaults 
    to look for all fields in the mapping if set to None. 
    """
    handler = DicomFileHandler()
    handler.load(dicom_filepath)

    if not headers:  # get all mappings unless headers
        headers = handler.list_header_mappings()

    uid = ''
    suffix = '.dcm'
    for h in headers:
        uid += handler.get_dicom_header_tag(h)

    if len(uid) == 0:
        raise BlankDicomHeaderError('No headers were found for this dicom file: {}'.format(dicom_filepath)) 

    return uid + suffix




def sortdicom(patient_root_dir='', output_dir='', with_copy=True):
    """ Main entrypoint for program. Given a patient_root_dir and an intended output_dir, extract dicom headers 
    from all .dcm in underlying subfolders and copy to the output_dir. 
    If with_copy is True will perform the copy to the output dir

    :param str patient_root_dir: The root dir for a single patient 
    :param str output_dir: The intended output dir. It will be created if it does not exist. 
    :param bool with_copy: Will copy the .dcm to the output folder if set to True. (defaults to True)
    :returns: a dictionary mapping the original filepath on the system to the new filepath 
    :rtype: dict
    """
    patient_root_dir = pathlib.Path(patient_root_dir)  # NOTE assumes input path was already checked

    if not os.path.exists(output_dir):
        l.info('Creating output dir {}'.format(output_dir))
        os.mkdir(output_dir)

    # check root dir exists and construct abspath
    dicom_filepaths = get_all_dicom_filepaths(patient_root_dir) 
    copy_map = {}  # key -> original name  value -> new name 

    for f in dicom_filepaths: 
        try:
            l.info('Extracting dicom header data for:    {}'.format(f))
            uid_filename = build_dicom_unique_identifier(f)
            copy_map[f] = uid_filename
        except BlankDicomHeaderError as err: 
            l.error(str(err)) 
    
    if with_copy:
        for k,v in copy_map.items():
            l.info('Copying: {}   to   {}'.format(k, os.path.join(output_dir, v))) 
            copy_dicom_file(k, v, output_dir)
    
    return copy_map 


