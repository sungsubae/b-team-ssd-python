import pytest
from pytest_mock import MockerFixture

from shell import Shell, main
from unittest.mock import patch, call

def test_cmd_read(mocker:MockerFixture):
    mk = mocker.Mock(spec=Shell)
    with patch("builtins.input", side_effect=["read 0", "exit"]):
        main(mk)

    mk.read.assert_called_with(0)

def test_cmd_write(mocker:MockerFixture):
    mk = mocker.Mock(spec=Shell)
    with patch("builtins.input", side_effect=["write 3 0xAAAABBBB", "exit"]):
        main(mk)

    mk.write.assert_called_with(3, "0xAAAABBBB")

def test_cmd_fullwrite(mocker:MockerFixture):
    mk = mocker.Mock(spec=Shell)
    with patch("builtins.input", side_effect=["fullwrite", "exit"]):
        main(mk)

    mk.fullwrite.assert_called()

def test_cmd_fullread(mocker:MockerFixture):
    mk = mocker.Mock(spec=Shell)
    with patch("builtins.input", side_effect=["fullread", "exit"]):
        main(mk)

    mk.fullread.assert_called()

def test_cmd_FullWriteAndReadCompare(mocker:MockerFixture):
    mk = mocker.Mock(spec=Shell)
    with patch("builtins.input", side_effect=["1_", "exit"]):
        main(mk)

    with patch("builtins.input", side_effect=["1_FullWriteAndReadCompare", "exit"]):
        main(mk)

    assert mk.FullWriteAndReadCompare.call_count == 2


def test_cmd_PartialLBAWrite(mocker:MockerFixture):
    mk = mocker.Mock(spec=Shell)
    with patch("builtins.input", side_effect=["2_", "exit"]):
        main(mk)
    with patch("builtins.input", side_effect=["2_PartialLBAWrite", "exit"]):
        main(mk)

    assert mk.PartialLBAWrite.call_count == 2

def test_cmd_WriteReadAging(mocker:MockerFixture):
    mk = mocker.Mock(spec=Shell)
    with patch("builtins.input", side_effect=["3_", "exit"]):
        main(mk)
    with patch("builtins.input", side_effect=["3_WriteReadAging", "exit"]):
        main(mk)

    assert mk.WriteReadAging.call_count == 2