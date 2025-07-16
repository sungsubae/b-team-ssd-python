from buffer import Buffer


def test_buffer_write_and_read():
    buffer = Buffer()
    buffer.make_init_buffer()

    buffer.write('E', 5, size=5)
    assert buffer.read(5) == '0x0x00000000'
    buffer.write('W', 5, '0x0x00000011')
    assert buffer.read(5) == '0x0x00000011'
