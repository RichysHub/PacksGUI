import os
from datetime import datetime

from utils import date_from_filename


# Todo: Probably want a rename, given we aren't assuming it's a pack any more
class CardPack:
    def __init__(self, file_path, folder_path):
        self.image_name = file_path

        self.folder_path = folder_path
        self.full_path = os.path.join(folder_path, file_path)
        # Todo: datetime module wants ints, not strings, so is a bit of a pain
        # --> May want to reevaluate implementation of the sortkey
        self.sortkey = date_from_filename(file_path)
        self.date_time = datetime(*[int(val) for val in self.sortkey.split('/')])
        self.date = self.date_time.date()
        self.time = self.date_time.time()