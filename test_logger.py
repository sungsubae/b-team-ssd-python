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

    # 6. 로그 내용 확인 (시간은 제외하고 메시지 포함 여부만 확인)
    written_log = handle.write.call_args[0][0]
    assert "Test log message" in written_log
    assert "latest.log" in logger.logfile
