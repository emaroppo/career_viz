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


def scrape_experience(browser, profile, wait_time=5):
    profile['experiences']=[]
    experience_html=browser.find_element(By.CSS_SELECTOR, '#experience').find_element(By.XPATH, '..')

    if 'Show all' in experience_html.text:
        full_exp_button=experience_html.find_element(By.CSS_SELECTOR,
                                             'span.pvs-navigation__text')
        full_exp_button.click()
        time.sleep(wait_time)

        experience_html=browser.find_element(By.CSS_SELECTOR, 'main#main > section').find_element(By.TAG_NAME, 'ul') \
            .find_elements(By.TAG_NAME, 'li')

        for i,j in enumerate(experience_html):

            try:
                experience={}
                experience['company_url']=j.find_element(By.CSS_SELECTOR, 'div > a').get_attribute('href')
                experience_data=list(sorted(set(j.text.split('\n')), key=j.text.split('\n').index))
                experience['title']=experience_data[0]
                experience['company']=experience_data[1]
                if len(experience_data)>2:
                    experience['date']=experience_data[2]
                if len(experience_data)>3:
                    experience['location']=experience_data[3]
                profile['experiences'].append(experience)

            except NoSuchElementException:
                pass
        browser.find_element(By.CSS_SELECTOR, 'main#main>section>div>button').click()
        time.sleep(wait_time)


    else:
        experience_page=experience_html.find_element(By.TAG_NAME, 'ul').find_elements(By.TAG_NAME, 'li')

        for i,j in enumerate(experience_page):

            try:
                experience={}
                experience['company_url']=j.find_element(By.CSS_SELECTOR, 'div > a').get_attribute('href')
                experience_data=list(sorted(set(j.text.split('\n')), key=j.text.split('\n').index))
                experience['title']=experience_data[0]
                experience['company']=experience_data[1]
                if len(experience_data)>2:
                    experience['date']=experience_data[2]
                if len(experience_data)>3:
                    experience['location']=experience_data[3]
                profile['experiences'].append(experience)

            except NoSuchElementException:
                pass



    return profile


def scrape_education(browser, profile, wait_time=5):
    profile['education_titles']=[]
    education_html=browser.find_element(By.CSS_SELECTOR, '#education').find_element(By.XPATH, '..')
    if 'Show all' in education_html.text:

        full_edu_history_button=education_html.find_element(By.CSS_SELECTOR,
                                                     'span.pvs-navigation__text')
        full_edu_history_button.click()
        time.sleep(wait_time)

        education_html=browser.find_element(By.CSS_SELECTOR, 'main#main > section').find_element(By.TAG_NAME, 'ul')\
            .find_elements(By.TAG_NAME, 'li')
        for i,j in enumerate(education_html):
            education_title={}

            try:
                education_title['institution_url']=j.find_element(By.CSS_SELECTOR, 'div > a').get_attribute('href')
                education_data=list(sorted(set(j.text.split('\n')), key=j.text.split('\n').index))
                education_title['institution']=education_data[0]
                education_title['title']=education_data[1]
                if len(education_data)>2:
                    education_title['date']=education_data[2]
                if len(education_data)>3:
                    education_title['notes']=education_data[3]
                profile['education_titles'].append(education_title)
            except NoSuchElementException:
                pass
        browser.find_element(By.CSS_SELECTOR, 'main#main>section>div>button').click()
        time.sleep(wait_time)

    else:
        education_page=education_html.find_element(By.TAG_NAME, 'ul').find_elements(By.TAG_NAME, 'li')
        for i,j in enumerate(education_page):
            education_title={}
            try:
                education_title['institution_url']=j.find_element(By.CSS_SELECTOR, 'div > a').get_attribute('href')
                education_data=list(sorted(set(j.text.split('\n')), key=j.text.split('\n').index))
                education_title['institution']=education_data[0]
                education_title['title']=education_data[1]
                if len(education_data)>2:
                    education_title['date']=education_data[2]
                if len(education_data)>3:
                    education_title['notes']=education_data[3]
                profile['education_titles'].append(education_title)
            except NoSuchElementException:
                pass

    return profile


def scrape_certifications(browser, profile, wait_time=5):
    profile['certifications']=[]
    cert_html=browser.find_element(By.CSS_SELECTOR, '#licenses_and_certifications').find_element(By.XPATH, '..')

    if 'Show all' in cert_html.text:
        full_cert_button=cert_html.find_element(By.CSS_SELECTOR, 'div > div > div > a > span.pvs-navigation__text')

        full_cert_button.click()
        time.sleep(wait_time)
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
        time.sleep(wait_time)

    else:
        pass

    return profile


def scrape_skills(browser,profile, wait_time=5):
    profile['skills']=[]

    skills_html=browser.find_element(By.CSS_SELECTOR, '#skills').find_element(By.XPATH, '..')

    if 'Show all' in skills_html.text:

        full_skills_button=skills_html.find_element(By.CSS_SELECTOR,
                                                     'span.pvs-navigation__text')
        full_skills_button.click()
        time.sleep(wait_time)

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
        time.sleep(wait_time)

    else:
        pass

    return profile


def scrape_profile(browser, profile, wait_time=5):

    browser.get(profile['url'])
    time.sleep(wait_time)
    profile_data=browser.find_element(By.CSS_SELECTOR, '#main')
    profile['personal_details'] = {}
    try:
        profile['personal_details']['about'] = profile_data.find_element(By.CSS_SELECTOR, '#about').find_element(By.XPATH, '..') \
            .find_elements(By.CSS_SELECTOR, 'div')[-1].text.split('\n')[-1]
    except NoSuchElementException:
        print('No about section!')

    print('scraping education...')
    try:
        profile=scrape_education(browser, profile, wait_time)
        print('done!')
    except NoSuchElementException:
        print('couldnt scrape edu')

    print('scraping job experience...')
    try:
        profile=scrape_experience(browser, profile, wait_time)
        print('done!')

    except NoSuchElementException:
        print('couldnt scrape exp')

    print('scraping certifications...')
    try:
        profile=scrape_certifications(browser, profile, wait_time)
        print('done!')

    except NoSuchElementException:
        print('couldnt scrape certifications')

    print('scraping skills...')
    try:
        profile=scrape_skills(browser, profile, wait_time)
        print('done!')
    except NoSuchElementException:
        print('couldnt scrape skill')

    print(profile)
    return profile

def main(from_scratch=False, src_path='dsr_data.json', dst_path='dsr_full_profiles.json'):

    browser=setup_browser()

    if not from_scratch:
        with open(src_path, 'r') as file:
            src_data=json.load(file)

        with open(dst_path, 'r') as file:
            dst_data=json.load(file)

        while src_data['data']:
            print(len(src_data['data']))
            try:
                profile=src_data['data'].pop()
                profile=scrape_profile(browser, profile=profile, wait_time=3)
                dst_data['data'].append(profile)
            except Exception as e:
                print(e)
                with open(src_path, 'w') as file:
                    file.write(json.dumps(src_data))

                with open(dst_path, 'w') as file:
                    file.write(json.dumps(dst_data))
                break

        return dst_data

main()
