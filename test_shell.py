from shell import Shell

def test_write_command():
    shell = Shell()
    output = shell.ssd_write("write 3 0xAAAABBBB")
    assert "[Write] Done" in output
    # 내부 data 값이 올바르게 바뀌었는지 직접 체크
    assert shell.data[3] == int("0xAAAABBBB", 16)