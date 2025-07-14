from shell import Shell

def test_read_valid_index(capsys):
    shell = Shell()
    result = shell.read(3)
    captured = capsys.readouterr()
    assert captured.out.strip() == "[Read] LBA 03 : 0xAAAABBBB"

def test_read_invalid_index(capsys):
    shell = Shell()
    result = shell.read(100)
    captured = capsys.readouterr()
    assert captured.out.strip() == "[Read] ERROR"