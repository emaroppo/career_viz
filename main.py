from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import json
import os
import pickle
import requests
import time


def get_login_cookies(browser):
    browser.get('https://www.linkedin.com/login')
    input('Please login on browser (press enter when done)')
    cookies = browser.get_cookies()
    pickle.dump(cookies, open('linkedin_cookies.pkl',"wb"))

    return cookies


def setup_browser(cookie_path='linkedin_cookies.pkl'):
    browser = webdriver.Chrome('/usr/local/bin/chromedriver')

    if cookie_path in os.listdir():
        login_cookies=pickle.load(open('linkedin_cookies.pkl', 'rb'))
    else:
        login_cookies=get_login_cookies(browser)

    browser.get('https://www.linkedin.com/')

    for cookie in login_cookies:
        browser.add_cookie(cookie)
    return browser

def scrape_people(browser):
    browser.get('https://www.linkedin.com/school/data-science-retreat/people/')
    dsr_people = []

    while len(dsr_people) < 300:
        people = browser.find_elements(By.CSS_SELECTOR,
                                     '#main > div > div > div > div > div.scaffold-finite-scroll__content > ul > li')
        for i in people:
            dsr_people.append(i)
            dsr_people=list(set(dsr_people))


        page=browser.find_element(By.TAG_NAME, 'body')
        page.send_keys(Keys.END)
        time.sleep(2)

    data={'data':[]}

    for j in dsr_people:

        try:
            url=j.find_element(By.CSS_SELECTOR, 'div > section > div > div > div > div > a').get_attribute('href')
            name=j.find_element(By.CSS_SELECTOR, 'div > section > div > div > div > div > a').text
            data['data'].append({'name':name, 'url':url})
        except NoSuchElementException:
            pass

    with open('dsr_data.json', 'w+') as file:
        file.write(json.dumps(data))
    return data


def scrape_experience(browser, profile):
    profile['experiences']=[]
    experience_html=browser.find_element(By.CSS_SELECTOR, '#experience').find_element(By.XPATH, '..')

    if 'Show all' in experience_html.text:
        full_exp_button=experience_html.find_element(By.CSS_SELECTOR,
                                             'span.pvs-navigation__text')
        full_exp_button.click()
        time.sleep(5)

        experience_html=browser.find_element(By.CSS_SELECTOR, 'main#main > section').find_element(By.TAG_NAME, 'ul') \
            .find_elements(By.TAG_NAME, 'li')

        for i,j in enumerate(experience_html):

            try:
                experience={}
                experience['company_url']=j.find_element(By.CSS_SELECTOR, 'div > a').get_attribute('href')
                experience_data=list(sorted(set(j.text.split('\n')), key=j.text.split('\n').index))
                experience['title']=experience_data[0]
                experience['company']=experience_data[1]
                experience['date']=experience_data[2]
                experience['location']=experience_data[3]
                profile['experiences'].append(experience)

            except NoSuchElementException:
                pass
        browser.find_element(By.CSS_SELECTOR, 'main#main>section>div>button').click()
        time.sleep(5)


    else:
        experience_page=experience_html.find_element(By.TAG_NAME, 'ul').find_elements(By.TAG_NAME, 'li')

        for i,j in enumerate(experience_page):

            try:
                experience={}
                experience['company_url']=j.find_element(By.CSS_SELECTOR, 'div > a').get_attribute('href')
                experience_data=list(sorted(set(j.text.split('\n')), key=j.text.split('\n').index))
                experience['title']=experience_data[0]
                experience['company']=experience_data[1]
                experience['date']=experience_data[2]
                experience['location']=experience_data[3]
                profile['experiences'].append(experience)

            except NoSuchElementException:
                pass



    return profile


def scrape_education(browser, profile):
    profile['education_titles']=[]
    education_html=browser.find_element(By.CSS_SELECTOR, '#education').find_element(By.XPATH, '..')
    if 'Show all' in education_html.text:

        full_edu_history_button=education_html.find_element(By.CSS_SELECTOR,
                                                     'span.pvs-navigation__text')
        full_edu_history_button.click()
        time.sleep(5)

        education_html=browser.find_element(By.CSS_SELECTOR, 'main#main > section').find_element(By.TAG_NAME, 'ul')\
            .find_elements(By.TAG_NAME, 'li')
        for i,j in enumerate(education_html):
            education_title={}

            try:
                education_title['institution_url']=j.find_element(By.CSS_SELECTOR, 'div > a').get_attribute('href')
                education_data=list(sorted(set(j.text.split('\n')), key=j.text.split('\n').index))
                education_title['institution']=education_data[0]
                education_title['title']=education_data[1]
                education_title['date']=education_data[2]
                if len(education_data)>3:
                    education_title['notes']=education_data[3]
                profile['education_titles'].append(education_title)
            except NoSuchElementException:
                pass
        browser.find_element(By.CSS_SELECTOR, 'main#main>section>div>button').click()
        time.sleep(5)

    else:
        education_page=education_html.find_element(By.TAG_NAME, 'ul').find_elements(By.TAG_NAME, 'li')
        for i,j in enumerate(education_page):
            education_title={}

            try:
                education_title['institution_url']=j.find_element(By.CSS_SELECTOR, 'div > a').get_attribute('href')
                education_data=list(sorted(set(j.text.split('\n')), key=j.text.split('\n').index))
                education_title['institution']=education_data[0]
                education_title['title']=education_data[1]
                education_title['date']=education_data[2]
                if len(education_data)>3:
                    education_title['notes']=education_data[3]
                profile['education_titles'].append(education_title)
            except NoSuchElementException:
                pass
        print(profile['education_titles'])

    return profile


