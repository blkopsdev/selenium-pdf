from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
from image_match import distance
from image_match import get_tracks
from image_match import getSlideInstance


class ChinaVisa:
    def __init__(self, time2wait=10):
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('disable-infobars')
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--verbose')
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": "/home/ubuntu/work/visa-selenium/pdf/downloaded",
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing_for_trusted_sources_enabled": False,
            "safebrowsing.enabled": False
        })
        self.browser = webdriver.Chrome(chrome_options=chrome_options)
        self.browser.implicitly_wait(10)
        self.browser.get('https://bio.visaforchina.org/#/nav/quickSelection?visacenterCode=HAG2&' \
                         'request_locale=en_US&site_alias=HAG2_EN')
        self.wait = WebDriverWait(self.browser, time2wait)

    def new_form(self):
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//button[@ng-click=\'prepareApplicationForm()\']')))\
            .click()  # Prepare new application
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//button[@ng-click=\'agree()\']'))).click()
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//label[@for="introduction1"]'))).click()
        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '//button[@ng-click=\'startANew()\']'))).click()  # Start new form

    def slideVerifyCode(self):
        slider = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'yidun_slider')))
        ActionChains(self.browser).click_and_hold(slider).perform()
        slider_loc_x = slider.location["x"]
        img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "yidun_bg-img")))
        icon = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "yidun_jigsaw")))
        pic_width = img.size['width']
        icon_width = icon.size['width']
        img_url = img.get_attribute("src")
        icon_url = icon.get_attribute("src")
        match_x = distance(img_url, icon_url, pic_width)
        if match_x == -1:
            raise Exception()

        slider_instance = getSlideInstance(pic_width, icon_width, match_x)
        tracks = get_tracks(slider_instance)

        for track in tracks:
            ActionChains(self.browser).move_by_offset(xoffset=track, yoffset=0).perform()
        else:
            ActionChains(self.browser).move_by_offset(xoffset=3, yoffset=0).perform()
            ActionChains(self.browser).move_by_offset(xoffset=-3, yoffset=0).perform()
            time.sleep(0.5)
            ActionChains(self.browser).release().perform()
        time.sleep(5)

        form_start = self.browser.find_element_by_xpath('//input[@ng-model="personal.personinfo_passportfamilyname"]')
        if form_start:
            print("Captcha passed successfully")
            return True
        else:
            return False

    def getCaptcha(self, attempt_times=20):

        self.new_form()
        self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, "yidun_tips__text"),
                                                         r"drag to complete puzzle"))
        for attempt in range(attempt_times):
            try:
                if self.slideVerifyCode():
                    return True
            except Exception as e:
                print(e)
                ActionChains(self.browser).release().perform()
                refresh = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "yidun_refresh")))
                refresh.click()
                time.sleep(0.6)
        return False

    def mainStep(self):
        self.browser.close()

    def find_element_by_xpath(self, xpath):
        while True:
            try:
                return self.browser.find_element_by_xpath(xpath)
            except:
                time.sleep(1)
                continue

    def find_element_by_id(self, id):
        while True:
            try:
                return self.browser.find_element_by_id(id)
            except:
                time.sleep(1)
                continue

    def find_elements_by_xpath(self, xpath):
        while True:
            try:
                return self.browser.find_elements_by_xpath(xpath)
            except:
                time.sleep(1)
                continue


if __name__ == '__main__':
    drv = ChinaVisa()
    drv.getCaptcha()
    drv.mainStep()
