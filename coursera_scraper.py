import json
from random import randint
from time import sleep
from shutil import which
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_options = Options()
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_experimental_option('useAutomationExtension', False)
# chrome_options.add_argument("--headless")   # comment it out if you want to see what's happening.

search = input('Enter Search Words: ')
search_term = search.replace('+','%2B').replace(' ','%20').replace('(','%28').replace(')','%29').replace('/','%2F').replace('&','%26').replace("'","%27").replace(',','%2C').replace(':','%3A').replace(';','%3B').replace('=','%3D').replace('?','%3F').replace('@','%40').replace('*','%2A').replace('!','%20').replace('#','%23').replace('$','%24')
chrome_path = which("chromedriver")
driver = webdriver.Chrome(executable_path=chrome_path, options= chrome_options)
driver.maximize_window()

def login():
    print('logging in...')
    url = 'https://www.coursera.org/login?redirectTo=%2F' # login page url
    driver.get(url)
    sleep(1)
    driver.find_element_by_xpath("//*[@id='email']").send_keys('fiverrscrapy@hotmail.com') # putting email
    driver.find_element_by_xpath("//*[@id='password']").send_keys('fiverrscrapy') # putting password
    sleep(1)
    driver.find_element_by_xpath("//*[@id='rendered-content']/div/div/div/div/div/section/section/div[1]/form/button").click() #clicking the login button
    sleep(1)

def backup_login():
    print('Using another Login option..')
    url = 'https://www.coursera.org/login?redirectTo=%2F' # login page url
    driver.get(url)
    main_page = driver.current_window_handle

    driver.find_elements_by_xpath("//section[@class='_dfm2a9']/button")[1].click()
    sleep(3)
    for handle in driver.window_handles:
        if handle != main_page:
            login_page = handle
            
    # change the control to signin page       
    driver.switch_to.window(login_page)

    driver.find_element_by_id('email').send_keys('banglabokbok420@gmail.com')
    driver.find_element_by_id('pass').send_keys('5rVQ&FSR')
    driver.find_element_by_xpath("//input[@type='submit']").click()
    sleep(1)
    try:
        driver.find_element_by_xpath("//div[@class='bp9cbjyn j83agx80 taijpn5t c4xchbtz by2jbhx6 a0jftqn4']").click()
    except:
        pass
    driver.switch_to.window(main_page)
    sleep(2)






def scrape():
    link_list = []
    print(f'seaching for {search} courses...')
    sleep(1)
    driver.get(f'https://www.coursera.org/search?query={search_term}&tab=all') # searching for all courses available in searched category
    if driver.find_element_by_xpath("//a[@data-click-key='search.search.click.header_right_nav_button']").text == 'Log In':
        backup_login()
        driver.get(f'https://www.coursera.org/search?query={search_term}&tab=all')
    print('collecting links from first page...')
    links = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//li[@class='ais-InfiniteHits-item']/div/div/a")) # collecting all links in a list
    )


    for link in links:
        link_list.append(link.get_attribute('href'))

    print('collecting links from second page...')
    driver.get(f"https://www.coursera.org/search?query={search_term}&page=2&index=prod_all_launched_products_term_optimization") # going to second page
    links = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//li[@class='ais-InfiniteHits-item']/div/div/a")) # collecting all links
    )
    for link in links:
        link_list.append(link.get_attribute('href'))


    data = {}
    lists = []




# ----------------------scraping each courses------------------------------------------------------------------------------
    print(f'Total {len(link_list)} course links found...')
    s = 1
    for link in link_list:
        print(f'scraping link {s}')
        s = s + 1
        driver.get(link)
        title = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//h1[contains(@class,'banner-title')]")) # collecting all links
        )
        title = title.text
        

        if driver.find_element_by_xpath("//button[@data-track-component='enroll_button']").text == 'Zum Kurs':
            free_or_paid = 'Free'
        else:
            link_suffix = link.replace('https://www.coursera.org','')
            check_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//form[@action='{link_suffix}']/button")) # collecting all links
            )
            driver.implicitly_wait(1)
            check_button.click()
            sleep(1)
            # driver.find_element_by_xpath(f"//form[@action='{link_suffix}']/button").click()
            
            free_check = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='c-modal-content']/div")) # collecting all links
            )
            free_check = free_check.get_attribute('class')
            # free_check = driver.find_element_by_xpath("//div[@class='c-modal-content']/div").get_attribute('class')
            if free_check == 'enrollmentChoiceContainer':
                if driver.find_elements_by_xpath("//div[@class='c-modal-content']/div/div")[1].get_attribute('class') == 'cem-body':
                    free_or_paid = 'Free'
                else:
                    free_or_paid = 'Paid'
            elif free_check == 'enroll-modal-container':
                if len(driver.find_elements_by_xpath("//div[@class='c-modal-content']/div/div"))==3:
                    free_or_paid = 'Free'
                else:
                    free_or_paid = 'Paid'
        
        if free_or_paid == 'Free':
            data = {
                'Course Title': title,
                'Course Url': link,
                'Status': 'Free'
            }
            lists.append(data)

    with open("Free_courses.json", "w") as outfile:
        json.dump(lists, outfile)


login()
scrape()