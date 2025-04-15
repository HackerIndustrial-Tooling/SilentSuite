# TCC DB Viewer 

Parse and dump the Transparency, Consent, and Control (TCC) database


## sideloading the script 

You can't access the sqlite db that holds TCC unless you have FDA (Full Disk Access) permission. You either SE or use a program that has access. 
The sideloader.c binary is a dylib that can be used on vulnerable binaries to sideload the script. 

either 
clang -dynamiclib -o sideload.dylib sideload.c
or 
// compile with gcc -dynamiclib inject.c -o inject.dylib
//gcc -mmacosx-version-min=12.3 -dynamiclib inject.c -o inject.dylib
// clang -shared -undefined dynamic_lookup -o inject.dylib inject.c
execute like:
DYLD_INSERT_LIBRARIES=./sideload.dylib /usr/bin/env
DYLD_INSERT_LIBRARIES=./sideload.dylib /usr/bin/python3



check if program is vulnerable to DYLD Injection
codesign -dvv /path/to/binary 

look for 
CodeDirectory v=20500 size=8614 flags=0x10000(runtime)

The 0x10000(runtime) flag indicates that the binary is signed with the Hardened Runtime, which disables environment variable injection, including:

   - DYLD_INSERT_LIBRARIES
   - DYLD_PRINT_*
   - DYLD_FORCE_FLAT_NAMESPACE





