import os

from buffer import Buffer


def test_buffer_write_and_read():
    buffer = Buffer()
    buffer.make_init_buffer()

    buffer.write('E', 5, size=5)
    assert buffer.read(5) == '0x00000000'
    buffer.write('W', 5, '0x00000011')
    assert buffer.read(5) == '0x00000011'


def get_empty_buffer_cnt(file_list):
    empty_cnt = 0

    for file_name in file_list:
        if 'empty' in file_name:
            empty_cnt += 1

    return empty_cnt

def test_buffer_write_join_command():
    buffer = Buffer()
    buffer.make_init_buffer()

    buffer.write('E', 5, size=5)
    buffer.write('E', 7, size=5)
    buffer.write('E', 9, size=5)

    file_list = os.listdir(Buffer().folder_path)

    assert get_empty_buffer_cnt(file_list) == len(file_list) - 1

def test_buffer_write_not_join_erase_command():
    buffer = Buffer()
    buffer.make_init_buffer()

    buffer.write('E', 5, size=5)
    buffer.write('E', 10, size=6)

    file_list = os.listdir(Buffer().folder_path)

    assert get_empty_buffer_cnt(file_list) == len(file_list) - 2