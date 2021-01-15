import os
import argparse
import requests
import lxml.html
from lxml.etree import tostring
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException


def setup_argparser():
    """
    Sets up the argument parser of the program.

    @return Dictionary containing the arguments.
    """
    parser = argparse.ArgumentParser(description='Scraps google image.')
    # parser.add_argument('keyword', metavar='N', type=int, nargs='+',
    #                     help='an integer for the accumulator')
    parser.add_argument('debug', action='store_false',
                        help='Allows the debugging of the scrapper')

    args = parser.parse_args()


def setup_selenium():
    """
    Sets up the selenium driver.

    @return The selenium driver.
    """

    # ffprofile = webdriver.FirefoxProfile()
    # adblockfile = r'C:\Users\Qnouro\Downloads\adblock\adblock_plus-3.10.1-an+fx.xpi'
    # ffprofile.add_extension(adblockfile)
    # ffprofile.set_preference("extensions.adblockplus.currentVersion", "3.10.1")
    driver = webdriver.Firefox()
    #
    # sleep(5)

    return driver


def close_selenium(driver):
    """
    Safely closes the selenium driver.
    @param driver: Driver to close.
    """
    driver.close()


def scroll_website(driver, nb_iter=10, sleep_time=2):
    """
    Keeps scrolling to the bottom of the page a number of time, to trigger the
    javascript scripts loading the images.
    A sleep time is required to give the time to the script to load, between the
    scrolls.
    """
    LOAD_MORE_BUTTON_XPATH = '//input[@value="Afficher plus de résultats"]'
    END_PAGE_XPATH = "//div[text()='Fin des posts à consulter.']"

    for _ in range(nb_iter):
        # Scrolls until the bottom of the VISIBLE page.
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Check if Load More images button is available
        try:
            button = driver.find_element_by_xpath(LOAD_MORE_BUTTON_XPATH)
            button.click()

        except ElementNotInteractableException as e:
            pass

        except Exception as e:
            print(type(e), ":", e)

        # Check if we've reached the end of page
        my_element = driver.find_element_by_xpath(END_PAGE_XPATH)
        if my_element.is_displayed():
            break

        # Wait for the JS script to load
        sleep(sleep_time)

#
# def get_images_url(driver):
#     """
#     Get urls of all the images available.
#     """
#     page_html = driver.page_source
#     #
#     # soup = BeautifulSoup(page_html, 'html.parser')
#     #
#     # associated_research = soup.findAll("div", {"class": "J3Tg1d"})
#     #
#     # for div in associated_research:
#     #     print("removing...")
#     #     div.extract()
#     #
#     # mydivs = soup.findAll("img", {"class": "rg_i Q4LuWd"})
#     #
#     # assert(len(mydivs) > 0)
#
#
#     return None


def remove_div_element_by_class(driver, class_name):
    element = driver.find_elements_by_class_name(class_name)
    driver.execute_script("""
    var elements = arguments[0];
    elements.forEach(
        element => element.parentNode.removeChild(element));
    """, element)



def gather_images(driver, div, dir_name):
    """
    Gathers all the image links
    """

    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

    links_list = []

    content = driver.find_elements_by_tag_name('img')
    for index, c in enumerate(content):
        parent = c.find_element_by_xpath('..')
        if not parent.get_attribute("data-navigation"):
                # Open the full image
                c.click()
                sleep(1)

                # Go get the url
                big_image = driver.find_elements_by_class_name('n3VNCb')
                img = big_image[1]
                if index == 1:
                    img = big_image[0]
                # img = big_image[index != 1]
                link = img.get_attribute("src")
                try:
                    response = requests.get(link.rstrip())

                    with open(f"{dir_name}/{dir_name}_{index}.png", "wb") as file:
                        file.write(response.content)
                except Exception as e:
                    try:
                        link = img.get_attribute("alt")
                        response = requests.get(link.rstrip())

                        with open(f"{dir_name}/{dir_name}_{index}.png", "wb") as file:
                            file.write(response.content)
                    except Exception as e:
                        try:
                            sleep(5)
                            link = img.get_attribute("src")
                            response = requests.get(link.rstrip())

                            with open(f"{dir_name}/{dir_name}_{index}.png", "wb") as file:
                                file.write(response.content)
                        except:
                            print(e)
                            for big_im in big_image:
                                print(big_im.get_attribute("src"))
                            print("############################################################")


def main():
    args = setup_argparser()
    driver = setup_selenium()
    key_word = "black horse"
    while not key_word:
        key_word = input("Please enter a keyword to download the images: ")

    try:
        driver.get(f"https://www.google.fr/search?tbm=isch&source=hp&q={key_word}&oq={key_word}")

        scroll_website(driver, nb_iter=10)

        remove_div_element_by_class(driver, 'bMoG0d')  # Remove Ads
        remove_div_element_by_class(driver, 'J3Tg1d')  # Remove Similar Searches

        gather_images(driver, None, "black_horse")


    except Exception as e:
        print("App crashed.")
        print(e)

    finally:
        close_selenium(driver)


if __name__ == "__main__":
    main()
