from selenium import webdriver
from bs4 import BeautifulSoup

import time


def setup_driver(driver_path: str) -> webdriver:
    """Creates a driver object given the path of the webdriver.
    @param driver_path: the local path to the local Chrome webdriver
    @return the driver object"""
    driver = webdriver.Chrome(executable_path=driver_path)
    driver.get("https://www.indeed.com/advanced_search")
    return driver


def open_buzzwords(file_name) -> list:
    """Creates a list of buzzwords from a text file.
    @param file_name: the path to the local list of words
    @return a list of words"""
    buzz_list = []
    open_file = open(file_name)
    for line in open_file:
        new_term = line.rstrip()
        buzz_list.append(new_term)

    open_file.close()
    return buzz_list


def search_indeed(driver: webdriver) -> None:
    """Searches indeed given search terms."""
    WHAT = "software engineer intern"
    WHERE = ""
    NOT = ""

    input_what = driver.find_element_by_id('as_and')
    input_what.send_keys(WHAT)

    input_not = driver.find_element_by_id('as_not')
    input_not.send_keys(NOT)

    input_where = driver.find_element_by_id('where')
    input_where.send_keys(WHERE)

    results = driver.find_element_by_xpath('//select[@id="limit"]//option[@value=20]')
    results.click()

    sort = driver.find_element_by_xpath('//select[@id="sort"]//option[@value="date"]')
    sort.click()

    submit = driver.find_element_by_xpath('//*[@id="fj"]')
    submit.click()


def parse_job_text(job_text: str, search_terms: str) -> list:
    """Searches through a job description for search terms, returning a list of found words.
    @param: job_text: a string of the job description
    @param: search_terms: a list of words to search for.
    @return: a list of words found in the job description."""
    results_list = []

    for term in search_terms:
        if job_text.find(term) != -1:
            results_list.append(term)

    if len(results_list) != 0:
        print(results_list)
    return results_list


def search_job(driver: webdriver) -> str:
    """Switches to the iframe, extracts the job description, and swaps to the main.
    @param: driver: the webdriver
    @return: the job text description."""
    driver.switch_to.frame("vjs-container-iframe")

    raw_description = driver.find_element_by_id("jobDescriptionText").get_attribute("innerHTML")
    job_text_str_raw = BeautifulSoup(raw_description, features='html.parser').get_text()
    job_text = job_text_str_raw.strip('\n')

    driver.switch_to.parent_frame()

    return job_text


def list_jobs(driver: webdriver) -> list:
    """Returns a list of the job cards on the website.
    Used to bypass stale elements.
    @param: driver: the webdriver.
    @return: a list of job cards"""
    jobs = driver.find_elements_by_xpath('//a[@data-hiring-event="false"]')
    return jobs


def close_popup_first(driver: webdriver) -> None:
    driver.find_element_by_xpath('//button[@class="popover-x-button-close icl-CloseButton"]')


def search_jobs(driver: webdriver, buzzwords_file):
    """Searches through all jobs on one page and returns a list of lists containing the key terms.
    @param: driver: the Chrome webdriver
    @param: buzzwords_file: the file containing the key words
    @return: a list of list containing the found words in each job."""
    total_list = []

    job_count = len(list_jobs(driver))

    for i in range(0, job_count):
        try:
            job_list = list_jobs(driver)
            job_list[i].click()
            job_txt = search_job(driver)
            results = parse_job_text(job_txt, buzzwords_file)
            if len(results) != 0:
                total_list.append(results)
            time.sleep(1)
        except IndexError:
            close_popup_first(driver)

    return total_list


if __name__ == "__main__":
    buzzword_list = open_buzzwords('buzzwords.txt')
    indeed_driver = setup_driver('/Users/MKND/Desktop/chromedriver.exe')
    search_indeed(indeed_driver)

    resulting_list = search_jobs(indeed_driver, buzzword_list)

    print(resulting_list)
    indeed_driver.close()
