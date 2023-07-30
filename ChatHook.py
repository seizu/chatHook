import datetime
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class ChatHook:
    def __init__(self, browser_binary, webdriver_binary, webdriver_log=None, browser='FIREFOX', poll_frequency=1.0, timeout=30):
        
        self.default_browser = browser
        self.driver = None
        self.poll_frequency = poll_frequency
        self.timeout = timeout
        if webdriver_log is None:
            webdriver_log = webdriver_binary + '.log.txt'

        if self.default_browser == 'FIREFOX':
            from selenium.webdriver.firefox.options import Options
            from selenium.webdriver.firefox.service import Service

            service_args = ['--connect-existing', '--marionette-port=2828', '--marionette-host=127.0.0.1']
            service = Service(executable_path=webdriver_binary, service_args=service_args, log_path=webdriver_log)
            options = Options()
            options.binary_location = browser_binary
            self.driver = webdriver.Firefox(service=service, options=options)

        elif self.default_browser == 'CHROME':
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            #caps = {'browserName': 'chrome', 'version': '', 'platform': 'ANY', 'goog:chromeOptions': {'extensions': [], 'args': [], 'debuggerAddress': '127.0.0.1:9222'}}
            service = Service(executable_path=webdriver_binary, log_path=webdriver_log)
            options = Options()
            options.debugger_address = "127.0.0.1:9222"            
            options.binary_location = browser_binary
            self.driver = webdriver.Chrome(service=service, options=options)
        else:
            raise ValueError("Browser not supported")
    
    def tprint(self, text=""):
        print(datetime.datetime.now(datetime.timezone.utc).isoformat()[:23] + "Z: " + str(text))

    def send_message(self, text):
        textbox = self.driver.find_element(By.XPATH, self.XP_TEXT_AREA)
        textbox.send_keys(text)
        textbox.send_keys(Keys.ENTER)

    def _inject_javascript(self):
        with open(self.INJECTOR, 'r', encoding='utf-8') as file:
            js = file.read()
        self.driver.execute_script(js)

    def init_discord(self, user=None, password=None, channel_url=None, callback=None):
        self.user = user
        self.password = password
        self.channel_url = channel_url        
        self.XP_CHATSTACK = '//div[starts-with(@id,"chat-stack-id-")]'
        self.XP_LOGIN_USER = '//input[@name="email"]'
        self.XP_LOGIN_PW = '//input[@name="password"]'
        self.XP_BUTTON_SUBMIT = '//button[@type="submit"]'
        self.XP_TEXT_AREA = '//div[contains(@class,"slateTextArea-")]/following::div[contains(@class,"slateTextArea-")]'
        self.INJECTOR = 'dc_injector.js'        
        self._init_hook(callback)

    def _init_hook(self, callback=None):
        if self.channel_url is not None:
            self.driver.get(self.channel_url)

        self.driver.implicitly_wait(10)
        self._inject_javascript()
        
        if self.password is not None and self.user is not None: 
            try:
                user = self.driver.find_element("xpath",self.XP_LOGIN_USER)
                pw = self.driver.find_element("xpath",self.XP_LOGIN_PW)                   
                user.send_keys(self.user)
                pw.send_keys(self.password)
                time.sleep(0.5)
                self.driver.find_element("xpath",self.XP_BUTTON_SUBMIT).click()
            except:
                pass

        self.tprint("Chat hook installed.")
        self.driver.implicitly_wait(self.timeout)        
        wait = WebDriverWait(self.driver, 1000000, poll_frequency=self.poll_frequency)
        while True:
            try:
                elems = wait.until(EC.presence_of_all_elements_located((By.XPATH, self.XP_CHATSTACK)))
            except Exception as e:
                self.tprint(e)

            for elem in elems:
                try:
                    data = {}
                    data['msg_id'] = elem.get_attribute('data-msgId')
                    data['utc_time'] = elem.get_attribute('data-utcTime')
                    data['local_time'] = elem.get_attribute('data-localTime')
                    data['unix_time'] = float(elem.get_attribute('data-unixTime'))
                    data['user_name'] = elem.get_attribute('data-userName')
                    data['chat_content'] = elem.get_attribute('innerText')
                    data['chat_text'] = data['chat_content']
                    #time, data['chat_text'] = re.split('^\[[0-9: ]{5,7}\].*?: ', data['chat_content'])                    
                    data['ms_elapsed'] = float(int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds() * 1000) - data['unix_time'])                        
                    self.driver.execute_script("document.getElementById('chat-stack-id-" + elem.get_attribute('id')[14:] + "').remove();")

                    if callback is not None:
                        callback(data)
                except Exception as e:
                    self.tprint(e)
                    return
        
