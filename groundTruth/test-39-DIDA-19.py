import time
from appium import webdriver

desired_caps = {}
desired_caps['platformName'] = 'Android'
desired_caps['platformVersion'] = '6.0.1'
desired_caps['deviceName'] = '127.0.0.1:7555'
desired_caps['appPackage'] = 'cn.ticktick.task'
desired_caps['appActivity'] = 'com.ticktick.task.activity.MeTaskActivity'
desired_caps['newCommandTimeout'] = '1000'
desired_caps['noReset'] = True

driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', desired_caps)
time.sleep(10)

try:
    el1 = driver.find_elements_by_class_name('android.widget.ImageButton')[1]
    el1.click()
    time.sleep(3)

    el2 = driver.find_elements_by_id('cn.ticktick.task:id/amc')[0]
    el2.click()
    time.sleep(3)

    el3 = driver.find_elements_by_id('android:id/title')[4]
    el3.click()
    time.sleep(3)

    el4 = driver.find_elements_by_id('android:id/title')[0]
    el4.click()
    time.sleep(3)

    el5 = driver.tap([(189, 299)])
    el5.click()
    time.sleep(3)

    el6 = driver.tap([(123, 681)])
    el6.click()

finally:
    time.sleep(3)
    driver.quit()
