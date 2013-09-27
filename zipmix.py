#!/usr/bin/env python
import sys, os, mmap, struct

PK12 = 'PK\1\2'
PK34 = 'PK\3\4'
PK56 = 'PK\5\6'
PK78 = 'PK\7\8'

if len(sys.argv) != 4:
    print 'Usage: %s zip1 zip2 out_zip' % sys.argv[0]
    sys.exit()

def import_zip(zip_fn):
    zip_data = {}
    fn_list = []

    buf = mmap.mmap(os.open(zip_fn, os.O_RDONLY), 0, access=mmap.ACCESS_READ)
    end_record = buf.rfind(PK56)
    dir_start = struct.unpack('<i', buf[end_record + 16 : end_record + 20])[0]

    while dir_start < end_record:
        if buf[dir_start : dir_start + 4] != PK12:
            raise "%s signature error" % zip_fn
            
        (create_version, extract_version, flags, compress_method, modify_time, modify_date,
            crc32, compressed_size, uncompressed_size, filename_len, extra_len, commit_len,
            disk_number, internal_attr, external_attr, offset) = struct.unpack('<HHHHHHIIIHHHHHII', buf[dir_start + 4 : dir_start + 46])
        flags &= ~8 # to support apk

        dir_start += 46
        filename = buf[dir_start : dir_start + filename_len]
        dir_start += filename_len
        extra_field = buf[dir_start : dir_start + extra_len]
        dir_start += extra_len
        commit = buf[dir_start : dir_start + commit_len]
        dir_start += commit_len

        if buf[offset : offset + 4] != PK34:
            raise "%s signature error" % zip_fn

        local_filename_len, local_extra_len = struct.unpack('<HH', buf[offset + 26 : offset + 30])
        offset += 30 + local_filename_len
        local_extra_field = buf[offset : offset + local_extra_len]
        offset += local_extra_len
        data = buf[offset : offset + compressed_size]

        if filename not in zip_data:
            zip_data[filename] = (create_version, extract_version, flags, compress_method, modify_time, modify_date,
                                crc32, compressed_size, uncompressed_size, filename_len, 0, commit_len,
                                disk_number, internal_attr, external_attr, '', commit, '', data)
            fn_list.append(filename)
    
    return zip_data, fn_list

zip_data1, fn_list1 = import_zip(sys.argv[1])
zip_data2, fn_list2 = import_zip(sys.argv[2])

zip_out = open(sys.argv[3], 'wb')
central_header = ''
for filename in fn_list1:
    data1 = zip_data1[filename]
    data2 = zip_data2[filename]
    if data1[6] == data2[6] and data1[8] == data2[8] and data1[7] > data2[7]:
        data = data2
    else:
        data = data1
    offset = zip_out.tell()
    zip_out.write(PK34 + struct.pack('<HHHHHIIIH', *data[1:10]) + struct.pack('<H', 0) + filename + data[17])
    zip_out.write(data[18])
    if data[9] != len(filename) or data[10] != len(data[15]) or data[11] != len(data[16]):
        print data[9], len(filename), data[10], len(data[15]), data[11], len(data[16])
    central_header += PK12 + struct.pack('<HHHHHHIIIHHHHHI', *data[:15]) + struct.pack('<I', offset) + filename + data[15] + data[16]

offset = zip_out.tell()
zip_out.write(central_header)
zip_out.write(PK56 + struct.pack('<HHHHIIH', 0, 0, len(fn_list1), len(fn_list1), len(central_header), offset, 0))
