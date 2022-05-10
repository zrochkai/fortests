#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import os
import time
import pymysql

from Screenshot import Screenshot_Clipping
from config import anti_captcha_key
from selenium import webdriver
from anticaptchaofficial.imagecaptcha import *
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service

from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from vpn_disconnect_email import send_mail_connect_vpn
import smtplib

def enter_as_human(element, string):
    for s in string:
        element.send_keys(s)
        time.sleep(0.5)

def run_main_loggedin():
    """
    This method used to purchase the offers from comcast
    :return:
    """
    # preview = input("Enter y if you want to test with preview site, or n to test with business: ").lower()
    # if preview == "y":
    #     preview = True
    # else:
    #     preview = False 
    # till_the_end = input("Enter y if you want run all the way till the end, or n if you want to stop at checkout page: ").lower()
    # if till_the_end == "y":
    #     till_the_end = True
    # else:
    #     till_the_end = False

    email_error_text = "The following errors occured: <br>"
    users_not_find_offers_text_dict = {}
    users_not_find_offers_text_dict["Central"] = "Central:<br><br>"
    users_not_find_offers_text_dict["NED"] = "NED:<br><br>"
    users_not_find_offers_text_dict["West"] = "West:<br><br>"
    
    preview = False

    mydb = pymysql.connect(
        host="localhost",
        user="root",
        password="comcast", 
        database="comcast_scrap" 
    )
    mycursor = mydb.cursor()

    root_dir = os.path.dirname(os.path.abspath(__file__))

    offers_to_test = {"Central" : {}, "NED" : {}, "West" : {}}
    sql = "SELECT `Division`, `EPC Offer #` from active_no_exclusions_smb;"
    mycursor.execute(sql)
    for data in mycursor.fetchall():
        try:
            division = data[0]
            offer_id = str(int(data[1]))
        except:
            continue
        if offer_id not in offers_to_test[division]:
            offers_to_test[division][offer_id] = [False]
  

    sql = "SELECT * FROM accounts.user_accounts"

    mycursor.execute(sql)
    result = mycursor.fetchall()
    for data in result:
        p_id = data[8]
        user_name = data[4]
        password = data[5]
        division = data[0]
        if user_name:
            user_name = user_name.strip()
        if password:
            password = password.strip()
        if division:
            division = division.strip()
        print(user_name)
        print(password)
        print(division)
        if user_name and password:

            #options.headless = True
            #options.add_argument("--log-level=3")
            #options.add_argument("--disable-gpu");
            #options.add_argument("--no-sandbox");
            #driver = webdriver.Chrome(options=options)

            chromeOptions = Options()
            chromeOptions.add_argument("--headless")
            #chromeOptions.add_argument("--remote-debugging-port=9222")
            chromeOptions.add_argument('--no-sandbox')
            script_dir = os.path.dirname(os.path.abspath(__file__))
            service = Service(os.path.join(script_dir, "chromedriver"))
            driver = webdriver.Chrome(service=service, options=chromeOptions)

            url = 'https://business.comcast.com/'
            try:
                driver.get(url)
                # driver.find_element_by_class_name("bsp-buddy-profile-btn").click()
            except:
                #send_mail_connect_vpn(os.path.basename(__file__))
                while True:
                    print("retrying...")
                    try:
                        driver.get(url)
                        break
                    except:
                        time.sleep(600)
            time.sleep(5)

            driver.maximize_window()
            counter = 0
            while True:
                try:
                    if counter > 2:
                        break
                    modal_close_btn = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.kcHeader > button'))
                        )
                    if modal_close_btn:
                        modal_close_btn.click()
                        print("Modal exits")
                        time.sleep(2)
                        break
                    else:
                        print("Modal not find")
                except:
                    counter = counter + 1
                    print("Modal not find")

            try:
                hamburger_btn = WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.CLASS_NAME, 'bsp-profile-icon--hamburger'))
                        )
                if hamburger_btn:
                    hamburger_btn.click()
                    time.sleep(2)
            except:
                pass

            while True:
                print("redirecting to login...")
                try:
                    driver.find_element(By.CLASS_NAME, "bsp-buddy-profile--sign-in").click()
                    break
                except:
                    time.sleep(5)
                    print("retrying...")
            time.sleep(5)
            #driver.maximize_window()

            if 'media-container' in driver.page_source:
                print("media-container --- ")
                element1 = driver.find_element_by_id('media-container').screenshot('./screenshot.png')

                solver = imagecaptcha()
                solver.set_verbose(1)
                solver.set_key(anti_captcha_key)

                captcha_text = solver.solve_and_return_solution("./screenshot.png")

                if captcha_text != 0:
                    print("captcha text " + captcha_text)
                else:
                    print("task finished with error " + solver.error_code)
                
                captcha_text = str(captcha_text).upper()

            while True:
                print("checking login form...")
                try:
                    WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="user"]'))
                        )
                    print("checked")
                    break
                except:
                    print("retrying...")
            print("logining...")
            while True:
                enter_as_human(driver.find_element(By.XPATH, '//*[@id="user"]'), user_name)
                time.sleep(2)
                enter_as_human(driver.find_element(By.XPATH, '//*[@id="passwd"]'), password)
                time.sleep(2)

                if 'media-container' in driver.page_source:
                    driver.find_element_by_xpath('//*[@id="nucaptcha-answer"]').send_keys(captcha_text)
                    time.sleep(2)

                driver.find_element_by_xpath('//*[@id="sign_in"]').click()

                time.sleep(4)
                try:
                    driver.find_element_by_xpath('//*[@id="content"]/div/div/div[2]/p/a').click()
                except:
                    pass
                if "Incorrect" not in driver.page_source:
                    print('Incorrect --- ')
                    break
                else:
                    print("login info incorrect")
                    break
                print("retrying...")
                time.sleep(5)

            time.sleep(10)
            print("Please re-enter your email address and password and try again...")
            if 'Please re-enter your email address and password and try again.' in driver.page_source:
                print('username or password wrong')
                driver.close()
                continue
            print("preview")
            if preview:
                url = "https://preview.business.comcast.com/shop/offers/"
            else:
                url = "https://business.comcast.com/shop/offers/"
            driver.get(url)
            time.sleep(10)

            crawl_date = time.strftime('%Y-%m-%d')
            crawl_time = time.strftime('%H:%M:%S')
            print("servicequoteshort --- ")
            if 'servicequoteshort' in driver.current_url:
                print("no offers found.")
                sql = "INSERT INTO accounts_with_no_offers(timestamp, username, password) VALUES(%s, %s, %s);"
                val = (crawl_date + crawl_time, user_name, password)
                mycursor.execute(sql, val)
                mydb.commit()
                save_screenshot_no_offers(driver, f"{user_name}.png")
                driver.close()
                users_not_find_offers_text_dict[division] += user_name + "<br>"
                continue
            try:
                survey = driver.find_elements_by_class_name("kcBtn.kcBtnIcon.kcBtn-remove")
                print(survey)
                survey.click()
                print("Survey Popup closed")
            except:
                print("No Survey Popup appeared")

            # 2. Message popup - following code will select "No" for help when it appears
            try:
                popup = driver.find_element_by_css_selector("div.kcInviteBtns > div.kcInviteNoBtnWrapper > button")
                popup.click()
                print("Popup Closed")
            except:
                print("No Popup appeared")

            try:
                driver.find_element_by_css_selector("[title*='Close chat window']").click()
                print("Chat pop up")
                print("Pop up closed")
            except:
                print("No Chat pop up")

            

            offer_card_name = driver.find_elements_by_css_selector(".cb-offer-card-name")
            link = driver.find_elements_by_css_selector(".text-link-primary")

            names = [el.text for el in offer_card_name]
            print("offers found:")
            print(names)

            item_link = []

            for el in link:
                if el.get_attribute("href"):
                    item_link.append(el.get_attribute("href"))

            if not item_link:
                link = driver.find_elements_by_css_selector('.button-primary')
                item_link = [el.get_attribute("href") for el in link]

            print("offer links:")
            print(item_link)
            if len(names) == 0:
                print("No offers found.")
                sql = "INSERT INTO accounts_with_no_offers(timestamp, username, password) VALUES(%s, %s, %s);"
                val = (crawl_date + crawl_time, user_name, password)
                mycursor.execute(sql, val)
                mydb.commit()
                save_screenshot_no_offers(driver, f"{user_name}.png")
                driver.close()
                users_not_find_offers_text_dict[division] += user_name + "<br>"
                continue
            required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
            # driver.set_window_size(1920, required_height)
            if not os.path.isdir(f"all_offers_{user_name}"):
                os.mkdir(f"all_offers_{user_name}")
            # driver.save_screenshot(f"all_offers_{user_name}/{driver.title}.png".replace("|", " "))
            ob = Screenshot_Clipping.Screenshot()
            ob.full_Screenshot(driver, save_path=r'.', image_name=f"all_offers_{user_name}/{driver.title}.png".replace("|", " "))
            with open(f"all_offers_{user_name}/{driver.title}.png".replace("|", " "), "rb") as f:
                image_content = f.read()
            screenshot0 = image_content
            for x in range(len(names)):
                if (names[x] == ''):
                    continue
                try:
                    res = item_link[x].split("/")
                    offer_id = res[len(res) - 1]
                except:
                    offer_id = "N/A"

                try:
                    url1 = url2 = url3 = url4 = server = ip = state = city = zip = isExisting = ipNumber = visitorID = visitorSessionID = release = ""
                    assemblyDate = applicationID = screenshot1 = screenshot2 = screenshot3 = screenshot4 = screenshot5 = screenshot6 = screenshot7 = screenshot8 = "" 
                    offer_id = res[len(res) - 1]
                    if offer_id in offers_to_test[division] and not offers_to_test[division][offer_id][0]:
                        offers_to_test[division][offer_id][0] = True
                        offers_to_test[division][offer_id].append(user_name)
                        driver.get(item_link[x])
                        url1 = driver.current_url
                        if not os.path.isdir(f"{offer_id}_{user_name}"):
                            os.mkdir(f"{offer_id}_{user_name}")      
                        time.sleep(5)
                        required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
                        driver.set_window_size(1920, required_height)
                        driver.save_screenshot(f"{offer_id}_{user_name}/{driver.title}.png".replace("|", " "))
                        with open(f"{offer_id}_{user_name}/{driver.title}.png".replace("|", " "), "rb") as f:
                            image_content = f.read()
                        screenshot1 = image_content
                        driver.find_element_by_class_name("cb-offer-detail-info-header-cta").find_element_by_tag_name("button").click()
                        time.sleep(5)
                        WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "s-internet-addon-addon-section-title-font"))
                        )
                        url2 = driver.current_url
                        
                        
                        
                        required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
                        driver.set_window_size(1920, required_height)
                        checkout_btn = driver.find_element_by_class_name("button.button-primary")
                        driver.execute_script("arguments[0].scrollIntoView();", checkout_btn)
                        driver.find_element_by_tag_name("body").send_keys(Keys.END)
                        driver.find_element_by_tag_name("body").send_keys(Keys.END)
                        time.sleep(0.5)
                        driver.save_screenshot(f"{offer_id}_{user_name}/{driver.title}.png".replace("|", " "))
                        with open(f"{offer_id}_{user_name}/{driver.title}.png".replace("|", " "), "rb") as f:
                            image_content = f.read()
                        screenshot2 = image_content
                        driver.find_element_by_xpath('//*[@id="buy"]/main/footer/div[2]/div/div[1]/div/button').click()
                        time.sleep(3)
                        driver.save_screenshot(f"{offer_id}_{user_name}/{driver.title}.png".replace("|", " "))
                        with open(f"{offer_id}_{user_name}/{driver.title}.png".replace("|", " "), "rb") as f:
                            image_content = f.read()
                        screenshot3 = image_content
                        driver.find_element_by_xpath('//*[@id="buy"]/main/footer/div[2]/div/div[1]/div/button').click()
                        time.sleep(2)
                        checkout_btn.click()
                        time.sleep(5)

                        # next page

                        try:
                            
                            driver.find_element_by_tag_name("body").send_keys(Keys.END)
                            driver.find_element_by_tag_name("body").send_keys(Keys.END)
                            time.sleep(0.5)
                            driver.save_screenshot(f"{offer_id}_{user_name}/{driver.title}.png".replace("|", " "))
                            with open(f"{offer_id}_{user_name}/{driver.title}.png".replace("|", " "), "rb") as f:
                                image_content = f.read()
                            screenshot4 = image_content
                            checkout_btn = driver.find_element_by_xpath('//*[@id="VoiceAddons"]/div[3]/div[1]/div[3]/button')
                            checkout_btn.click()
                            time.sleep(5)
                        except:
                            pass

                        # Enter business category
                        try:
                            
                            WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located((By.ID, "businessCategory"))
                            ).send_keys("Anything")
                            driver.find_element_by_xpath('//*[@id="account_info_form"]/button').click()
                            driver.find_element_by_xpath('//*[@id="account_info_form"]/button').click()
                            time.sleep(5)
                        except:
                            print("No Business Category")
                        # select date and time
                        try:
                            WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located((By.CLASS_NAME, "s-calendar_day._selectable"))
                            )
                            url3 = driver.current_url
                            driver.find_element_by_class_name("s-calendar_day._selectable").click()
                            select_time = Select(driver.find_element_by_id('SELECT A TIME'))
                            select_time.select_by_index(1)
                            required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
                            driver.set_window_size(1920, required_height)
                            driver.save_screenshot(f"{offer_id}_{user_name}/{driver.title}_date_selection.png".replace("|", " "))
                            with open(f"{offer_id}_{user_name}/{driver.title}_date_selection.png".replace("|", " "), "rb") as f:
                                image_content = f.read()
                            screenshot5 = image_content
                            
                            driver.find_element_by_xpath('//*[@id="installation_form"]/div/div[2]/div/div/div[2]/div[2]/button').click()
                        except:
                            print("No date and time selection.")
                            

                        try:
                            driver.find_element_by_id("telephoneNumberInstall").clear()
                            driver.find_element_by_id("telephoneNumberInstall").send_keys("2127291154")
                            driver.find_element_by_xpath('//*[@id="installation_form"]/div/div[3]/div[4]/button').click()
                        except:
                            pass
                        try:
                            required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
                            driver.set_window_size(1920, required_height)
                            time.sleep(0.5)
                            driver.save_screenshot(f"{offer_id}_{user_name}/{driver.title}_review_order.png".replace("|", " "))
                            with open(f"{offer_id}_{user_name}/{driver.title}_review_order.png".replace("|", " "), "rb") as f:
                                image_content = f.read()
                            screenshot6 = image_content
                            complete_order_btn = driver.find_element_by_class_name("s-terms-conditions-drawer_terms")
                            driver.execute_script("arguments[0].scrollIntoView();", complete_order_btn)
                            # if offers_to_test[offer_id] == "post_checkout":
                            #     driver.find_element_by_class_name("cb-checkbox-image").click()
                            required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
                            driver.set_window_size(1920, required_height)
                            driver.save_screenshot(f"{offer_id}_{user_name}/{driver.title}_review_order2.png".replace("|", " "))
                            with open(f"{offer_id}_{user_name}/{driver.title}_review_order2.png".replace("|", " "), "rb") as f:
                                image_content = f.read()
                            screenshot7 = image_content
                            # if offers_to_test[offer_id] == "post_checkout":
                            #     driver.find_element_by_xpath('//*[@id="terms_and_condition_form"]/div[2]/button').click()
                            #     time.sleep(10)
                            #     if "SCHEDULE APPOINTMENT" in driver.page_source:
                            #         first_iteration = False
                            #         continue
                        except:
                            pass
                        
                            
                        # if offers_to_test[offer_id] == "post_checkout":
                        #     url4 = driver.current_url
                        #     required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
                        #     driver.set_window_size(1920, required_height)
                        #     driver.save_screenshot(f"{offer_id}_{user_name}/{driver.title}.png".replace("|", " "))
                        #     with open(f"{offer_id}_{user_name}/{driver.title}.png".replace("|", " "), "rb") as f:
                        #         image_content = f.read()
                        #     screenshot8 = image_content
                        if preview:
                            driver.get("https://preview.business.comcast.com/healthcheck/")
                        else:
                            driver.get("https://business.comcast.com/healthcheck/")
                        time.sleep(2)
                        fields = [elem.find_elements_by_tag_name("td")[1].text for elem in driver.find_elements_by_tag_name("tr")]
                        server = fields[0]
                        ip = fields[1]
                        state = fields[2]
                        city = fields[3]
                        zip = fields[4]
                        isExisting = fields[5]
                        ipNumber = fields[6]
                        visitorID = fields[7]
                        visitorSessionID = fields[8]
                        release = fields[9]
                        assemblyDate = fields[10]
                        applicationID = fields[11]

                        scms_id = ""
                        try:
                            for row in driver.find_elements_by_tag_name("table")[1].find_elements_by_tag_name("tr"):
                                if "SCMS_ID" in row.find_element_by_tag_name("td").text:
                                    scms_id = row.find_elements_by_tag_name("td")[1].text
                                    break
                        except:
                            pass

                        print(scms_id)
                        mycursor.execute("SELECT id FROM purchasing_user_offers ORDER BY id DESC LIMIT 1;")
                        id = mycursor.fetchall()[0][0] + 1
                        sql = "INSERT INTO purchasing_user_offers VALUES (" + "%s, "*30 + "%s);"
                        val = (id, crawl_date + crawl_time, user_name, offer_id, "True", url1, url2, url3, url4, server, ip, state, city, zip, isExisting, ipNumber, 
                        visitorID, visitorSessionID, release, assemblyDate, applicationID, scms_id, screenshot0, screenshot1, screenshot2, screenshot3, screenshot4, screenshot5, 
                        screenshot6, screenshot7, screenshot8)
                        print(f"offer {offer_id} purchased")
                        mycursor.execute(sql, val)
                        mydb.commit()
                        
                                                     

                except Exception as e:
                    print(e)
                    sql = "INSERT INTO unable_to_test_offers (timestamp, offer_id, reason) VALUES (%s, %s, %s);"
                    values = (crawl_date + " " + crawl_time, offer_id, "Ran into error during purchase. Error: " + str(e))
                    mycursor.execute(sql,values)
                    mydb.commit()
                    email_error_text += f"Offer ID {offer_id} User: {user_name}: {str(e)}<br>"
            
            print("signing out")
            driver.get("https://business.comcast.com/account/overview")
            time.sleep(3)
            try:
                driver.find_element_by_xpath('//*[@id="bcp-header"]/div[4]/div/div[4]/button').click()
                time.sleep(1)
                driver.find_element_by_id('bsdMyAccountSignOut').click()
            except:
                pass

            driver.close()

    crawl_date = time.strftime('%Y-%m-%d')
    crawl_time = time.strftime('%H:%M:%S')
    email_success_text = "Following are the active offers which were successfully tested during today's session: <br>"
    for division, value in offers_to_test.items():
        email_success_text += f"<br>{division}:<br><br>"
        for offer_id, arr in value.items():
            if arr[0]:
                email_success_text += offer_id + " - Tested by user: " + value[offer_id][1] + "<br>"
            else:
                sql = "INSERT INTO unable_to_test_offers (timestamp, offer_id, reason) VALUES (%s, %s, %s);"
                values = (crawl_date + " " + crawl_time, offer_id, "Unable to find offer")
                mycursor.execute(sql, values)
                mydb.commit()

    users_not_found_text = "The following users did not find any offers:<br><br>"
    for division, text in users_not_find_offers_text_dict.items():
        users_not_found_text += text

    return ("TEST RESULTS FOR LOGGED IN USERS: <br><br>" + email_success_text + "<br>" + users_not_found_text + "<br>" + email_error_text), offers_to_test

