from selenium import webdriver

def init_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--user-data-dir=C:/Users/Arthur/AppData/Local/Google/Chrome/User Data')  # Caminho para o perfil do usuário do Chrome
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })

    return driver
