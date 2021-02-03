class MonkeyConfig(object):
    # 测试的app包名
    package_name = "com.sina.weibo"
    # 测试app中模块的关键词
    module_key = "com.sina.weibo"
    # 设置当测试app卡死时，要自动跳回到随机一个下列界面
    activity = [".MainTabActivity",
                ".page.SearchResultActivity",
                ".feed.DetailWeiboActivity",
                ".page.NewCardListActivity",
                ".photoalbum.imageviewer.ImageViewer",
                ]
    # monkey 命令
    monkeyCmd = f"monkey -p {package_name} --throttle 300  " \
                "--pct-appswitch 5 --pct-touch 30 --pct-motion 60 --pct-anyevent 5  " \
                "--ignore-timeouts --ignore-crashes   --monitor-native-crashes -v -v -v 3000 > "
