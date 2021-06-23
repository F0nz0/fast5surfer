import os
import h5py

def SUBS(path, parent, tree):    
    for p in os.listdir(path):
        abspath = os.path.join(path, p)
        parent_element = tree.insert(parent, 'end', text=p, open=False)
        if os.path.isdir(abspath):
            SUBS(abspath, parent_element, tree)

def SUBS_fast5(file, parent, tree):
    for key in file.keys():
        parent_element = tree.insert(parent, "end", text=key, open=True)
        if type(file[key]) == h5py._hl.group.Group:
            SUBS_fast5(file[key], parent_element, tree)


def print_attrs(name, obj):
    '''Funzione usata per iterare attraverso la struttura del file fast5/hdf5'''
    print(name)

    '''
    # FULL CODE FOUND ON STACK OVERFLOW. To BE ADAPTED
    def print_attrs(name, obj):
    print(name)
    for key, val in obj.attrs.items():
        print("    %s: %s" % (key, val))

    f = h5py.File('foo.hdf5', 'r')
    f.visititems(print_attrs)
    '''