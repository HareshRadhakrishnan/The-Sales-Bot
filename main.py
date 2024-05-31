from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import pyperclip
from selenium.common.exceptions import UnexpectedAlertPresentException
from time import sleep
import pandas as pd
Chrome_Driver_path = "C:/Users/Haresh/PycharmProjects/chromedriver_win32/chromedriver.exe"
# csv_file_path = 'statics/cleaned_data.csv'
csv_file_path = 'statics/1day_missed.csv'
class DataCollector:
    def __init__(self,driver_path):
        self.driver = webdriver.Chrome(driver_path)

    def collect(self):
        for num in range(41,200):
            self.driver.get(f'https://www.mytutor.lk/teachers_and_tuition_classes_in_sri_lanka.php?page={num}&ipp=20&')
            # self.driver.get(f'https://www.mytutor.lk/teachers_and_tuition_classes_in_sri_lanka.php')
            sleep(1)
            # self.data_div = self.driver.find_element_by_xpath('/html/body/div[2]/div[1]/section/div[2]')
            alldata = self.driver.find_elements_by_xpath(".//*[@class='product-info']")
            for data in alldata:
                sleep(0.2)
                link  = data.find_element_by_xpath('.//h5/a').get_attribute('href')
                self.driver.execute_script(f'window.open("{link}");')
                self.driver.switch_to.window(self.driver.window_handles[1])
                self.scrape_page()
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                sleep(1)
    def scrape_page(self):
        sleep(1)
        details_div = self.driver.find_element_by_css_selector('div.col-xs-9')
        name = details_div.find_element_by_xpath('//font/span/b')
        name = name.text
        education = details_div.find_element_by_css_selector('strong[style="color:#2ecc71;"]')
        education = education.text
        occupation = details_div.find_element_by_xpath('//span/strong[2]').text.split(':')[1]
        age = details_div.find_element_by_xpath('//span/strong[3]').text.split(' ')[2]
        btn_contact = details_div.find_element_by_id('loadContactDetails')
        btn_contact.click()
        sleep(0.2)
        div_contact = details_div.find_element_by_id('load_contact')
        phone = div_contact.find_elements_by_css_selector('strong a')
        try:
            mail = div_contact.find_element_by_css_selector('span[style="color:#666666; font-size:14px"]').find_element_by_css_selector('strong')
            mail = mail.text
        except:
            mail = None
            pass
        other_details = self.driver.find_elements_by_xpath('//*[@id="product-slider"]')
        medium = other_details[3].find_elements_by_xpath(".//*[@class='label label-default span_labal']")
        medium = [med.text for med in medium]

        subjects =other_details[2].find_elements_by_css_selector('li b a')
        subjects = [subject.text for subject in subjects]

        try:
            whatsapp = phone[-1].text
        except IndexError:
            print('Whats App number not found')
            whatsapp = phone
            pass
        self.save_data(data_list =  [name,education,age,occupation,whatsapp,[num.text for num in phone], subjects,mail,medium])

    def save_data(self,data_list):
        # df_data = pd.DataFrame(columns=['Name','Education','age','Occupation','Whatsapp','Phone numbers','Subject', 'Mail', 'Medium'])
        df_data = pd.read_csv('data.csv')
        df_data = df_data.append(pd.DataFrame([data_list],columns=['Name','Education','age','Occupation','Whatsapp','Phone numbers','Subject', 'Mail', 'Medium']),ignore_index=True)
        print(df_data)
        df_data.to_csv('data.csv', index=False)
class Whatsapp:
    def __init__(self, Chrome_path, data_file):
        self.path = Chrome_path
        self.csv = data_file
    def get_numbers(self):
        csv_data = pd.read_csv(self.csv)
        whatsapp_numbers  = csv_data.Whatsapp.values
        return whatsapp_numbers

    def message(self,msg):
        whats_nums = self.get_numbers()
        driver = webdriver.Chrome(self.path)
        driver.get('https://web.whatsapp.com')
        sleep(15)
        print(len(whats_nums))
        numbers_listed = 0
        for whats_num in whats_nums:
            numbers_listed +=1
            print(f"Processing row : {numbers_listed}")
            f = open('current_row.txt', 'a')
            f.write(f"Processing row : {numbers_listed}")
            if len(str(whats_num)) ==10 and str(whats_num)[0] == '0':
                whats_num = str(whats_num)[1:]
            elif str(whats_num)[0] != '0' or str(whats_num)[0] != '7':
                f.write(f'for {whats_num} Message Failed ')
                print( f'The number is {whats_num}')
                continue
            try:
                driver.get(f'https://web.whatsapp.com/send?phone=+94{whats_num}')
                sleep(5)
                wait = WebDriverWait(driver=driver, timeout=20)
                input_path = '//*[@id="main"]/footer/div[1]/div[2]/div/div[1]/div/div[2]'
                box = wait.until(EC.presence_of_element_located((By.XPATH, input_path)))
                pyperclip.copy(msg)
                box.send_keys(Keys.CONTROL + 'v' )
                box.send_keys(Keys.ENTER)
                sleep(3)
            except UnexpectedAlertPresentException:
                sleep(5)
            except Exception as e:
                error_csv = pd.read_csv('errors.csv')
                # error_csv = pd.DataFrame(columns=['row', 'number', 'error'])
                error_lst = [numbers_listed, whats_num, str(e)]
                error_csv = error_csv.append(pd.DataFrame([error_lst], columns=['row','number', 'error']),ignore_index=True)
                error_csv.to_csv('errors.csv',index=False)
                print(f'for +94{whats_num} Message Failed Due to {e}')
                f.write(f'for +94{whats_num} Message Failed Due to {e}')
                pass

            f.close()
# Data_driver = DataCollector(Chrome_Driver_path)
# Data_driver.collect()

whatsapp = Whatsapp(Chrome_Driver_path, csv_file_path)
with open('msg.txt', encoding='utf-8') as msg:
    message = msg.read()

message  = message
whatsapp.message(message)

