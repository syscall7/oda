from odaweb.models import OdaFile

from hachoir_parser import createParser, ParserList
from hachoir_metadata import extractMetadata
from hachoir_core.cmd_line import unicodeFilename

def extract_metadata(uuid):
    oda_file = OdaFile.objects.get(uuid=uuid)
    filename = oda_file.file_handle().name
    #filename, real_filename = unicodeFilename(filename, "utf8"), filename
    parser = createParser(filename, real_filename=filename, tags=None)
    metadata = extractMetadata(parser,1.0)
    return metadata

def mime_type(uuid):
    oda_file = OdaFile.objects.get(uuid=uuid)
    filename = oda_file.file_handle().file.name
    #filename, real_filename = unicodeFilename(filename, "utf8"), filename
    parser = createParser(filename, real_filename=filename, tags=None)
    return parser.mime_type