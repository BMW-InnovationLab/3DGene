import argparse
import os.path

import random
import numpy
import numpy as np

from layoutgeneration.generation.generate import generate_from_json
from layoutgeneration.generation.save import save_final_regions
from layoutgeneration.layout.region import load_region_types
from layoutgeneration.visualization.plot import plot_generation_tree

if __name__ == '__main__':
    random.seed(42)
    np.random.seed(42)
    parser = argparse.ArgumentParser(prog='AiPipeline Layout Generator',
                                     description='Generate a 2D layout based on a hierarchy of generation strategies')
    parser.add_argument('-r', '--regions', required=True)
    parser.add_argument('-s', '--strats', required=True)
    parser.add_argument('-o', '--output', required=True)
    parser.add_argument('-v', '--visualize', action='store_true')

    args = parser.parse_args()

    load_region_types(args.regions)
    roots = generate_from_json(args.strats)

    save_final_regions(roots[-1], args.output, args.visualize)

    if args.visualize:
        plot_generation_tree(roots[-1], os.path.dirname(args.output))