def run_main_non_loggedin():
    """
    This method used to purchase the offers from comcast
    :return:
    """
    # preview = input("Enter y if you want to test with preview site, or n to test with business: ").lower()
    # if preview == "y":
    #     preview = True
    # else:
    #     preview = False 
    # till_the_end = input("Enter y if you want run all the way till the end, or n if you want to stop at checkout page: ").lower()
    # if till_the_end == "y":
    #     till_the_end = True
    # else:
    #     till_the_end = False

    email_error_text = "The following errors occurred: <br>"
    address_not_find_offers_text_dict = {}
    address_not_find_offers_text_dict["Central"] = "Central:<br><br>"
    address_not_find_offers_text_dict["NED"] = "NED:<br><br>"
    address_not_find_offers_text_dict["West"] = "West:<br><br>"
    
    preview = False

    mydb = pymysql.connect(
        host="localhost",
        user="root",
        password="comcast", 
        database="comcast_scrap" 
    )
    mycursor = mydb.cursor()

    offers_to_test = {"Central" : {}, "NED" : {}, "West" : {}}
    sql = "SELECT `Division`, `EPC Offer #` from active_no_exclusions_smb;"
    mycursor.execute(sql)
    for data in mycursor.fetchall():
        try:
            division = data[0].strip()
            offer_id = str(int(data[1]))
        except:
            continue
        if offer_id not in offers_to_test[division]:
            offers_to_test[division][offer_id] = [False]
  

    sql = "SELECT * FROM accounts.addresses"

    mycursor.execute(sql)
    result = mycursor.fetchall()
    # got_west = False
    # got_ned = False
    # got_central = False
    for data in result:
        region = data[0]
        if region:
            region = region.strip()
        street = data[1]
        suite = data[2]
        city = data[3]
        state = data[4]
        zip = data[5]
        id = data[7]
        
        # if region == "West" and got_west:
        #     continue
        # if region == "NED" and got_ned:
        #     continue
        # if region == "Central" and got_central:
        #     continue
        # if not suite:
        #     continue

        options = Options()
        #options.headless = True
        options.add_argument("--log-level=3")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(options=options)
        url = 'https://business.comcast.com/shop/offers'
        if preview:
            url = "https://preview.business.comcast.com/shop/offers"
        try:
            driver.get(url)
        except:
            send_mail_connect_vpn(os.path.basename(__file__))
            while True:
                try:
                    driver.get(url) 
                    break
                except:
                    time.sleep(600)
        driver.maximize_window()
        time.sleep(5)
        try:
            driver.find_element_by_class_name("kcSurvey").find_element_by_class_name("kcBtn.kcBtnIcon.kcBtn-remove").click()
            time.sleep(1)
        except:
            pass
        try:
            driver.find_element_by_class_name("kcInviteNoBtnWrapper").click()
            time.sleep(1)
        except:
            pass
        try:
            address_input = WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.ID, "address"))
                            )
        except:
            try:
                driver.find_element_by_class_name("text-link.text-link-primary").click()
                address_input = WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.ID, "address"))
                            )
            except:
                continue
        address = f"{street} {city} {state} {zip}"
        address_input.send_keys(address)
        time.sleep(8)
        try:
            WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.ID, "ca-listbox"))
                            ).find_element_by_tag_name("li").click()
        except:
            continue
        time.sleep(1)
        driver.find_element_by_class_name("button.button-primary").click()
        try:
            WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "button.button-secondary"))).click()
        except:
            pass

        try:
            driver.find_element_by_id("address").send_keys(suite)
            time.sleep(4)
            try:
                WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located((By.ID, "ca-listbox"))
                                ).find_element_by_tag_name("li").click()
                time.sleep(1)
            except:
                pass
            driver.find_element_by_class_name("button.button-primary").click()
            time.sleep(20)
        except:
            pass
                            
        crawl_date = time.strftime('%Y-%m-%d')
        crawl_time = time.strftime('%H:%M:%S')

        offer_card_name = driver.find_elements_by_css_selector(".cb-offer-card-name")
        link = driver.find_elements_by_css_selector(".text-link-primary")

        names = [el.text for el in offer_card_name]
        print("offers found:")
        print(names)

        item_link = []

        try:
            for el in link:
                if el.get_attribute("href"):
                    item_link.append(el.get_attribute("href"))
        except:
            driver.close()
            continue

        if not item_link:
            link = driver.find_elements_by_css_selector('.button-primary')
            item_link = [el.get_attribute("href") for el in link]

        try:
            item_link = [item for item in item_link if "offers/detail" in item]
        except:
            continue
        print("offer links:")
        print(item_link)
        if len(names) == 0:
            print("No offers found.")
            save_screenshot_no_offers(driver, f"{address}.png")
            driver.close()
            address_not_find_offers_text_dict[region] += address + "<br>"
            
            continue
        required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
        driver.set_window_size(1920, required_height)
        if not os.path.isdir(f"all_offers_{street}"):
            os.mkdir(f"all_offers_{street}")
        driver.save_screenshot(f"all_offers_{street}/{driver.title}.png".replace("|", " "))
        with open(f"all_offers_{street}/{driver.title}.png".replace("|", " "), "rb") as f:
            image_content = f.read()
        screenshot0 = image_content
        for x in range(len(names)):
            if (names[x] == ''):
                continue
            try:
                res = item_link[x].split("/")
                offer_id = res[len(res) - 1]
            except:
                offer_id = "N/A"

            try:
                url1 = url2 = url3 = url4 = server = ip = state = city = zip = isExisting = ipNumber = visitorID = visitorSessionID = release = ""
                assemblyDate = applicationID = screenshot1 = screenshot2 = screenshot3 = screenshot4 = screenshot5 = screenshot6 = screenshot7 = screenshot8 = "" 
                offer_id = res[len(res) - 1]
                if offer_id in offers_to_test[region] and not offers_to_test[region][offer_id][0]:
                    offers_to_test[region][offer_id][0] = True
                    offers_to_test[region][offer_id].append(address)
                    driver.get(item_link[x])
                    url1 = driver.current_url
                    if not os.path.isdir(f"{offer_id}_{street}"):
                        os.mkdir(f"{offer_id}_{street}")      
                    time.sleep(15)
                    required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
                    driver.set_window_size(1920, required_height)
                    try:
                        driver.find_element_by_id("tcChat_btnCloseChat_img").click()
                    except:
                        pass
                    driver.save_screenshot(f"{offer_id}_{street}/{driver.title}.png".replace("|", " "))
                    with open(f"{offer_id}_{street}/{driver.title}.png".replace("|", " "), "rb") as f:
                        image_content = f.read()
                    screenshot1 = image_content
                    driver.find_element_by_class_name("cb-offer-detail-info-header-cta").find_element_by_class_name("button.button-primary").click()
                    time.sleep(5)
                    try:
                        WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "s-internet-addon-addon-section-title-font"))
                        )
                    except:
                        print("Get a free quote button found!")
                        sql = "Update accounts.addresses SET notes = 'Faulty address, shows Get a free quote button on offers' WHERE id = %s"
                        mycursor.execute(sql, (id))
                        break

                    url2 = driver.current_url 
                    required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
                    driver.set_window_size(1920, required_height)
                    checkout_btn = driver.find_element_by_class_name("button.button-primary")
                    driver.execute_script("arguments[0].scrollIntoView();", checkout_btn)
                    driver.find_element_by_tag_name("body").send_keys(Keys.END)
                    driver.find_element_by_tag_name("body").send_keys(Keys.END)
                    time.sleep(0.5)
                    driver.save_screenshot(f"{offer_id}_{street}/{driver.title}.png".replace("|", " "))
                    with open(f"{offer_id}_{street}/{driver.title}.png".replace("|", " "), "rb") as f:
                        image_content = f.read()
                    screenshot2 = image_content
                    driver.find_element_by_xpath('//*[@id="buy"]/main/footer/div[2]/div/div[1]/div/button').click()
                    time.sleep(3)
                    driver.save_screenshot(f"{offer_id}_{street}/{driver.title}.png".replace("|", " "))
                    with open(f"{offer_id}_{street}/{driver.title}.png".replace("|", " "), "rb") as f:
                        image_content = f.read()
                    screenshot3 = image_content
                    driver.find_element_by_xpath('//*[@id="buy"]/main/footer/div[2]/div/div[1]/div/button').click()
                    time.sleep(2)
                    driver.execute_script("arguments[0].scrollIntoView();", checkout_btn)
                    checkout_btn.click()
                    time.sleep(5)

                    # next page

                    WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.ID, "firstName"))
                        ).send_keys("Test")
                    driver.find_element_by_id("lastName").send_keys("Test")
                    driver.find_element_by_id("businessName").send_keys("Test")
                    driver.find_element_by_id("telephoneNumber").clear()
                    driver.find_element_by_id("telephoneNumber").send_keys("2127291154")
                    driver.find_element_by_id("emailAddress").clear()
                    driver.find_element_by_id("emailAddress").send_keys("offersbsee@gmail.com")
                    driver.save_screenshot(f"{offer_id}_{street}/{driver.title}.png".replace("|", " "))
                    with open(f"{offer_id}_{street}/{driver.title}.png".replace("|", " "), "rb") as f:
                        image_content = f.read()
                    screenshot4 = image_content
                    driver.find_element_by_class_name("button.button-primary").click()

                    # select date and time
                    try:
                        WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "s-calendar_day._selectable"))
                        )
                        url3 = driver.current_url
                        driver.find_element_by_class_name("s-calendar_day._selectable").click()
                        select_time = Select(driver.find_element_by_id('SELECT A TIME'))
                        select_time.select_by_index(1)
                        required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
                        driver.set_window_size(1920, required_height)
                        driver.save_screenshot(f"{offer_id}_{street}/{driver.title}_date_selection.png".replace("|", " "))
                        with open(f"{offer_id}_{street}/{driver.title}_date_selection.png".replace("|", " "), "rb") as f:
                            image_content = f.read()
                        screenshot5 = image_content
                        
                        driver.find_element_by_xpath('//*[@id="installation_form"]/div/div[2]/div/div/div[2]/div[2]/button').click()
                    except:
                        print("No date and time selection.")

                    # Enter business category
                    try:
                        
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, "businessCategory"))
                        ).send_keys("Anything")
                        driver.find_element_by_xpath('//*[@id="account_info_form"]/button').click()
                        driver.find_element_by_xpath('//*[@id="account_info_form"]/button').click()
                        time.sleep(5)
                    except:
                        print("No Business Category")

                    

                    try:
                        driver.find_element_by_id("telephoneNumberInstall").clear()
                        driver.find_element_by_id("telephoneNumberInstall").send_keys("2127291154")
                        driver.find_element_by_xpath('//*[@id="installation_form"]/div/div[3]/div[4]/button').click()
                    except:
                        pass
                    
                    try:
                        
                        driver.find_element_by_tag_name("body").send_keys(Keys.END)
                        driver.find_element_by_tag_name("body").send_keys(Keys.END)
                        time.sleep(0.5)
                        driver.save_screenshot(f"{offer_id}_{street}/{driver.title}.png".replace("|", " "))
                        with open(f"{offer_id}_{street}/{driver.title}.png".replace("|", " "), "rb") as f:
                            image_content = f.read()
                        screenshot6 = image_content
                        checkout_btn = driver.find_element_by_class_name('button.button-primary')
                        driver.execute_script("arguments[0].scrollIntoView();", checkout_btn)
                        checkout_btn.click()
                        time.sleep(5)
                    except:
                        pass
  
                    try:
                        required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
                        driver.set_window_size(1920, required_height)
                        time.sleep(0.5)
                        complete_order_btn = driver.find_element_by_class_name("s-terms-conditions-drawer_terms")
                        driver.execute_script("arguments[0].scrollIntoView();", complete_order_btn)
                        # if offers_to_test[offer_id] == "post_checkout":
                        #     driver.find_element_by_class_name("cb-checkbox-image").click()
                        required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
                        driver.set_window_size(1920, required_height)
                        driver.save_screenshot(f"{offer_id}_{street}/{driver.title}_review_order2.png".replace("|", " "))
                        with open(f"{offer_id}_{street}/{driver.title}_review_order2.png".replace("|", " "), "rb") as f:
                            image_content = f.read()
                        screenshot7 = image_content
                        # if offers_to_test[offer_id] == "post_checkout":
                        #     driver.find_element_by_xpath('//*[@id="terms_and_condition_form"]/div[2]/button').click()
                        #     time.sleep(10)
                        #     if "SCHEDULE APPOINTMENT" in driver.page_source:
                        #         first_iteration = False
                        #         continue
                    except:
                        pass
                    
                        
                    # if offers_to_test[offer_id] == "post_checkout":
                    #     url4 = driver.current_url
                    #     required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
                    #     driver.set_window_size(1920, required_height)
                    #     driver.save_screenshot(f"{offer_id}_{street}/{driver.title}.png".replace("|", " "))
                    #     with open(f"{offer_id}_{street}/{driver.title}.png".replace("|", " "), "rb") as f:
                    #         image_content = f.read()
                    #     screenshot8 = image_content
                    if preview:
                        driver.get("https://preview.business.comcast.com/healthcheck/")
                    else:
                        driver.get("https://business.comcast.com/healthcheck/")
                    time.sleep(2)
                    fields = [elem.find_elements_by_tag_name("td")[1].text for elem in driver.find_elements_by_tag_name("tr")]
                    server = fields[0]
                    ip = fields[1]
                    state = fields[2]
                    city = fields[3]
                    zip = fields[4]
                    isExisting = fields[5]
                    ipNumber = fields[6]
                    visitorID = fields[7]
                    visitorSessionID = fields[8]
                    release = fields[9]
                    assemblyDate = fields[10]
                    applicationID = fields[11]

                    scms_id = ""
                    try:
                        for row in driver.find_elements_by_tag_name("table")[1].find_elements_by_tag_name("tr"):
                            if "SCMS_ID" in row.find_element_by_tag_name("td").text:
                                scms_id = row.find_elements_by_tag_name("td")[1].text
                                break
                    except:
                        pass

                    print(scms_id)
                    mycursor.execute("SELECT id FROM purchasing_non_user_offers ORDER BY id DESC LIMIT 1;")
                    try:
                        id = mycursor.fetchall()[0][0] + 1
                        if not id:
                            raise Exception("No id")
                    except:
                        id = 1
                    sql = "INSERT INTO purchasing_non_user_offers VALUES (" + "%s, "*30 + "%s);"
                    val = (id, crawl_date + crawl_time, address, offer_id, "True", url1, url2, url3, url4, server, ip, state, city, zip, isExisting, ipNumber, 
                    visitorID, visitorSessionID, release, assemblyDate, applicationID, scms_id, screenshot0, screenshot1, screenshot2, screenshot3, screenshot4, screenshot5, 
                    screenshot6, screenshot7, screenshot8)
                    print(f"offer {offer_id} purchased")
                    mycursor.execute(sql, val)
                    mydb.commit()
                    # if region == "West":
                    #     got_west = True
                    # elif region == "NED":
                    #     got_ned = True
                    # elif region == "Central":
                    #     got_central = True
                    

            except Exception as e:
                print(e)
                sql = "INSERT INTO unable_to_test_offers (timestamp, offer_id, reason) VALUES (%s, %s, %s);"
                values = (crawl_date + " " + crawl_time, offer_id, "Ran into error during purchase. Error: " + str(e))
                mycursor.execute(sql,values)
                mydb.commit()
                email_error_text += f"Offer ID {offer_id} Address: {address}: {str(e)}<br>"
        
        driver.close()

    crawl_date = time.strftime('%Y-%m-%d')
    crawl_time = time.strftime('%H:%M:%S')
    email_success_text = "Following are the active offers which were successfully tested during today's session: <br>"
    for division, value in offers_to_test.items():
        email_success_text += f"<br>{division}:<br><br>"
        for offer_id, arr in value.items():
            if arr[0]:
                email_success_text += offer_id + " - Tested on address: " + value[offer_id][1] + "<br>"
            else:
                sql = "INSERT INTO unable_to_test_offers (timestamp, offer_id, reason) VALUES (%s, %s, %s);"
                values = (crawl_date + " " + crawl_time, offer_id, "Unable to find offer")
                mycursor.execute(sql, values)
                mydb.commit()

    address_not_found_text = "The following addresses did not find any offers:<br><br>"
    for division, text in address_not_find_offers_text_dict.items():
        address_not_found_text += text

    return ("TEST RESULTS FOR NON LOGGED IN USERS: <br><br>" + email_success_text + "<br>" + address_not_found_text + "<br>" + email_error_text), offers_to_test

