from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


flag = False
driver = webdriver.Chrome(ChromeDriverManager().install())

driver.get("https://www.kiloo.com/subway-surfers/")

try:
    # wait 10 seconds before looking for element
    AgreeButton = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH,"//span[text()='AGREE']")))
    AgreeButton.click()
finally:
    # else quit
    pass

actions = ActionChains(driver)
def clickCanvas():
    global flag
        # wait 10 seconds before looking for element
    if flag==False :
        
        # Canvas = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,"//body/canvas"))).click()
        iframe = driver.find_element_by_xpath("//iframe[@id='gameframe']")
        driver.switch_to.frame(iframe)

        Canvas = driver.find_element(By.XPATH,"//body/canvas")
        Canvas.click()
        flag=True
    return Canvas
    # else quit


driver.fullscreen_window()

body = driver.find_element(by=By.TAG_NAME, value="body")
    
def clickRight():
    # canvas = clickCanvas()
    actions.send_keys(Keys.ARROW_RIGHT).perform()

    # body.send_keys(Keys.ARROW_RIGHT)
def clickLEFT():
    # canvas = clickCanvas()
    actions.send_keys(Keys.ARROW_LEFT).perform()

    body.send_keys(Keys.ARROW_LEFT)
def clickUP():
    # canvas = clickCanvas()
    actions.send_keys(Keys.ARROW_UP).perform()

    body.send_keys(Keys.ARROW_UP)
def clickDOWN():
    # canvas = clickCanvas()
    actions.send_keys(Keys.ARROW_DOWN).perform()

    body.send_keys(Keys.ARROW_DOWN)
def closeWebDriver():
    driver.close()