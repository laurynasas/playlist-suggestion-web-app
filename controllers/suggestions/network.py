from node import Node
from song import load_songs

SOURCE_MARKER = "++"


class Network:
    def __init__(self):
        self.members = {}
        self.sources = {}
        self.songs = []
        self.search_box = []

    def get_member_by_title(self, title):
        return self.members.get(title)

    def get_source_by_title(self, title):
        return self.sources.get(title)

    def append_source(self, other):
        self.sources[other.__str__()] = other
        self.members[other.__str__()] = other

    def append_member(self, other):
        self.members[other.__str__()] = other

    def __str__(self):
        reprs = ""
        for member in self.members.values():
            relation = member.__str__() + " || "
            reprs += relation
        return reprs

    def get_members(self):
        return self.members

    def register_new_song(self, song):
        self.songs.append(song)
        self.search_box.append(song.get_song_artist() + " - " + song.get_title())

    def prepare_songs_search_box(self):
        return self.search_box

def load_network(network_file_dir, sources_to_load):
    network_file = open(network_file_dir, "r")
    content = network_file.readlines()
    network = Network()

    i = 0
    sources = 0
    while sources != sources_to_load:
        title = content[i].replace("\n", "")

        if SOURCE_MARKER in content[i]:
            source = Node(title.replace(SOURCE_MARKER, ""))
            network.append_source(source)
            sources += 1
        else:
            neigh = network.get_member_by_title(title)
            if not neigh:
                neigh = Node(title)
                network.append_member(neigh)
            neigh.append_incoming(source)
            source.append_outcoming(neigh)
        i += 1

    return network


def load_network_with_songs(network_file_dir, songs_file_dir, sources_to_load):
    network = load_network(network_file_dir,
                           sources_to_load)

    load_songs(songs_file_dir,
               sources_to_load, network)

    return network
