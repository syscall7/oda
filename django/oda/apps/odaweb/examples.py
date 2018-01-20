Examples = (
    {
        'project_name': 'strcpy (x86)',
        'short_name': 'strcpy_x86',
        'data': '55 31 D2 89 E5 8B 45 08 56 8B 75 0C 53 8D 58 FF 0F B6 0C 16 88 4C 13 01 83 C2 01 84 C9 75 F1 5B 5E 5D C3 ',
        'options': {'target': "binary", 'architecture': "i386"},
        'comments': (
            (0x00, "press the ';' button to make a comment"),
            (0x01, "you can also click the right mouse button to get a context menu"),
            (0x09, 'char* src = arg[1]'),
            (0x0d, 'char* dst = arg[0]'),
            (0x10, 'char c = src[i]'),
            (0x14, 'dst[i] = c'),
            (0x18, 'i++'),
            (0x1b, 'while (c != 0)'),
        ),
        'labels': (
            (0x10, 'loop'),
        )
    },
    {
        'project_name': 'strcpy (arm)',
        'short_name': 'strcpy_arm',
        'data': '01 20 40 E2 02 20 61 E0 01 30 D1 E4 00 00 53 E3 02 30 C1 E7 FB FF FF 1A 1E FF 2F E1',
        'options': {'target': "binary", 'architecture': "arm"},
    },
    {
        'project_name': 'whoami (Linux)',
        'short_name': 'whoami',
        'file_name': 'whoami',
        'options': {'target': "elf64-x86-64", 'architecture': "i386:x86-64"},
    },
    {
        'project_name': 'mkdir (Linux)',
        'short_name': 'mkdir',
        'binary_type': 'file',
        'file_name': 'mkdir',
        'options': {'target': "elf64-x86-64", 'architecture': "i386:x86-64"},
    },
    {
        'project_name': 'cat (Linux)',
        'short_name': 'cat',
        'file_name': 'cat',
        'options': {'target': "elf64-x86-64", 'architecture': "i386:x86-64"},
    },
    {
        'project_name': 'chown (Linux)',
        'short_name': 'chown',
        'file_name': 'chown',
        'options': {'target': "elf64-x86-64", 'architecture': "i386:x86-64"},
    },
    #{
    #    'project_name': 'mongodb',
    #    'short_name': 'mongodb',
    #    'file_name': 'mongod',
    #    'options': {'target': "elf64-x86-64", 'architecture': "i386:x86-64"},
    #},

    #{
    #    'project_name' : 'Sasser Worm (Windows)',
    #    'short_name' : 'sasser',
    #    'binary_type' : 'file',
    #    'file_name' : 'net-worm.win32.sasser.a',
    #    'options' : OdaOptions(target="elf32-i386", architecture="i386"),
    #    },
)
