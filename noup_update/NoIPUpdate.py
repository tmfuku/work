#!/usr/bin/env python
# coding: utf-8

import json
import sys
import os
import time
import slackweb
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

CHROMEDRIVER = "/usr/bin/chromedriver"


def send_slack(hookurl, msg):
    hookurl = 'https://hooks.slack.com/services/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'
    slack = slackweb.Slack(url=hookurl)
    slack.notify(title='NoIP Notify', text=msg)


def get_driver():
     
    #　ヘッドレスモードでブラウザを起動
    options = Options()
    options.add_argument('--headless')
 
 
    # ブラウザーを起動
    driver = webdriver.Chrome(CHROMEDRIVER, options=options)
     
    return driver


def AutoLogin(conf):
    # 起動するブラウザを宣言します 
    browser = get_driver()
    
    # ログイン対象のWebページURLを宣言します 
    url  = 'https://www.noip.com/login'
    
    # 対象URLをブラウザで表示します。 
    browser.get(url)
    # ログインIdとパスワードの入力領域を取得します。 

    user_id = browser.find_element_by_name("username")
    pass_id = browser.find_element_by_name("password")
    
    login_btn = browser.find_element_by_id("clogs-captcha-button")
    
    user_id.send_keys(conf['userName'])
    pass_id.send_keys(conf['passwd'])
    
    login_btn.click()
    
    time.sleep(5)
    
    browser.save_screenshot('/tmp/xxx.png')
    return browser
    
def update(browser, conf):

    active_elm = browser.find_element_by_xpath('//*[@id="content-wrapper"]/div[1]/div[2]/div[1]/div[1]/div[1]/div/div/div/div/div/span[2]')
    print(active_elm)
    active_elm.click()
    time.sleep(5)
    
    #browser.save_screenshot('/tmp/xxx2.png')
    
    host_elm = browser.find_element_by_xpath('//*[@id="host-panel"]/table/tbody/tr/td[1]')
    
    print(host_elm.text)
    send_slack(conf['slackHookUrl'], host_elm.text)


if __name__ == '__main__':
    with open('NoIPUpdate.json', 'r') as f:
        conf = json.load(f)
    browser = AutoLogin(conf)
    update(browser, conf)
    




