#!/usr/local/bin/python3
# Copyright (c) KMG. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
##

import argparse
import os
import shutil

DUPLIS_BANNER_FILE = os.path.join(os.path.curdir, 'banner.txt')
LDD_FILE = os.path.join(os.path.curdir, 'ldd-cmd')
NM_FILE = os.path.join(os.path.curdir, 'nm-cmd')
TMP_DIR = os.path.join(os.path.curdir, 'scratch', 'tmp')
TMP_FILE = os.path.join(TMP_DIR, 'tmp.txt')
LDD_OUT_FILE = os.path.join(TMP_DIR, 'ldd.txt')
NM_OUT_FILE = os.path.join(TMP_DIR, 'nm.txt')
LIB_NM_OUT_FILE = os.path.join(TMP_DIR, 'nm_lib.txt')
NM_TMP_FILE = os.path.join(TMP_DIR, 'nm_tmp.txt')


def parse_ldd(ldd_cmd, i_file, tmp_file, ldd_out_file, do_print=False):
    if os.path.isfile(i_file) is False:
        print("file " + i_file + " not found!")
        return
    try:
        os.remove(tmp_file)
    except:
        pass
    cmd = ldd_cmd + " " + i_file + " > " + tmp_file
    if do_print:
        print("ldd cmd : " + cmd)
    os.system(cmd)
    file1 = open(tmp_file, 'r')
    file2 = open(ldd_out_file, 'w')

    while True:
        # Get next line from file
        line = file1.readline().strip('\n')

        # if line is empty
        # end of file is reached
        if not line:
            break
        arr = line.split("=>")
        try:
            path = arr[1].split(' (0x')[0].strip()
        except:
            pass
        file2.write(path)
        file2.write('\n')

    file1.close()
    file2.close()
    os.remove(TMP_FILE)


def parse_nm(nm_cmd, grep_word, i_file, tmp_file, nm_out_file, do_print=False):
    if os.path.isfile(i_file) is False:
        print("file " + i_file + " not found!")
        return
    try:
        os.remove(tmp_file)
    except:
        pass
    if grep_word is None or grep_word == "":
        cmd = nm_cmd + " " + i_file + " > " + tmp_file
    else:
        cmd = nm_cmd + " " + i_file + " | grep " + grep_word + " > " + tmp_file
    if do_print:
        print("nm cmd : " + cmd)
    os.system(cmd)
    file1 = open(tmp_file, 'r')
    file2 = open(nm_out_file, 'w')

    while True:
        # Get next line from file
        line = file1.readline().strip('\n')

        # if line is empty
        # end of file is reached
        if not line:
            break
        arr = line.split(' ', 2)
        try:
            sym = arr[2].strip()
        except:
            pass
        file2.write(sym)
        file2.write('\n')

    file1.close()
    file2.close()
    os.remove(tmp_file)


def find_symbol_from_file(symbol, from_file, nm_file, lib_file, out_fd, is_first):
    if os.path.isfile(nm_file) is False:
        print("file " + nm_file + " not found!")
        return False
    file1 = open(nm_file, 'r')
    found = False
    while not found:
        line = file1.readline().strip('\n').strip()
        if not line:
            break
        if symbol.endswith(line):
            if is_first:
                out_fd.write(symbol)
                out_fd.write('\n\t\t')
                out_fd.write(from_file)
                out_fd.write('\n')
            out_fd.write('\t\t')
            out_fd.write(lib_file)
            out_fd.write('\n')
            found = True
    file1.close()
    return found


def find_symbol(symbol, from_file, lib_file, nm_cmd, grep_word, out_fd, is_first):
    if os.path.isfile(lib_file) is False:
        print("file " + lib_file + " not found!")
        return False
    try:
        os.remove(NM_TMP_FILE)
    except:
        pass
    parse_nm(nm_cmd, grep_word, lib_file, TMP_FILE, NM_TMP_FILE)
    if os.path.isfile(NM_TMP_FILE) is False:
        print("file " + NM_TMP_FILE + " not created!")
        return False
    found = find_symbol_from_file(symbol, from_file, NM_TMP_FILE, lib_file, out_fd, is_first)
    os.remove(NM_TMP_FILE)
    return found


