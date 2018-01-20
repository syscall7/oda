import sys
import os
from ctypes import *
from ctypes.wintypes import HWND, LPCSTR, UINT, ULONG, HANDLE, BYTE, DWORD, BOOLEAN

WORD      = c_ushort
PVOID     = c_void_p
LPVOID    = c_void_p
PULONG    = POINTER(c_ulong)
SHORT     = c_short
ULONG_PTR = POINTER(c_ulong)
ULONG_PTR = POINTER(c_ulong)
SIZE_T    = c_ulong

PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400

MEM_COMMIT                = 0x00001000
MEM_RESERVE               = 0x00002000
MEM_DECOMMIT              = 0x00004000
MEM_RELEASE               = 0x00008000
MEM_RESET                 = 0x00080000

MEM_IMAGE                 = 0x01000000
MEM_MAPPED                = 0x00040000
MEM_PRIVATE               = 0x00020000


class MEMORY_BASIC_INFORMATION(Structure):
    _fields_ = [
        ("BaseAddress", PVOID),
        ("AllocationBase", PVOID),
        ("AllocationProtect", DWORD),
        ("RegionSize", SIZE_T),
        ("State", DWORD),
        ("Protect", DWORD),
        ("Type", DWORD),
    ]

class PROC_STRUCT(Structure):
    _fields_ = [
        ("wProcessorArchitecture", WORD),
        ("wReserved", WORD),
    ]

class SYSTEM_INFO_UNION(Union):
    _fields_ = [
        ("dwOemId", DWORD),
        ("sProcStruc", PROC_STRUCT),
    ]

class SYSTEM_INFO(Structure):
    _fields_ = [
        ("uSysInfo", SYSTEM_INFO_UNION),
        ("dwPageSize", DWORD),
        ("lpMinimumApplicationAddress", LPVOID),
        ("lpMaximumApplicationAddress", LPVOID),
        ("dwActiveProcessorMask", DWORD),
        ("dwNumberOfProcessors", DWORD),
        ("dwProcessorType", DWORD),
        ("dwAllocationGranularity", DWORD),
        ("wProcessorLevel", WORD),
        ("wProcessorRevision", WORD),
    ]

class UNICODE_STRING(Structure):
    _fields_ = [("Length", c_ushort),
                ("MaximumLength", c_ushort),
                ("Buffer", ULONG)]  # not sure why I can't use c_wchar_p here

class LIST_ENTRY(Structure):
    _fields_ = [
        ("Flink",               ULONG),
        ("Blink",               ULONG),
    ]

class LDR_MODULE(Structure):
    _fields_ = [
        ("InLoadOrderModuleList",  LIST_ENTRY),
        ("InMemoryOrderModuleList",  LIST_ENTRY),
        ("InInitializationOrderModuleList",  LIST_ENTRY),
        ("BaseAddress",  ULONG),
        ("EntryPoint",  ULONG),
        ("SizeOfImage",  ULONG),
        ("FullDllName",  UNICODE_STRING),
        ("BaseDllName",  UNICODE_STRING),
        ("Flags",  ULONG),
        ("LoadCount",  SHORT),
        ("TlsIndex",  SHORT),
        ("HashTableEntry",  LIST_ENTRY),
        ("TimeDateStamp",  ULONG),
    ]

class PEB_LDR_DATA(Structure):
    _fields_ = [
        ("Length", ULONG),
        ("Initialized", BOOLEAN),
        ("SsHandle", PVOID),
        ("InLoadOrderModuleList", LIST_ENTRY),
        ("InMemoryOrderModuleList", LIST_ENTRY),
        ("InInitializationOrderModuleList", LIST_ENTRY),
    ]

