import h5py
import sys

def print_structure(name, obj):
    if isinstance(obj, h5py.Dataset):
        print(f"Dataset: {name}, Shape: {obj.shape}, Dtype: {obj.dtype}")
        for k, v in obj.attrs.items():
            print(f"  Attr: {k} = {v}")
    elif isinstance(obj, h5py.Group):
        print(f"Group: {name}")
        for k, v in obj.attrs.items():
            print(f"  Attr: {k} = {v}")

with h5py.File('FiberTest_10sec_C1_2026-04-02T14.tsb.h5', 'r') as f:
    print("ROOT Attributes:")
    for k, v in f.attrs.items():
        print(f"  {k} = {v}")
    f.visititems(print_structure)
