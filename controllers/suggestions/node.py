class Node:
    def __init__(self, title):
        self._title = title
        self.outgoing_neighbours = []
        self.incoming_neighbours = []
        self.songs = []

    def append_outcoming(self, neighbour):
        self.outgoing_neighbours.append(neighbour)

    def append_incoming(self, neighbour):
        self.incoming_neighbours.append(neighbour)

    def append_song(self, song):
        self.songs.append(song)

    def append_all(self, all_neighbours):
        for el in all_neighbours:
            self.outgoing_neighbours.append(el)

    def get_n_order_neighbours(self, order, network, all_set=None, frontier=None):
        if not all_set:
            all_set = {}
        if not frontier:
            frontier = self.get_outgoing_neighbours()
        if order == 0:
            return all_set
        else:
            future_frontier = []
            for el in frontier:
                future_frontier.extend(network.get_member_by_title(el.get_title()).get_outgoing_neighbours())
                if not all_set.get(el.get_title()):
                    all_set[el.get_title()] = el
            return self.get_n_order_neighbours(order - 1, network, all_set, future_frontier)

    def get_outgoing_neighbours(self):
        return self.outgoing_neighbours

    def get_incoming_neighbours(self):
        return self.incoming_neighbours

    def __str__(self):
        return self._title

    def get_title(self):
        return self._title

    def print_top_songs(self, n):
        print_string = ""
        for song in self.songs[:n]:
            print_string += song._title + " | "
        return print_string

    def get_songs(self):
        return self.songs