#!/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2009-2020, Mario Vilas
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice,this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the copyright holder nor the names of its
#       contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import struct

from winappdbg import System, win32

#RegistryEditorVersion = "REGEDIT4"  # for Windows 95
RegistryEditorVersion = "Windows Registry Editor Version 5.00"

# Helper function to serialize data to hexadecimal format.
def reg_hexa(value, type):
    return "hex(%x):%s" % (type, ",".join( ["%.2x" % ord(x) for x in value] ))

# Registry export function.
def reg_export( reg_path, filename ):

    # Queue of registry keys to visit.
    queue = []

    # Get the registry key the user requested.
    key = System.registry[ reg_path ]

    # Add it to the queue.
    queue.append( key )

    # Open the output file.
    with open(filename, "wb") as output:

        # Write the file format header.
        output.write( "%s\r\n" % RegistryEditorVersion )

        # For each registry key in the queue...
        while queue:
            key = queue.pop()

            # Write the key path.
            output.write( "\r\n[%s]\r\n" % key.path )

            # If there's a default value, write it.
            default = str(key)
            if default:
                output.write( "@=\"%s\"\r\n" % default )

            # For each value in the key...
            for name, value in key.iteritems():

                # Skip the default value since we already wrote it.
                if not name:
                    continue

                # Serialize the name.
                s_name = "\"%s\"" % name

                # Serialize the value.
                t_value = key.get_value_type(name)
                if t_value == win32.REG_SZ and type(value) == str:
                    s_value = "\"%s\"" % value.replace("\"", "\\\"")
                elif t_value == win32.REG_DWORD:
                    s_value = "dword:%.8X" % value
                else:
                    if t_value == win32.REG_QWORD:
                        value = struct.pack("<Q", value)
                    elif t_value == win32.REG_DWORD:
                        value = struct.pack("<L", value)
                    elif t_value == win32.REG_DWORD_BIG_ENDIAN:
                        value = struct.pack(">L", value)
                    elif t_value == win32.REG_MULTI_SZ:
                        if not value:
                            value = ""
                        elif type(value) == str:
                            value = "\0".join(value)
                        else:
                            value = u"\0".join(value)
                    if type(value) == str:
                        s_value = reg_hexa(value, t_value)
                    else:
                        s_value = reg_hexa(value.encode("UTF-16"), t_value)

                # Write the name and value.
                output.write( "%s=%s\r\n" % (s_name, s_value) )

# When invoked from the command line,
# the first argument is a registry key to read from,
# the second argument is a filename to write to.
if __name__ == "__main__":
    import sys
    reg_path = sys.argv[1]
    filename = sys.argv[2]
    reg_export( reg_path, filename )
