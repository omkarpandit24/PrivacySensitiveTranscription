import argparse
import cv2
import _pickle as pickle

# view items in clusters
def main(model_path):
    print('[INFO] Loading saved clustering model from \'' + model_path + '\'')
    with open(model_path, 'rb') as handle:
        unpickler = pickle.Unpickler(handle)
        model = unpickler.load()
        labels = model['labels']

    unique_labels = set(labels.values())
    print('[INFO] ' + str(len(unique_labels) - 1) + ' unique clusters and ' + \
          str(list(labels.values()).count(-1)) + ' noise points found')

    print('[INFO] Press ESC to stop viewing a cluster, press any other key to continue')

    while True:
        # get user input
        label = input('[INFO] Input a number from ' + str(min(unique_labels)) + \
                      ' to ' + str(max(unique_labels)) + ' to view a cluster: ')

        try:
            label = int(label)
        except:
            print('[ERROR] Expected an int')
            continue

        if label not in unique_labels:
            print('[ERROR] Input not in specified range')
            continue

        # view items in clusters
        for im, l in labels.items():
            if l == label:
                img = cv2.imread('./images/' + im, 0)
                cv2.imshow(im, img)

                k = cv2.waitKey(0) & 0xFF
                cv2.destroyAllWindows()

                # press ESC to exit
                if k == 27:
                    break

if __name__ == '__main__':
    # require clustering model filepath
    parser = argparse.ArgumentParser(description='Manually inspect clusters')
    parser.add_argument('-p', '--path', required=True,
                        nargs=1, action='store',
                        type=str, dest='model_path',
                        help='The filepath of the clustering model')

    args = vars(parser.parse_args())
    model_path = args['model_path'][0]

    main(model_path)

