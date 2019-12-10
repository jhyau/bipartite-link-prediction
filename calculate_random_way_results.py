import util
import snap

train = util.load_json("./data/train/oag_random_walks.json")
test = util.load_json("./data/test/oag_random_walks.json")

with open('./data/train/oag_random_walk_results.txt', "w") as file:
    for key in train:
        prediction = 0
        maximum = 0
        for inner in train[key]:
            if train[key][inner] > maximum:
                maximum = train[key][inner]
                prediction = inner

        file.write(str(key) + " " + str(prediction) + "\n")

print("Finished writing out results for train!")

with open('./data/test/oag_random_walk_results.txt', 'w') as f:
    for key in test:
        prediction = 0
        maximum = 0
        for inner in test[key]:
            if test[key][inner] > maximum:
                maximum = test[key][inner]
                prediction = inner

        f.write(str(key) + " " + str(prediction) + "\n")

print("Finished writing out results for test")

def accuracy(truth, predictions, set_type):
    count = 0
    total = 0
    G = snap.LoadEdgeList(snap.PUNGraph, truth, 0, 1)
    with open(predictions, 'r') as pred:
        line = pred.readline()
        while line:
            key = line.split()
            if G.IsEdge(int(key[0]), int(key[1])):
                count += 1
            total += 1
            line = pred.readline()

    print(set_type + " accuracy is : ", count / total)
    print("total values: ", total)
    print("raw correct: ", count)

accuracy("./data/full.txt", "./data/train/oag_random_walk_results.txt", "train")
accuracy("./data/full.txt", "./data/test/oag_random_walk_results.txt", "test")
