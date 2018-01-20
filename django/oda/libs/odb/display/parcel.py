import logging

from oda.libs.odb.display.base import DisplayGenerator
from oda.libs.odb.display.code import CodeDisplayGenerator
from oda.libs.odb.display.data import DataDisplayGenerator

logger = logging.getLogger(__name__)

class ParcelDisplayGenerator(DisplayGenerator):
    def __init__(self, context):
        super().__init__(context)
        self.ofd = context.ofd

    def display(self, parcel):

        # set the current window based on this parcel's boundaries
        if self.context.cur_start and parcel.vma_start < self.context.cur_start:
            # nothing to do, start of window is good
            pass
        # else, initialize start to the start of the parcel
        else:
            self.context.cur_start = parcel.vma_start

        if self.context.cur_end and parcel.vma_end >= self.context.cur_end:
            # nothing to do, end of window is good
            pass
        else:
            self.context.cur_end = parcel.vma_end

        if parcel.is_code:
            codeDisplay = CodeDisplayGenerator(self.context)
            codeDisplay.display()
        else:
            dataDisplay = DataDisplayGenerator(self.context)
            dataDisplay.display()

        self.context.cur_start = None
        self.context.cur_end = None

