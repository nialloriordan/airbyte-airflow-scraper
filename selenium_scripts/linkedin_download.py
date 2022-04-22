from bs4 import BeautifulSoup
import pandas as pd
import json
from selenium import webdriver


def scrape_linkedin(
    driver,
    linkedin_url,
    linkedin_username,
    linkedin_password,
    profiles_location,
    results_location,
):
    # login to Linkedin
    driver.get(linkedin_url)
    username = driver.find_element_by_id("username")
    username.send_keys(linkedin_username)
    password = driver.find_element_by_id("password")
    password.send_keys(linkedin_password)
    sign_in_button = driver.find_element_by_xpath('//*[@type="submit"]')
    sign_in_button.click()

    # load profiles
    df = pd.read_csv(profiles_location)

    # scrape data
    json_data = []
    for i in range(df.shape[0]):
        profile_url = df["profile_url"][i]
        driver.get(profile_url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        person_id = df["person_id"][i]
        name = (
            soup.find("div", {"class": "pv-text-details__left-panel"})
            .find("h1")
            .text.strip()
            .encode("ascii", "ignore")
            .decode()
        )
        position = (
            soup.find("div", {"class": "pv-text-details__left-panel"})
            .find("div", {"class": "text-body-medium break-words"})
            .text.strip()
            .encode("ascii", "ignore")
            .decode()
        )
        location = (
            soup.find("div", {"class": "pb2 pv-text-details__left-panel"})
            .find("span", {"class": "text-body-small inline t-black--light break-words"})
            .text.strip()
            .encode("ascii", "ignore")
            .decode()
        )
        company = (
            soup.find("ul", {"class": "pv-text-details__right-panel"})
            .find("h2")
            .find("div")
            .text.strip()
            .encode("ascii", "ignore")
            .decode()
        )
        try:
            connec = (
                soup.find("div", attrs={"class": "ph5"})
                .find("span", {"class": "link-without-visited-state"})
                .text.strip()
                .encode("ascii", "ignore")
                .decode()
            )
        except:
            connec = (
                soup.find("div", {"class": "ph5 pb5"})
                .find("span", {"class": "t-bold"})
                .text.strip()
                .encode("ascii", "ignore")
                .decode()
            )
        no_conn = connec.split()[0]
        no_conn = no_conn[:3]
        no_conn = int(no_conn)

        user_data = dict()
        user_data["Person ID"] = str(person_id)
        user_data["Name"] = str(name)
        user_data["Role"] = str(position)
        user_data["Location"] = str(location)
        user_data["Current Company"] = str(company)
        user_data["Number of Connections"] = int(no_conn)
        json_data.append(user_data)

    # save scraped data to json
    with open(results_location, "w") as fp:
        json.dump(json_data, fp, sort_keys=True, indent=4)
