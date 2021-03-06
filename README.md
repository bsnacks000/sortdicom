## sortdicom 

| version |
|:-------:|
| 0.1.1 | 

A package that extracts metadata from dicom header tags using ```pydicom```, renames the files with that metadata and copies them to a new location.

### Install 
-----------

Install using pip from this repo after creating a virtualenv. If you're using anaconda you should install ```pip``` and ```git``` first.

```
$ pip install git+https://github.com/bsnacks000/sortdicom.git@v0.1.0#egg=sortdicom
```

Replace the ```@v0.1.0``` with some other version if it exists in the repo. Available releases are tagged and listed under the github release tag.

If you have ```make``` installed you can clone this repo and run:

```
$ make install 
```

### Usage 
--------- 

There's a simple entrypoint in the processor package. An example script would simply look like this. It could be run inside a script, interpreter or jupyter notebook. 

```python
import sortdicom.processor as processor 

root_dir = 'absolute/path/to/my/project/root/dir/'
output_dir = 'absolute/path/to/my/project/output/dir/'

results = processor.sortdicom(root_dir, output_dir)
```
This will attempt to parse tags for any files with a .dcm extension within the root folder regardless of depth. So if you have multiple patients with multiple subdirectories per patient in your project root, this program walk the file tree and attempt to parse all .dcms that are in any subdirectories.  

The ```results``` object returned by this function call contains a mapping of the original filepath to the newly mapped filename derived from the tags.

For debugging you can first run ```processor.sortdicom``` without the ```output_dir``` key word argument. When this is set to ```None``` it will not copy any files. This could be useful for debugging to make sure you get the correct tags before writing to the file system.


## Tests

The tests unfortunately won't work without specific public NIH dicom files that are too big to version control. If I ever release this on pypi I will host the files somewhere for testing purposes, but for now just email me if you want the data to run the tests. The files need to be placed in specific folders I marked in the testing folder.  
