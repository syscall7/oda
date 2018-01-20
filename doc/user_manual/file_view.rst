File View
---------

In File View mode, shown in Figure 5, a user can work on disassembling an
entire uploaded file. ODA supports several types of executable file formats,
including Windows Portable Executable (PE), Executable and Linkable Format
(ELF), Mach Object (Mach-O), Motorola S-record format (SREC), and Intel Hex.
ODA extracts metadata, such as symbols and section headers, from these file
formats and displays the content on the sidebar and tab views. Users can also
upload raw binaries and inform ODA about the target architecture and
architecture-specific options. ODA supports over 60 different instruction set
architectures, including Intel x86 (32-bit and 64-bit), PowerPC, MIPs, ARM,
AVR, Alpha, Sparc, and many others.

ODA supports a variety of methods for navigating large files. The navigation
bar at the top of the display shows code section boundaries and allows users to
drag the position indicator to the desired address. The disassembly content is
updated to reflect the new location. Users can also jump directly to a target
address through the “Go to Address” dialog box, or by clicking on a hyperlink
in the disassembly. Hyperlinks are created for relative code branches as well
as function calls. Additionally, at the top of each function is a list of
hyperlinks showing all the locations from which the function is invoked. Users
can add their own comments to each line of the disassembly listing to document
the intentions and ramifications of the code.
