import os
import re


def find_index(s):
    return(int(re.split('_|\.', s)[1]))


new_index = 1
directory = './test/'

file_list = os.listdir(directory)
file_list = sorted(file_list, key=find_index)

print(file_list)

for filename in file_list:
    if filename.endswith('.jpg'):
        print(filename)
        index = find_index(filename)

        if index % 2 == 0:
            print('removed ', filename)
            os.remove(os.path.join(directory, filename))
        else:
            print('renamed ', filename, ' to ', new_index)
            new_filename = f'gsv_{new_index}.jpg'
            os.rename(
                os.path.join(directory, filename),
                os.path.join(directory, new_filename)
            )
            new_index += 1
    else:
        print('Not an image')
