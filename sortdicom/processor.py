""" Given an input directory will load .dcm files 
"""

import os 
import sys
import shutil 
import pathlib
from collections import OrderedDict

from .handler import DicomFileHandler 

DEFAULT_TYPES = ["mrn", "laterality","view", "date", "sequence_info", "modality"]

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
    for i,h in enumerate(headers):
        uid += handler.get_dicom_header_tag(h)
        if i < len(headers) - 1 and uid != '':
            uid += '_'

    if len(uid) == 0:
        raise BlankDicomHeaderError('No headers were found for this dicom file: {}'.format(dicom_filepath)) 

    return uid + suffix


def _label_duplicates(ordered_dict):
    """ takes an ordered dict and sorts the key value pairs. It checks 
    for duplicates within small groups
    """
    # sort the key value pairs so that duplicates line up 
    fname_tuples = sorted(ordered_dict.items(), key=lambda x:x[1])
    fname_lists = [list(f) for f in fname_tuples]

    current_candidate_duplicate = fname_lists[0][1] # start with the first one
    counter = 1  
    for i, row in enumerate(fname_lists): 
        if row[1] == current_candidate_duplicate: 
            row[1] = row[1].replace('.dcm', '_{}.dcm'.format(counter))  # append counter 
            counter += 1  #increment
        else:
            counter = 1  # reset the counter
            current_candidate_duplicate = row[1] # set the new duplicate candidate
            row[1] = row[1].replace('.dcm', '_{}.dcm'.format(counter)) 
            counter += 1
    
    return OrderedDict(fname_lists)

def sortdicom(root_dir, output_dir=None):
    """ Main entrypoint for program. Given a patient_root_dir and an intended output_dir, extract dicom headers 
    from all .dcm in underlying subfolders and copy to the output_dir. 
    If with_copy is True will perform the copy to the output dir

    :param str root_dir: The root dir for a project. Will parse .dcm from this folder down to the root and extract all into an array. 
    :param str output_dir: The intended output dir. If set to None (default) then no copy will take place (useful for testing) 
    :returns: a dictionary mapping the original filepath on the system to the new filepath. Useful for debugging or logging the filepath output for larger projects 
    :rtype: dict
    """
    root_dir = pathlib.Path(root_dir)  # NOTE assumes input path was already checked

    if output_dir:
        if not os.path.exists(output_dir): # do not make output_dir if with_copy = False
            l.info('Creating output dir {}'.format(output_dir))
            os.mkdir(output_dir)

    # check root dir exists and construct abspath
    dicom_filepaths = _get_all_dicom_filepaths(root_dir) 
    copy_map = OrderedDict()  # key -> original name  value -> new name w/ uid 
    repeat_counter = 1 
    
    for f in dicom_filepaths: 
        try:
            l.info('Extracting dicom header data for:    {}'.format(f))
            uid_filename = _build_dicom_unique_identifier(f)
            copy_map[f] = uid_filename
        except BlankDicomHeaderError as err: 
            l.error(str(err)) 
    # treat duplicates 
    copy_map = _label_duplicates(copy_map)
    if output_dir:
        for k,v in copy_map.items():
            l.info('Copying: {}   to   {}'.format(k, os.path.join(output_dir, v))) 
            _copy_dicom_file(k, v, output_dir)
    
    return copy_map 


