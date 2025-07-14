from shell import Shell


def test_read_valid_index(capsys):
    result = Shell.read(3)
    captured = capsys.readouterr()
    assert captured.out.strip() == "[Read] LBA 03 : 0xAAAABBBB"

def test_read_invalid_index(capsys):
    result = Shell.read(99)
    captured = capsys.readouterr()
    assert captured.out.strip() == "[Read] ERROR"