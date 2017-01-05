#!/usr/bin/env python
#
# git-find-lfs-extensions.py [size threshold in KB]
#
# Identify file extensions in a directory tree that could be tracked
# by GitLFS in a repository migration to Git.
#
# Columns explanation:
#   Extension = File extension.
#   LShare    = Percentage of files with the extensions are larger then
#               the threshold.
#   LCount    = Number of files with the extensions are larger then the
#               threshold.
#   Count     = Number of files with the extension in total.
#   Size      = Size of all files with the extension in MB.
#   Min       = Size of the smallest file with the extension in MB.
#   Max       = Size of the largest file with the extension in MB.
#
# Attention this script does only process a directory tree or Git HEAD
# revision. Git history is not taken into account.
#
# Author: Lars Schneider, http://larsxschneider.github.io/
#
import os
import sys

# Threshold that defines a large file
if len(sys.argv):
    THRESHOLD_IN_MB = float(sys.argv[1]) / 1024
else:
    THRESHOLD_IN_MB = 0.5

COLUMN_WIDHT = 60
cwd = os.getcwd()
result = {}

def add_file(ext, size_mb):
    if ext not in result:
        result[ext] = { 'count_large' : 0, 'size_large' : 0, 'count_all' : 0, 'size_all' : 0 }
    result[ext]['count_all'] = result[ext]['count_all'] + 1
    result[ext]['size_all'] = result[ext]['size_all'] + size_mb
    if size_mb > THRESHOLD_IN_MB:
        result[ext]['count_large'] = result[ext]['count_large'] + 1
        result[ext]['size_large'] = result[ext]['size_large'] + size_mb
    if not 'max' in result[ext] or size_mb > result[ext]['max']:
        result[ext]['max'] = size_mb
    if not 'min' in result[ext] or size_mb < result[ext]['min']:
        result[ext]['min'] = size_mb

def print_line(ext, share_large, count_large, count_all, size_all, min, max):
    print ('{}{}{}{}{}{}{}'.format(
        ext.ljust(COLUMN_WIDHT),
        str(share_large).rjust(10),
        str(count_large).rjust(10),
        str(count_all).rjust(10),
        str(size_all).rjust(10),
        str(min).rjust(10),
        str(max).rjust(10)
    ))

for root, dirs, files in os.walk(cwd):
    for basename in files:
        filename = os.path.join(root, basename)
        try:
            size_mb = float(os.path.getsize(filename)) / 1024 / 1024
            if not filename.startswith(os.path.join(cwd, '.git')) and size_mb > 0:
                ext = filename
                add_file('**  all  **', size_mb)
                while ext.find('.') >= 0:
                    ext = ext[ext.find('.')+1:]
                    if ext.find('.') <= 0:
                        add_file(ext, size_mb)
                # files w/o extension
                if filename.find('.') == -1:
                    add_file("no ext" , size_mb)
        except Exception as e:
            print (e)

print_line('Extension', 'LShare', 'LCount', 'Count', 'Size', 'Min', 'Max')
print_line('-------','-------','-------','-------','-------','-------','-------')

for ext in sorted(result.keys(), key=lambda x: result[x]['size_large'], reverse=True):
    if result[ext]['count_large'] > 0:
        large_share = 100*result[ext]['count_large']/result[ext]['count_all']
        print_line(
            ext,
            str(large_share) + ' %' if int(large_share) == large_share else '~ ' + str(round(large_share,2)) + ' %',
            result[ext]['count_large'],
            result[ext]['count_all'],
            int(result[ext]['size_all']),
            int(result[ext]['min']),
            int(result[ext]['max'])
        )