def find_duplicate_symbol(symbol, from_file, ldd_file, nm_cmd, grep_word, out_fd):
    if os.path.isfile(ldd_file) is False:
        print("file " + ldd_file + " not found!")
        return
    file1 = open(ldd_file, 'r')
    is_first = True
    while True:
        line = file1.readline().strip('\n').strip()
        if not line:
            break
        ret = find_symbol(symbol, from_file, line, nm_cmd, grep_word, out_fd, is_first)
        if is_first and ret:
            is_first = False
    file1.close()


def duplis():
    parser = argparse.ArgumentParser(description='duplis',
                                     epilog='Please report issues at https://github.com/kmgowda/duplis')
    parser.add_argument('-i', '--ifile', help="Input executable or lib file", required=True)
    parser.add_argument('-l', '--lfile', help="lib file to find the duplicate, if not supplied lib extracted from "
                                              "input file", required=False)
    parser.add_argument('-g', '--grep', help="grep for NM", required=False)
    parser.add_argument('-o', '--ofile', help='Output/Results txt file', default="out.txt")
    args = parser.parse_args()
    print(open(DUPLIS_BANNER_FILE, 'r').read())
    print('Input File : ', args.ifile)
    print('Output File : ', args.ofile)
    print("grep search for NM command: ", args.grep)
    if os.path.isfile(args.ifile) is False:
        print(args.ifile + " not found, exiting!")
        exit(1)
    if args.lfile and os.path.isfile(args.lfile) is False:
        print("The input lib file: " + args.lfile + " not found! exiting")
        exit(1)
    if os.path.isfile(LDD_FILE) is False:
        print(LDD_FILE + " is missing, exiting!")
        exit(1)
    if os.path.isfile(NM_FILE) is False:
        print(NM_FILE + " is missing, exiting!")
        exit(1)

    ldd_cmd = None
    with open(LDD_FILE) as f:
        ldd_cmd = f.readline().strip('\n').strip()
    if not ldd_cmd:
        print("ldd command is missing in " + LDD_FILE + ",  exiting!")
        exit(2)

    nm_cmd = None
    with open(NM_FILE) as f:
        nm_cmd = f.readline().strip('\n').strip()
    if not nm_cmd:
        print("nm command is missing in " + NM_FILE + ",  exiting!")
        exit(2)

    try:
        shutil.rmtree(TMP_DIR)
    except:
        pass
    os.makedirs(TMP_DIR)

    parse_ldd(ldd_cmd, args.ifile, TMP_FILE, LDD_OUT_FILE)
    parse_nm(nm_cmd, args.grep, args.ifile, TMP_FILE, NM_OUT_FILE)

    if os.path.isfile(NM_OUT_FILE) is False:
        print("Count not able to create file" + NM_OUT_FILE + " exiting!")
        exit(4)

    try:
        os.remove(args.ofile)
    except:
        pass
    try:
        os.remove(LIB_NM_OUT_FILE)
    except:
        pass

    if args.lfile:
        parse_nm(nm_cmd, args.grep, args.lfile, TMP_FILE, LIB_NM_OUT_FILE)
        if os.path.isfile(LIB_NM_OUT_FILE) is False:
            print("file " + LIB_NM_OUT_FILE + " not created!")
            exit(4)

    out_fd = open(args.ofile, 'w')

    file1 = open(NM_OUT_FILE, 'r')
    while True:
        symbol = file1.readline().strip('\n').strip()
        if not symbol:
            break
        print("Looking for duplicate symbols for :", symbol)
        if args.lfile:
            find_symbol_from_file(symbol, args.ifile, LIB_NM_OUT_FILE, args.lfile, out_fd, True)
        else:
            find_duplicate_symbol(symbol, args.ifile, LDD_OUT_FILE, nm_cmd, args.grep, out_fd)
    file1.close()
    out_fd.close()


if __name__ == "__main__":
    duplis()
