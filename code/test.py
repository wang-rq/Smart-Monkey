import datetime
import os
import random
import time
from multiprocessing import Pool
from typing import Dict, Union
import adbfunc
import config
from adbfunc import AndroidDebugBridge

adb = adbfunc.AndroidDebugBridge()
monkeyConfig = config.MonkeyConfig()

# 检测设备
def runnerPool():
    devices_Pool = []
    devices = adb.attached_devices()
    if devices:
        for item in range(0, len(devices)):
            _app: Dict[str, Union[str, int]] = {"devices": devices[item], "num": len(devices)}
            devices_Pool.append(_app)
        pool = Pool(len(devices))
        pool.map(start, devices_Pool)
        pool.close()
        pool.join()
    else:
        print("未检测到连接的设备")


def start(devices):
    device = devices["devices"]
    deviceNum = devices["num"]
    print(f"start device {device};num {deviceNum}")

    # 启动初始activity
    adb.open_app(monkeyConfig.package_name, monkeyConfig.activity[0], device)

    # log文件夹，存放每次test的结果日志
    logDir = os.path.join("log", f"{datetime.datetime.now().strftime('%Y%m%d_%p_%H%M%S')}")
    os.makedirs(logDir)
    adbLogFileName = os.path.join(logDir, "logcat.log")
    monkeyLogFile = os.path.join(logDir, "monkey.log")
    monkeyConfig.monkeyCmd = f"adb -s {device} shell {monkeyConfig.monkeyCmd + monkeyLogFile}"

    # 开始测试
    start_monkey(monkeyConfig.monkeyCmd, logDir)

    start_activity_time = time.time()
    while True:
        # 判断测试的app的module是否在top
        if AndroidDebugBridge().if_top(monkeyConfig.package_name,
                                        monkeyConfig.module_key) is False:
            # 打开第一个设置好的activity（微博主界面）
            adb.open_app(monkeyConfig.package_name, monkeyConfig.activity[0], device)

        current_activity = AndroidDebugBridge().current_activity()
        time.sleep(2)

        # 判断测试时是否有在一个界面卡死的现象，设置时间范围为 10
        if AndroidDebugBridge().if_dead_lock(start_activity_time, current_activity, 10):
            adb.open_app(monkeyConfig.package_name, random.choice(monkeyConfig.activity), device)
            start_activity_time = time.time()

        # 判断是否结束
        with open(monkeyLogFile, "r", encoding='utf-8') as monkeyLog:
            if monkeyLog.read().count('Monkey finished') > 0:
                print(f"{device}\n测试结束")
                break

    # 给 crash 计数并输出
    with open(adbLogFileName, "r", encoding='utf-8') as logfile:
        print(
            f"{device}\n存在{logfile.read().count('FATAL EXCEPTION')}个crash!"
            f"请查看{adbLogFileName}文件")


# 开始monkey测试
def start_monkey(monkeyCmd, logDir):
    os.popen(monkeyCmd)
    print(f"start_monkey {monkeyCmd}")

    # logcat文件中存入Monkey时的手机日志
    logFileName = os.path.join(logDir, "logcat.log")
    cmd2 = f"adb logcat -d >{logFileName}"
    os.popen(cmd2)

    # 导出traces文件 用于分析ANR
    traceFilename = os.path.join(logDir, "anr_traces.log")
    cmd3 = f"adb shell cat /data/anr/traces.txt>{traceFilename}"
    os.popen(cmd3)


def begin():
    os.popen("adb kill-server")
    os.popen("adb start-server")
    os.popen("adb root")


if __name__ == '__main__':
    begin()
    time.sleep(1)
    runnerPool()
