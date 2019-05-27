import pydicom  

import logging 
l = logging.getLogger(__name__)


class DicomFileHandler:
    """ Reads in an instance of Dicom file and extracts metadata.  
    Uses a mapping dict to group tag labels to search for fields present in the dicom in 
    order of precedence.  
    """

    mapping = {
        'mrn': [ (0x0010, 0x0020), ], # TODO get the other thing for utah
        'laterality': [ (0x0020, 0x0060), (0x0020, 0x0062) ], 
        'view': [ (0x0018, 0x5101) ], 
        'date': [ (0x0008, 0x0022), (0x0008, 0x0020) ], 
        # 'sequence_info': [ (0x0008, 0x103E), (0x0008, 0x1030), ],  # dropping in 0.1.1
        # 'modality': [ (0x0008, 0x0060), ], 
    }

    def __init__(self): 
        self.ds = None 
        self.filepath = None
        

    def _clean_tag(self, tag=''): 
        """ clean up the tag by replacing some whitespace and bad chars with _ or blanks
        """
        return tag.replace(' ', '-') \
            .replace('/','-') \
            .replace('(','') \
            .replace(')','') \
            .replace('*', '') \
            .replace('&', '') \
            .replace('$', '') \
            .replace(':', '.')
        
    
    def load(self, filepath=''):
        """ trys to load a dicom file given an absolute path and sets in on the instance
        :param str filepath: The filepath to the dicom header
        :raise: IOError if invalid path  
        """
        try: 
            self.ds = pydicom.dcmread(filepath)
            self.filepath = filepath
        except IOError as err:
            l.error('Invalid filepath. Double check the path you entered for {}'.format(filepath))
            raise  
        


    def list_header_mappings(self):
        """ return a list of the mapping key names to reference
        :return: a list of the mapping keys 
        :rtype: list 
        """ 
        return list(self.mapping.keys())  


    def get_dicom_header_tag(self, tagname=''): 
        """ loop through the dicom header key and create a tag for a single key. These 
        can be concatenated to form a unique identifier. Valid names are: "mrn", "laterality",
        "view", "type", "date", "sequence_info", "modality", "instance_number".
        
        :param str tagname: A tagname key from DicomFileHandler.mapping
        :returns: A string with the value for dicom header key.
        :rtype: str 
        """
        tagname = tagname.lower()
        if tagname not in self.mapping.keys():
            raise ValueError('Invalid dicom mapping name. Use list_header_mappings to get key names.')

        l.info('Now working on file: {}'.format(self.filepath))  # to help debug in terminal
        hexes = self.mapping[tagname]
        tag = '' 
        for h in hexes: 
            try:
                val = str(self.ds[h].value)
                if len(val) > 0:
                    l.debug('Found tag: {} -> {}'.format(h, val))
                    tag += val
                    break
            except KeyError as err:
                l.warn('Could not find tag for {} -> skipping this tag.'.format(h))
                
        return self._clean_tag(tag)
