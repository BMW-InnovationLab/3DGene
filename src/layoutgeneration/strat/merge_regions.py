from typing import List, Tuple, Dict

import numpy as np
from tqdm import tqdm

from layoutgeneration.layout.orientation import Orientation
from layoutgeneration.layout.region import Region, get_types


def find_reg(arr: np.ndarray, value_to_merge: Tuple) -> Dict:
    mask = np.all(arr == value_to_merge, axis=-1)
    if not np.any(mask):
        return None

    # Find the starting row and col
    idx_flat = np.argmax(mask)
    start_row, start_col = np.unravel_index(idx_flat, mask.shape)
    row = arr[start_row]

    # Find the width
    mask = np.all(row[start_col:] == value_to_merge, axis=-1)
    width = np.argmin(mask)
    if width == 0:  # Case where the width runs all along the row
        width = len(row) - start_col

    # Find the height
    mask = np.all(arr[start_row:, start_col:start_col + width] == value_to_merge, axis=-1)
    mask = np.all(mask, axis=1)
    height = np.argmin(mask)
    if height == 0:
        height = arr.shape[0] - start_row

    # Return the region as a dictionary
    region = {"y": start_col, "x": start_row, "height": width, "width": height}
    return region


class MergeRegion:

    def __init__(self):
        self.region_types = get_types()

    def find_all_regions(self, arr, orient: Orientation):
        result = []
        for region_type in tqdm(self.region_types):
            while True:
                region = find_reg(arr, (*region_type.value, orient.value))

                if region is None:
                    break

                region["orient"] = orient
                region["type"] = region_type
                result.append(region)

                start_row = region["y"]
                end_row = region["y"] + region["height"]
                start_col = region["x"]
                end_col = region["x"] + region["width"]
                arr[start_col:end_col, start_row:end_row] = -1

        return result

    def generate(self, mat, root: Region) -> List[Region]:
        print("Merging regions with orientation UP")
        regions = self.find_all_regions(mat, Orientation.UP)
        print("Merging regions with orientation DOWN")
        regions.extend(self.find_all_regions(mat, Orientation.DOWN))
        print("Merging regions with orientation LEFT")
        regions.extend(self.find_all_regions(mat, Orientation.LEFT))
        print("Merging regions with orientation RIGHT")
        regions.extend(self.find_all_regions(mat, Orientation.RIGHT))

        # to remove blank arrays: []
        regions = [x for x in regions if x]

        # create new list of regions
        new_regions = []

        for region in regions:
            new_regions.append(Region(region["x"] + root.x, region["y"] + root.y, region["width"],
                                      region["height"], region["orient"], region["type"]))
        return new_regions