def send_email(subject, text):
    sent_mail_list = ["Asher_Swing@comcast.com", "aswing358@cable.comcast.com", "olivia_shiner@comcast.com"]

    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = "offersbsee@gmail.com"
    message['To'] = ', '.join(sent_mail_list)

    
    part = MIMEText(text, 'html')
    message.attach(part)

    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login("offersbsee@gmail.com", "Comcast.g9")
    session.sendmail("offersbsee@gmail.com", sent_mail_list + ["asherswing@gmail.com", "mustansir2001@gmail.com"], message.as_string())
    session.close()


def save_screenshot_no_offers(driver, filename):
    if not os.path.isdir("no_offers_screenshots"):
        os.mkdir("no_offers_screenshots")
    driver.save_screenshot(f"no_offers_screenshot/{filename}")

if __name__ == '__main__':
    logged_in_results, logged_in_offers = run_main_loggedin()
    non_logged_in_results, non_logged_in_offers = run_main_non_loggedin()
    email_text = logged_in_results + "<br><br>" + non_logged_in_results
    email_text += "<br><br>Offers that were not found for both (Logged in and Non Logged in Users):<br>"
    for division, value in logged_in_offers.items():
        email_text += f"<br>{division}<br><br>"
        for offer_id, arr in value.items():
            if not arr[0] and not non_logged_in_offers[division][offer_id][0]:
                email_text += offer_id + "<br>"
    send_email("Offers Purchase Test on Business Site Report", email_text)
    #send_email("Testing", "Testing")
   


# %%
