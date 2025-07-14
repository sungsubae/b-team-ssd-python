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
    
def test_write_command():
    shell = Shell()
    result = shell.write("write 3 0xAAAABBBB")
    assert "[Write] Done" in result
    # 내부 data 값이 올바르게 바뀌었는지 직접 체크
    assert shell.data[3] == int("0xAAAABBBB", 16)