class PEB(Structure):
    _fields_ = [
        ("Reserved1",                BYTE*2),
        ("BeingDebugged",            BYTE),
        ("Reserved2",                BYTE),
        ("Reserved3",                PVOID*2),
        ("Ldr",                      ULONG), # POINTER(PEB_LDR_DATA)),
        ("ProcessParameters",        PVOID), # PRTL_USER_PROCESS_PARAMETERS),
        ("Reserved4",                BYTE*104),
        ("Reserved5",                PVOID*52),
        ("PostProcessInitRoutine",   PVOID), # PPS_POST_PROCESS_INIT_ROUTINE),
        ("Reserved6",                BYTE*128),
        ("Reserved7",                PVOID),
        ("SessionId",                ULONG),
    ]

class PROCESS_BASIC_INFORMATION(Structure):
    _fields_ = [
        ("Reserved1",       PVOID),
        ("PebBaseAddress",  HANDLE),
        ("Reserved2",       PVOID*2),
        ("UniqueProcessId", ULONG_PTR),
        ("Reserved4",       PVOID),
    ]



class Module(object):
    def __init__(self, name, path, addr, size):
        self.name = name
        self.path = path
        self.addr = addr
        self.size = size

class ModuleList(list):
    def contains_range(self, addr, size):
        for module in self:
            if (addr >= module.addr) and (addr+size <= module.addr+module.size):
                return True

class LimeDump():

    class LimeHeader(Structure):

        def __init__(self, addr=0, buf=''):
            LIME_MAGIC = 0x4c694d45
            LIME_VERSION = 1
            super(self.__class__, self).__init__(LIME_MAGIC, LIME_VERSION, addr, addr + len(buf) - 1, 0)

        _fields_ = [('magic', c_uint),
                    ('version', c_uint),
                    ('start', c_ulonglong),
                    ('end', c_ulonglong),
                    ('reserved', c_ulong)]

    def __init__(self):
        # store everything internally as a dictionary
        self.mmap = {}

    def add(self, addr, buf):
        # check if this chunk can be appended to an existing chunk
        for (a,b) in self.mmap.iteritems():
            # if this chunk is contiguous
            if (addr == (a + len(b))):
                self.mmap[a] += buf
                return
        self.mmap[addr] = buf

    def write(self, sock):
        for (addr, buf) in self.mmap.iteritems():
            hdr = LimeDump.LimeHeader(addr, buf)
            sock.sendall(hdr)
            sock.sendall(buf)


KERNEL32 = windll.kernel32

