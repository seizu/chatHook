# ---- open the browser with the parameters given below before starting the script ----
# chrome.exe --remote-debugging-port=9222
# firefox.exe --marionette
# tested with: python v3.11.4 , firefox v108, selenium 4.10, geckodriver 0.33.0


from ChatHook import ChatHook
discord_channel =  "https://discord.com/channels/828062267609579521/1350129071555870722"

def my_callback(data):    
    print(f"{data['local_time']}: {data['user_name']} {data['chat_text']}")
    pass

def main():   
    hook = ChatHook(browser_binary='C:/Program Files/Mozilla Firefox/firefox.exe',
                    webdriver_binary='driver/geckodriver.exe',
                    webdriver_log='driver/geckodriver.log',
                    browser='FIREFOX')
    
    #hook.init_discord(user='MY_EMAIL',password='MY_PASSWORD',channel_url=discord_channel, callback=my_callback)
    hook.init_discord(channel_url=discord_channel, callback=my_callback)
    
    #hook = ChatHook(browser_binary='D:/tools/GoogleChromePortable/App/Chrome-bin/chrome.ex',
    #                webdriver_binary='driver/chromedriver.exe',
    #                webdriver_log='driver/chromedriver.log',
    #                browser='CHROME')    
    #hook.init_discord(channel_url=discord_channel, callback=my_callback)
    
if __name__ == "__main__":
    main()