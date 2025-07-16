import os
from datetime import datetime
import inspect

FILE_MAX_SIZE = 10 * 1024  # 10KB

class Logger:
    def __init__(self, logfile='latest.log'):

        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.log_dir = current_dir
        self.logfile = os.path.join(current_dir, logfile)

    def roatate_file_if_needed(self):
        if os.path.exists(self.logfile) and os.path.getsize(self.logfile) > FILE_MAX_SIZE:
            timestamp = datetime.now().strftime("%y%m%d_%Hh_%Mm_%Ss")
            rotated_name = f"until_{timestamp}.log"
            rotated_path = os.path.join(self.log_dir, rotated_name)

            os.rename(self.logfile, rotated_path)

            self.change_file_extension_with_zip()

    def change_file_extension_with_zip(self):
        files=[]
        for file in os.listdir(self.log_dir):
            if file.startswith("until_") and file.endswith(".log"):
                files.append(file)

        if len(files) >= 2:
            files.sort(key=lambda filename: datetime.strptime(
                filename[len("until_"):-len(".log")], "%y%m%d_%Hh_%Mm_%Ss"))

            oldest_log = files[0]
            old_path = os.path.join(self.log_dir, oldest_log)
            new_path = old_path.replace(".log", ".zip")
            os.rename(old_path, new_path)

    def print(self, message: str):
        self.roatate_file_if_needed()

        now = datetime.now().strftime("[%y.%m.%d %H:%M]")

        frame = inspect.currentframe()
        outer_frames = inspect.getouterframes(frame)
        function_name = outer_frames[1].function
        class_name = self._get_caller_class_name(outer_frames)

        location = f"{class_name}.{function_name}()"
        log_line = f"{now} {location.ljust(35)}: {message}"

        with open(self.logfile, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')

    def _get_caller_class_name(self, outer_frames):
        try:
            caller_locals = outer_frames[1].frame.f_locals
            if 'self' in caller_locals:
                return caller_locals['self'].__class__.__name__
            else:
                return 'UnknownClass'
        except Exception:
            return 'UnknownClass'
