import os
from datetime import datetime
import inspect

class Logger:
    def __init__(self, logfile='latest.log'):

        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.logfile = os.path.join(current_dir, logfile)

    def print(self, message: str):
        now = datetime.now().strftime("[%y.%m.%d %H:%M]")


        frame = inspect.currentframe()
        outer_frames = inspect.getouterframes(frame)
        function_name = outer_frames[1].function
        class_name = self._get_caller_class_name(outer_frames)

        log_line = f"{now} {class_name}.{function_name}()".ljust(40) + f": {message}"

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
