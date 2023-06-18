import sys
import os
import tarfile
import gzip
import shutil
from pathlib import Path



def sorting_main_func(main_path):

    CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ "
    TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
                "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g" " ")
    NUMBERS = '1234567890'

    TRANS = {}
    for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
        TRANS[ord(c)] = l
        TRANS[ord(c.upper())] = l.upper()

    def normalize(file):
        no_type_name = file.name.removesuffix(file.suffix)
        no_type_name = no_type_name.translate(TRANS)

        for symb in no_type_name:
            if not (ord('a') <= ord(symb) <= ord('z') or ord('A') <= ord(symb) <= ord('Z') or symb in NUMBERS):
                no_type_name = no_type_name.replace(symb, '_')

        name_parts = (no_type_name, file.suffix)
        normalized_name = ''.join(name_parts)
        return normalized_name


    def dir_path_creation(type):
        dir_path = Path(os.path.join(main_path, type))
        return dir_path

    def file_delivering(item, type):
        if dir_path_creation(type).exists() == False:
            os.mkdir(dir_path_creation(type))
        if (dir_path_creation(type)/item.name).exists() == False:
            file_moving = shutil.move(item, dir_path_creation(type))
            return file_moving

    sorted_files_dict = {'images': [], 'videos': [], 'documents': [], 'music': [], 'archives': [], 'unknown': []}
    known_file_types_list = []
    unknown_file_types_list = []

    def sorting_file_names_and_types(item, type):
        sorted_files_dict[type].append(item.name)
        if not item.suffix in known_file_types_list:
            known_file_types_list.append(item.suffix)


    def sorting(folder_path):
        for item in folder_path.iterdir():
            if not item.name in ['images', 'videos', 'documents', 'music', 'archives', 'unknown']:
                if item.is_dir():
                    sorting(item)

                if item.is_file():
                    if item.suffix.removeprefix('.').upper() in ['JPEG', 'PNG', 'JPG', 'SVG']:
                        type = 'images'
                        if file_delivering(item, type):
                            file_delivering(item, type)
                            sorting_file_names_and_types(item, type)
                        else:
                            os.remove(item)
                            continue
                        
                    elif item.suffix.removeprefix('.').upper() in ['AVI', 'MP4', 'MOV', 'MKV']:
                        type = 'videos'
                        if file_delivering(item, type):
                            file_delivering(item, type)
                            sorting_file_names_and_types(item, type)
                        else:
                            os.remove(item)
                            continue
                        
                    elif item.suffix.removeprefix('.').upper() in ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX']:
                        type = 'documents'
                        if file_delivering(item, type):
                            file_delivering(item, type)
                            sorting_file_names_and_types(item, type)
                        else:
                            os.remove(item)
                            continue

                    elif item.suffix.removeprefix('.').upper() in ['MP3', 'OGG', 'WAV', 'AMR']:
                        type = 'music'
                        if file_delivering(item, type):
                            file_delivering(item, type)
                            sorting_file_names_and_types(item, type)
                        else:
                            os.remove(item)
                            continue
                    
                    elif item.suffix.removeprefix('.').upper() in ['ZIP', 'GZ', 'TAR']:
                        type = 'archives'
                        if file_delivering(item, type):
                            file_delivering(item, type)
                            sorting_file_names_and_types(item, type)
                        else:
                            os.remove(item)
                            continue
                
                    else:
                        type = 'unknown'
                        if file_delivering(item, type):
                            file_delivering(item, type)
                            sorted_files_dict['unknown'].append(item.name)
                            if not item.suffix in unknown_file_types_list:
                                unknown_file_types_list.append(item.suffix)
                        else:
                            os.remove(item)
                            continue
                        
                
                if item.is_dir():
                    os.rmdir(item)
    sorting(main_path)


    if (main_path/'archives').is_dir():
        def archive_unpacking(folder_path):
            archives_folder = folder_path / 'archives'
            for arch in os.listdir(archives_folder):
                arch_path = archives_folder / arch
                if arch_path.is_file():
                    output_folder = arch_path.with_suffix('')
                    if arch_path.suffix == '.gz':
                        with gzip.open(arch_path, 'rb') as gz_file:
                            with tarfile.open(fileobj=gz_file, mode='r') as tar:
                                tar.extractall(path=output_folder)
                    elif arch_path.suffix == '.tar':
                        with tarfile.open(arch_path, 'r') as tar:
                            tar.extractall(path=output_folder)
                    elif arch_path.suffix == '.zip':
                        shutil.unpack_archive(str(arch_path), str(output_folder))
        archive_unpacking(main_path)

        def archive_deleting(folder_path):
            for item in folder_path.iterdir():
                if item.is_file():
                    os.remove(item)
        archive_deleting(dir_path_creation('archives'))


    def renaming(folder_path):
        for folder in folder_path.iterdir():
            if folder.name in ['images', 'videos', 'documents', 'music', 'archives']:
                for item in folder.iterdir():
                    try:
                        os.rename(item, Path(os.path.join(item.parent, normalize(item))))
                    except Exception:
                        if item.is_dir():
                            shutil.rmtree(item)
                        else:
                            os.remove(item)
    renaming(main_path)


    def value_check(dict_given):
        result = []
        for key, value in dict_given.items():
            if value:
                x = [str(key), str(value)]
                mid_res = ': '.join(x)
                result.append(mid_res)
        return result


    if value_check(sorted_files_dict):
        print('У результаті було відсортовано такі файли:')
        for res in value_check(sorted_files_dict):
            print(res)
        print('')
    else:
        print('Жоден файл не було відсотровано!\n')

    if known_file_types_list: 
        print(f'Скрипту були відомі файли з такими розширеннями:\n{known_file_types_list}\n')
    if unknown_file_types_list:
        print(f'Скрипту не були відомі файли з такими розширеннями:\n{unknown_file_types_list}')

def args_check_func():        
    try:
        sorting_main_func(Path(sys.argv[1]))
    except IndexError:
        print('Помилка! Ви не надали шлях!')