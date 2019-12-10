import os
import random
import snap
import util
from collections import defaultdict, Counter

class KeyToInt():
    def __init__(self):
        self._n = -1
        self._map = {}


    def __getitem__(self, key):
        if key not in self._map:
            self._n += 1
            self._map[key] = self._n
        return self._map[key]

def write_node_data(nid_f, nids, infile, outfile):
    return util.write_json({nid_f(datum): datum for datum in util.load_json_lines(infile)
        if nid_f(datum) in nids}, outfile)


def create_graph(path):
    id_to_nid = KeyToInt()
    train_author_ids = []
    test_author_ids = []
    train_affiliation_ids = []
    test_affiliation_ids = []
    with open(path + 'train/graph.txt', 'w') as graph, open(path + 'train/new_edges.txt', 'w') as edges, \
            open(path + 'test/graph.txt', 'w') as test_graph, open(path + 'test/new_edges.txt', 'w') as test_edges, \
            open('./data/id_to_nid.txt', 'w') as mapping, open('./data/nid_to_id.txt', 'w') as inverse, open ('./data/full.txt', 'w') as full:
        with open("../bipartite/data/oag_data/data.txt", 'r') as file:
            line = file.readline()
            while line:
                keys = line.split()
                author_key = id_to_nid[keys[0]]
                affiliation_key = id_to_nid[keys[1]]
                mapping.write(str(keys[0]) + " " + str(author_key) + "\n")
                mapping.write(str(keys[1]) + " " + str(affiliation_key) + "\n")
                inverse.write(str(author_key) + " " + str(keys[0]) + "\n")
                inverse.write(str(affiliation_key) + " " + str(keys[1]) + "\n")
                full.write(str(author_key) + " " + str(affiliation_key) + "\n")

                # Randomly select 80% of entries to be in train_graph and train_new_edges
                # Still include all of the training set into the test set graph.txt
                if (random.randint(1, 100) >= 20):
                    if (random.randint(1, 100) >= 20):
                        graph.write(str(author_key) + " " + str(affiliation_key) + "\n")
                    else:
                        edges.write(str(author_key) + " " + str(affiliation_key) + "\n")

                    test_graph.write(str(author_key) + " " + str(affiliation_key) + "\n")
                    train_author_ids.append(author_key)
                    test_author_ids.append(author_key)
                    train_affiliation_ids.append(affiliation_key)
                    test_affiliation_ids.append(affiliation_key)
                # Randomly select 20% of entries to be test_graph and test_new_edges only
                else:
                    if (random.randint(1, 100) >= 20):
                        test_graph.write(str(author_key) + " " + str(affiliation_key) + "\n")
                    else:
                        test_edges.write(str(author_key) + " " + str(affiliation_key) + "\n")
                    test_author_ids.append(author_key)
                    test_affiliation_ids.append(affiliation_key)
                    
                line = file.readline()

    return train_author_ids, train_affiliation_ids, test_author_ids, test_affiliation_ids


def make_examples_simple(data_dir, author_ids, affiliation_ids, n_authors, negative_samples):
    graph = snap.LoadEdgeList(snap.PUNGraph, data_dir + 'graph.txt', 0, 1)
    new_edges = defaultdict(dict)
    with open(data_dir + 'new_edges.txt', 'r') as f:
        line = f.readline()
        while line:
            u, b = map(int, line.split())
            new_edges[u][b] = 1
            line = f.readline()
    
    # Just use all authors in new_edges
    examples = defaultdict(dict)
    Rnd = snap.TRnd(42)
    Rnd.Randomize()
    authors = []
    #for i in range(n_authors):
    #    authors.append(graph.GetRndNId(Rnd))
    # If just add in nodes from new_edges, there is KeyError
    for u in new_edges.keys():
        authors.append(u)
    
    print(len(authors))
    for u in authors:
        examples[u] = new_edges[u]
        for i in range(negative_samples):
            b = random.choice(affiliation_ids)
            examples[u][b] = 0

    p, n = 0, 0
    for u in examples:
        for b in examples[u]:
            p += examples[u][b]
            n += 1 - examples[u][b]

    print("Positive: ", p)
    print("Negative: ", n)
    print("Data skew: ", p / (p + n) )
    print("Sampling rate: ", negative_samples / len(affiliation_ids))
    print("writing examples...")
    util.write_json(examples, data_dir + 'oag_examples_simple.json')




if __name__ == '__main__':
    #TODO: Figure out how exactly make examples works...
    train_authors, train_affiliations, test_authors, test_affiliations = create_graph("./data/")
    make_examples_simple("./data/train/", train_authors, train_affiliations, 10000, 10)
    make_examples_simple("./data/test/", test_authors, test_affiliations, 50000, 10)
