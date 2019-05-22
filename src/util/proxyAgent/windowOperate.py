import win32gui, win32api, win32con,win32process,psutil
class windowOperate(object):
    @staticmethod
    def click_position(hwd, x_position, y_position):
        long_position = win32api.MAKELONG(x_position, y_position)
        win32api.PostMessage(hwd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, long_position)
        win32api.PostMessage(hwd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, long_position)

    @staticmethod
    def get_handle_by_process_id(pid):
        def callback(hwnd, hwnds):
            if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
                _, nID = win32process.GetWindowThreadProcessId(hwnd)
                if nID == pid:
                    hwnds.append(hwnd)
                return True

        results = []
        win32gui.EnumWindows(callback, results)
        if results:
            return results[0]
        else:
            return None

    @staticmethod
    def getPidByName(Str):
        pidList = []
        for pid in psutil.process_iter():
            if pid.name() == Str:
                pidList.append(pid.pid)
        return pidList

    @staticmethod
    def get_handle_by_process_name(processname):
        pids = windowOperate.getPidByName(processname)
        if pids:
            return windowOperate.get_handle_by_process_id(pids[0])
        else:
            return None