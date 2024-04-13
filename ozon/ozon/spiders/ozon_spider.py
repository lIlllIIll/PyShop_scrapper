import scrapy
import time

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from ..items import SmartphoneOsItem


class OzonSmartphonesSpider(scrapy.Spider):
    name = "ozon_spider"
    allowed_domains = ["ozon.ru"]
    path = "./driver/chromedriver.exe"
    start_url = "https://www.ozon.ru/category/smartfony-15502/?sorting=rating&page=1"
    the_required_amount = 100
    smartphones_links = []
    page_num = 0

    def start_requests(self):
        self.driver = self.get_selenium_driver()
        while len(self.smartphones_links) < self.the_required_amount:
            self.get_smartphones_links(self.get_next_page())
        yield scrapy.Request(
            url='https://blank.org',
            callback=self.parse_smartphone,
            dont_filter=True,
        )

    def get_selenium_driver(self):
        self.options = uc.ChromeOptions()
        self.prefs = {}
        self.prefs["profile.default_content_settings"] = {"images": 2}
        self.prefs["profile.managed_default_content_settings"] = {"images": 2}
        self.options.add_experimental_option("prefs", self.prefs)

        return uc.Chrome(options=self.options, headless=False,
                         driver_executable_path=self.path, version_main=123)

    def get_smartphones_links(self, url):
        self.driver.get(url)
        try:
            el = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "a.tile-hover-target")))
        except:
            pass
        self.driver.execute_script('window.scrollTo(5,5000);')
        try:
            el = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.ID, 'ozonTagManagerApp')))
        except:
            pass

        time.sleep(1)
        self.products = self.driver.find_elements(By.XPATH, "//div[@id='paginatorContent']/div/div/div/div/a")
        print(len(self.products))
        for product in self.products:
            self.href = product.get_attribute('href')
            if '-smartfon-' in self.href:
                if len(self.smartphones_links) < self.the_required_amount:
                    self.smartphones_links.append(self.href)
                else:
                    break

    def get_next_page(self):
        self.page_num = self.page_num + 1
        self.next_page_url = self.start_url[:self.start_url.find('page')] + f'page={self.page_num}'
        return self.next_page_url

    def parse_smartphone(self, response):
        for smartphone_link in self.smartphones_links:
            self.driver.get(smartphone_link)
            time.sleep(0.1)
            self.driver.execute_script('window.scrollTo(5,2000);')
            try:
                el = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, "//div[@id='section-characteristics']/div[1]")))

            except:
                pass

            time.sleep(0.2)

            if '-iphone-' in smartphone_link or 'apple-' in smartphone_link:
                self.iphone_os = 'iOS'
                try:
                    self.iphone_os = self.driver.find_element(
                        By.PARTIAL_LINK_TEXT, "iOS ").text
                except:
                    try:
                        self.iphone_os = self.driver.find_element(
                            By.XPATH, "//dd[contains(.,'iOS ')]").text
                    except:
                        pass

                yield SmartphoneOsItem(os_version=self.iphone_os)

            else:
                try:
                    self.android_os = self.driver.find_element(
                        By.XPATH, "//dd[contains(.,'Android ')]").text
                except:
                    try:
                        self.android_os = self.driver.find_element(
                            By.PARTIAL_LINK_TEXT, "Android").text
                    except:
                        try:
                            self.android_os = self.driver.find_element(
                                By.XPATH, "//dd[contains(.,'Android')]").text
                        except:
                            self.android_os = 'Unknown'
                            print(smartphone_link)

                yield SmartphoneOsItem(os_version=self.android_os)
