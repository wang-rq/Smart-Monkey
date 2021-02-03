import os
import platform
import time

class AndroidDebugBridge(object):
    @staticmethod
    # 执行命令
    def call_adb(command): 
        command_result = ''
        command_text = f'adb {command}'
        print("执行命令：" + command_text)
        results = os.popen(command_text, "r")
        while 1:
            line = results.readline()
            if not line:
                break
            command_result += line
        results.close()
        return command_result

    # 连接设备检查
    def attached_devices(self):
        result = self.call_adb("devices")
        devices = result.partition('\n')[2].replace('\n', '').split('\tdevice')
        return [device for device in devices if len(device) > 2]

    # 打开指定app
    def open_app(self, packageName, activity, devices):
        result = self.call_adb(
            f"-s {devices} shell am start -n {packageName}/{activity}")
        check = result.partition('\n')[2].replace('\n', '').split('\t ')
        if check[0].find("Error") >= 1:
            return False
        else:
            return True

    # 判断测试app是否在某个界面
    def if_top(self, pkg_name, moduleKey):
        result = self.current_activity()
        if result == '':
            return "the process doesn't exist."
        print(result)
        if (pkg_name in result and moduleKey in result and "leakcanary" not in result) or "WkBrowserActivity" in result or "CordovaWebActivity" in result:
            return True
        else:
            return False

    def current_activity(self):
        result = self.call_adb("shell dumpsys activity | findstr mResumedActivity")
        return result

    # 判断是否测试中app在某个界面停留时间过久
    def if_dead_lock(self, start_time, current_activity, max_time):
        while current_activity == self.current_activity():
            end_time = time.time()
            print(f"同一页面停留时间: {(end_time - start_time)}")
            if end_time - start_time > max_time:
                print("超过限定时间：随机打开设定的activity")
                return True
            else:
                return False
        else:
            return False
            