class ProcDump(object):

    def __init__(self, pid):
        # open the process
        self.hProcess = KERNEL32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid);
        if (self.hProcess == 0):
            raise Exception("Failed to open process %d" % pid)
        self.modules = ModuleList()

    def get_system_info(self):
        """Get system information."""
        self.system_info = SYSTEM_INFO()
        KERNEL32.GetSystemInfo(byref(self.system_info))

    def read_mem(self, address, buf):
        if not KERNEL32.ReadProcessMemory(self.hProcess, address, byref(buf), sizeof(buf), None):
           raise Exception("Failed to read memory at address 0x%x" % address)

    def add_module(self, module):
        print 'Module ', module
        print '  Load Order Flink: 0x%08x' % module.InLoadOrderModuleList.Flink
        print '  Load Order Blink: 0x%08x' % module.InLoadOrderModuleList.Blink
        print '  Memory Order Flink: 0x%08x' % module.InMemoryOrderModuleList.Flink
        print '  Memory Order Blink: 0x%08x' % module.InMemoryOrderModuleList.Blink
        print '  Init Order Flink: 0x%08x' % module.InInitializationOrderModuleList.Flink
        print '  Init Order Blink: 0x%08x' % module.InInitializationOrderModuleList.Blink
        print '  Base Address: 0x%08x' % module.BaseAddress
        print '  Entry Point: 0x%08x' % module.EntryPoint
        print '  Size of Image: 0x%08x' % module.SizeOfImage

        buf = create_unicode_buffer(1024)
        self.read_mem(module.FullDllName.Buffer, buf)
        path = wstring_at(buf[0:module.FullDllName.Length/2])
        print '  Full Module name length is %d' % (module.FullDllName.Length/2)
        print '  Full Module name is at 0x%08x' % module.FullDllName.Buffer
        print '  Full Module name is %s' % path

        buf = create_unicode_buffer(1024)
        self.read_mem(module.BaseDllName.Buffer, buf)
        name = wstring_at(buf[0:module.FullDllName.Length/2])
        print '  Base Module name length is %d' % (module.BaseDllName.Length/2)
        print '  Base Module name is at 0x%08x' % module.BaseDllName.Buffer
        print '  Base Module name is %s' % name
        print ''

        m = Module(name, path, module.BaseAddress, module.SizeOfImage)
        self.modules.append(m)

    def find_modules(self):

        # get process information
        prototype = WINFUNCTYPE(c_int, HANDLE, c_int, PVOID, ULONG, PULONG)
        paramflags = (1, "procHnd", 0), (1, "procInfoClass", 0), (1, "procInfo", None), (1, "procInfoLen", 0), (1, "retLen", None)
        NtQueryInformationProcess = prototype(("NtQueryInformationProcess", windll.ntdll), paramflags)
        pbi = PROCESS_BASIC_INFORMATION()
        err = NtQueryInformationProcess(self.hProcess, 0, byref(pbi), sizeof(pbi), None)
        if (err != 0):
            raise Exception("NtQueryInformationProcess failed")

        print "PEB is at 0x%x\n" % pbi.PebBaseAddress

        peb = PEB()
        self.read_mem(pbi.PebBaseAddress, peb)
        print 'Ldr is at 0x%08x' % peb.Ldr

        ldr = PEB_LDR_DATA()
        self.read_mem(peb.Ldr, ldr)

        print 'PEB_LDR_DATA - Length: %d' % ldr.Length
        print 'PEB_LDR_DATA - Initialized: %s' % ldr.Initialized
        print 'PEB_LDR_DATA - SsHandle: %s' % ldr.SsHandle
        print 'PEB_LDR_DATA - Load Order Flink: 0x%08x' % ldr.InLoadOrderModuleList.Flink
        print 'PEB_LDR_DATA - Load Order Blink: 0x%08x' % ldr.InLoadOrderModuleList.Blink
        print 'PEB_LDR_DATA - Memory Order Flink: 0x%08x' % ldr.InMemoryOrderModuleList.Flink
        print 'PEB_LDR_DATA - Memory Order Blink: 0x%08x' % ldr.InMemoryOrderModuleList.Blink
        print 'PEB_LDR_DATA - Init Order Flink: 0x%08x' % ldr.InInitializationOrderModuleList.Flink
        print 'PEB_LDR_DATA - Init Order Blink: 0x%08x' % ldr.InInitializationOrderModuleList.Blink


        # read the first module
        start = ldr.InLoadOrderModuleList.Flink

        lm = LDR_MODULE()
        self.read_mem(ldr.InMemoryOrderModuleList.Flink - sizeof(LIST_ENTRY), lm)

        cnt = 0
        while lm.InLoadOrderModuleList.Flink != start:
            print cnt
            cnt += 1
            self.add_module(lm)

            # read next module
            self.read_mem(lm.InMemoryOrderModuleList.Flink - sizeof(LIST_ENTRY), lm)

    def dump_memory(self, sock, include_dlls=False):

        limeDump = LimeDump()
        self.find_modules()

        for module in self.modules:
            buf = create_string_buffer(module.size)
            count = c_ulong(0)
            if KERNEL32.ReadProcessMemory(self.hProcess,
                                          module.addr,
                                          buf,
                                          module.size,
                                          byref(count)):
                print "Dumping 0x%x bytes at 0x%x" % (module.size, module.addr)
                limeDump.add(module.addr, buf.raw)
            
            # if we do not want all the loaded DLLs, bail
            if not include_dlls:
                break

        limeDump.write(sock)

if __name__ == '__main__':
    class NullSocket(object):
        def sendall(self, buf):
            print "Sending %d bytes to null socket" % len(str(buf))

    pdump = ProcDump(int(sys.argv[1]))
    pdump.dump_memory(NullSocket())
