import argparse
import hdbscan
import numpy as np
import os.path as path
import _pickle as pickle
import time

# train a density-based model using the feature vectors
def main(feats_path, max_cluster_size):
    print('[INFO] Preparing to cluster features from ' + feats_path)

    # load feature vectors
    with open(feats_path, 'rb') as handle:
        unpickler = pickle.Unpickler(handle)
        index = unpickler.load()
        index = {name: vector for name, vector in index.items() if vector is not None}

    # labels
    labels = {}

    # start timer
    start = time.time()

    # cluster iteratively
    min_cluster_size = max_cluster_size
    while len(index) > 0 and min_cluster_size >= 2:
        print('[INFO] Clustering ' + str(len(index)) + ' points with min_cluster_size=' + str(min_cluster_size))
        clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, min_samples=None,
                                    metric='braycurtis', algorithm='best',
                                    core_dist_n_jobs=-1)

        # reshape 3d vectors to 2d
        dataset = list(index.values())
        dataset = np.asarray(dataset)

        # fit clusterer
        clusterer.fit(dataset)

        # update labels (treat cluster 0 as noise)
        new_labels = clusterer.labels_

        current_max = max(labels.values()) if len(labels) > 0 else -1
        new_labels = [label + current_max if label > 0 else -1 for label in new_labels]

        new_labels = dict(zip(index.keys(), new_labels))
        labels.update(new_labels)

        # get features of noise points to recluster
        index = {k: v for k, v in index.items() if new_labels[k] == -1}
        min_cluster_size -= 1

    # end timer and print
    end = time.time()
    print('[INFO] Clustering completed after ' + str(end - start) + ' seconds')

    # save labels to disk
    base = path.basename(feats_path)
    name = path.splitext(base)[0]

    output = '../labels/iterative_' + name + '_mcs' + str(max_cluster_size) + '_labels.pickle'
    print('[INFO] Saving labels to ' + output)
    with open(output, 'wb') as handle:
        pickle.dump(labels, handle, protocol=4)

if __name__ == '__main__':
    # require filepath of features and name of clusterer to use
    parser = argparse.ArgumentParser(description='Cluster image feature vectors')
    parser.add_argument('-f', '--feats', required=True,
                        nargs=1, action='store',
                        type=str, dest='feats_path',
                        help='The filepath of the feature vectors')
    parser.add_argument('-m', '--max_cluster_size', required=True,
                        nargs=1, action='store',
                        type=int, dest='max_cluster_size',
                        help='The max clustering size to begin with')

    args = vars(parser.parse_args())
    feats_path = args['feats_path'][0]
    max_cluster_size = args['max_cluster_size'][0]

    main(feats_path, max_cluster_size)

