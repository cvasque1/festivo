from unicodedata import name

class Artist:
    name = ""
    _id = ""
    genres = []
    image = ""

    def __init__(self, name=None, _id=None, genres=None, image=None) -> None:
        self.name = name
        self._id = _id
        self.genres = genres
        self.image = image

    def __hash__(self):
        return hash((self.name, self._id))

    def __eq__(self, other):
        if type(self) == type(other):
            return self.name == other.name and self._id == other._id
        else:
            return False


class Playlist:
    name = ""
    _id = ""
    tracks = {}

    def __init__(self, name=None, _id=None, tracks=None) -> None:
        self.name = name
        self._id = _id
        self.tracks = tracks


class Track:
    name = ""
    _id = ""

    def __init__(self, name=None, _id=None) -> None:
        self.name = name
        self._id = _id
