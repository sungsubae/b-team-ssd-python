import os

from pytest_mock import MockerFixture
from logger import Logger
from datetime import datetime

def test_print_writes_to_latest_log(mocker:MockerFixture):
    mocker.patch("os.path.exists", return_value=False)
    mocker.patch("os.path.getsize", return_value=0)

    mocked_file = mocker.mock_open()
    mocker.patch("builtins.open", mocked_file)

    logger = Logger()
    logger.print("Test log message")

    mocked_file.assert_called_once_with(logger.logfile, 'a', encoding='utf-8')

    handle = mocked_file()
    handle.write.assert_called_once()

    written_log = handle.write.call_args[0][0]

    assert "Test log message" in written_log
    assert "latest.log" in logger.logfile


def test_create_until_file(mocker:MockerFixture):
    # latest.log exist and size is 11KB
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("os.path.getsize", return_value=11 * 1024)

    fixed_now = datetime(2025, 7, 16, 10, 10, 10)
    mocker.patch("logger.datetime", wraps=datetime)
    mocker.patch("logger.datetime.now", return_value=fixed_now)

    mock_rename = mocker.patch("os.rename")
    mocker.patch.object(Logger, "change_file_extension_with_zip")

    logger = Logger()
    logger.create_until_file()

    current_dir = os.path.dirname(os.path.abspath(__file__))
    expected_log_file = os.path.join(current_dir, 'latest.log')
    expected_until_log_file = os.path.join(current_dir, fixed_now.strftime("until_%y%m%d_%Hh_%Mm_%Ss.log"))
    mock_rename.assert_called_once_with(expected_log_file, expected_until_log_file)

def test_change_file_extension_with_zip(mocker:MockerFixture):
    # latest.log exist and size is 11KB
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("os.path.getsize", return_value=11 * 1024)

    # fix datetime.now()
    fixed_now = datetime(2025, 7, 16, 10, 10, 10)
    mocker.patch("logger.datetime", wraps=datetime)
    mocker.patch("logger.datetime.now", return_value=fixed_now)

    mock_rename = mocker.patch("os.rename")
    mocker.patch("os.listdir", return_value=[
        "until_250710_09h_00m_00s.log",
        "until_250713_09h_00m_00s.log"
    ])

    logger = Logger()
    logger.create_until_file()

    current_dir = os.path.dirname(os.path.abspath(__file__))

    expected_log_file = os.path.join(current_dir, 'latest.log')
    expected_until_log_file = os.path.join(current_dir, fixed_now.strftime("until_%y%m%d_%Hh_%Mm_%Ss.log"))

    expected_zip_src_file = os.path.join(current_dir, "until_250710_09h_00m_00s.log")  # 더 오래된 파일
    expected_zip_dst_file = os.path.join(current_dir, "until_250710_09h_00m_00s.zip")

    assert mock_rename.call_count == 2
    mock_rename.assert_any_call(expected_log_file, expected_until_log_file)
    mock_rename.assert_any_call( expected_zip_src_file, expected_zip_dst_file)