def scrape_certifications(browser, profile):
    profile['certifications']=[]
    cert_html=browser.find_element(By.CSS_SELECTOR, '#licenses_and_certifications').find_element(By.XPATH, '..')

    if 'Show all' in cert_html.text:
        full_cert_button=cert_html.find_element(By.CSS_SELECTOR, 'div > div > div > a > span.pvs-navigation__text')

        full_cert_button.click()
        time.sleep(5)
        full_cert_html=browser.find_element(By.CSS_SELECTOR, 'main#main > section').find_element(By.TAG_NAME, 'ul') \
            .find_elements(By.TAG_NAME, 'li')

        for i,j in enumerate(full_cert_html):
            certification={}

            try:
                if j.text != 'Show credential':
                    certification['institution_url'] = j.find_element(By.CSS_SELECTOR, 'div > a').get_attribute('href')
                    certification_data = list(sorted(set(j.text.split('\n')), key=j.text.split('\n').index))
                    certification['title'] = certification_data[0]
                    certification['institution'] = certification_data[1]
                    certification['date'] = certification_data[2]
                    profile['certifications'].append(certification)
            except NoSuchElementException:
                pass

        browser.find_element(By.CSS_SELECTOR, 'main#main>section>div>button').click()
        time.sleep(5)

    else:
        pass

    return profile

def scrape_skills(browser,profile):
    profile['skills']=[]

    skills_html=browser.find_element(By.CSS_SELECTOR, '#skills').find_element(By.XPATH, '..')

    if 'Show all' in skills_html.text:

        full_skills_button=skills_html.find_element(By.CSS_SELECTOR,
                                                     'span.pvs-navigation__text')
        full_skills_button.click()
        time.sleep(5)

        skills_html=browser.find_element(By.CSS_SELECTOR, 'main#main > section').find_element(By.TAG_NAME, 'ul') \
            .find_elements(By.XPATH, './li')
        for i,j in enumerate(skills_html):
            try:
                if j.text:
                    k=j.text.split("\n")[0]
                    profile['skills'].append(k)

            except NoSuchElementException:
                pass


        browser.find_element(By.CSS_SELECTOR, 'main#main>section>div>button').click()
        time.sleep(5)

    else:
        pass

    return profile


def scrape_profile(url):

    browser=setup_browser()

    url='https://www.linkedin.com/in/naokishibuya/'
    browser.get(url)
    time.sleep(4)
    profile_data=browser.find_element(By.CSS_SELECTOR, '#main')
    profile = {}
    profile['personal_details'] = {}

    profile['personal_details']['about'] = profile_data.find_element(By.CSS_SELECTOR, '#about').find_element(By.XPATH, '..') \
        .find_elements(By.CSS_SELECTOR, 'div')[-1].text.split('\n')[-1]

    print('scraping education...')
    try:
        profile=scrape_education(browser, profile)
        print('done!')
    except NoSuchElementException:
        print('couldnt scrape edu')

    print('scraping job experience...')
    try:
        profile=scrape_experience(browser, profile)
        print('done!')

    except NoSuchElementException:
        print('couldnt scrape exp')

    print('scraping certifications...')
    try:
        profile=scrape_certifications(browser, profile)
        print('done!')

    except NoSuchElementException:
        print('couldnt scrape certifications')

    print('scraping skills...')
    try:
        profile=scrape_skills(browser, profile)
        print('done!')
    except NoSuchElementException:
        print('couldnt scrape skill')

    print(profile)
    return profile

scrape_profile('

'''
def main(from_scratch=False, src_file='dsr_data.json'):
    browser=setup_browser()
    
    url='https://www.linkedin.com/in/naokishibuya/'
    browser.get(url)
    time.sleep(4)
    profile_data=browser.find_element(By.CSS_SELECTOR, '#main')
    
    profile={}
    profile['personal_details']={}
    
    profile['personal_details']['about']=profile_data.find_element(By.CSS_SELECTOR, '#about').find_element(By.XPATH, '..') \
        .find_elements(By.CSS_SELECTOR, 'div')[-1].text.split('\n')[-1]
'''

