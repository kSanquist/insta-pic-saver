"""
This program allows the user to input an Instagram username and a max number
of photos to scrape from the Instagram user's profile. These images are
then saved to the user's pc in a folder with the same name as the inputted
Instagram username.

Author: Kyle Sanquist
Version: 1.0
"""
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from exceptions import NoPostsException, PrivateAccountException
from selenium_cs import *
import os
import time
import requests
from ig_bot_creator import create_acc
import sys


def main():
    _cls()
    intro()


def intro(delay=0):
    """Handles command redirection"""
    _cls(delay)
    command = _get_command()
    while command is None:
        print("Your command was invalid, please try again!")
        _cls(2)
        command = _get_command()

    if command == '1':
        print("\nTaking you to ACCOUNT CREATOR...")
        acc_creation()
    elif command == '2':
        print("\nTaking you to PHOTO GRABBER...")
        grab_photos()
    else:
        print("\nEXITING PROGRAM...")
        sys.exit(0)


def conf(prompt: str) -> bool:
    print(prompt)
    confirm = input("[Y/N] : ").strip()[0].upper()
    return confirm == 'Y'


def acc_creation(redirect=False):
    _cls(2)
    print(ACC_CREATE_ART)
    confirm = conf("\nContinue with new Instagram account generation?")
    if confirm:
        _cls(2)
        create_acc.main(ACC_CREATE_ART)
        _cls(3)
        if not redirect:
            print("\nReturning to the home page...")
            intro(2)
    else:
        print("\nNo account created, returning to the home page...")
        intro(2)


def grab_photos():
    _cls(2)
    print(PHOTO_GRAB_ART)
    if os.path.getsize("./ig_bot_creator/plain_accounts.txt") == 0:  # Handles if plain_accounts.txt is empty
        confirm = conf("\nAt least one account is need to login to Instagram and grab the user's photos.\n"
                       "Would you like to go to the account creator and generate a new account?")
        if confirm:
            print("\nRedirecting to ACCOUNT CREATOR...")
            acc_creation(redirect=True)
            _cls(2)
            print(PHOTO_GRAB_ART)
        else:
            print("\nYou cannot continue without making an account before hand, returning to the home page...")
            intro(3)

    accounts = create_acc.load_accounts("./ig_bot_creator/pickled_accounts.txt")
    login_success = False
    for email, passwd in accounts.items():  # Attempts login of each account in pickled_accounts.txt until attempt works
        print(f"\nAttempting login with {email}...")
        try:
            attempt_login(email, passwd)
            print("SUCCESS!")
            login_success = True
            break
        except TimeoutException:
            print("FAILED. Account Removed")
            del accounts[email]

    if not login_success:  # Handles what happens if no accounts in pickled_accounts.txt login successfully
        print("\nAll the accounts currently saved to ./ig_bot_creator/plain_accounts.txt "
              "were unresponsive to a login attempt,\nchances are they were banned."
              "These unresponsive accounts will be removed from plain_accounts.txt\nand you "
              "will be sent back to the home page. It is recommended you make a new account\n"
              "with the ACCOUNT CREATOR before attempting to use the PHOTO GRABBER again.")
        input("\nPRESS ENTER WHEN YOU ARE READY TO HEAD HOME!")

        print("\nReturning to the home page...")
        intro(2)

    print("\nInput the username of the user you'd like to grab photos from")  # Gets username to grab photos from
    user = input("[USERNAME] : ")
    try:
        print(f"\nValidating {user}'s account...")
        driver.get(f"https://instagram.com/{user}/")
    except PrivateAccountException:
        print(f"\n{user}'s account is private, unable to get any images. Returning to the home page...")
        intro(2)
    except NoPostsException:
        print(f"\n{user}'s account has no posts, unable to get any images. Returning to the home page...")
        intro(2)
    except TimeoutException:
        print(f"\n{user}'s account could not be found, unable to get any images. Returning to the home page...")
        intro(2)

    post_count = _post_count()
    print("DONE!")
    print(f"\nInput the number of photos you'd like to grab from {user}.")
    print(f"NOTE: {user} has {post_count} posts, therefore max number of photos grabbable is {post_count}")
    while True:
        num_of_photos = input("[NUMBER OF PHOTOS] : ")  # Gets number of photos to grab
        if num_of_photos.isdigit():
            break
        print("                     Invalid Input, please enter a WHOLE NUMBER!")

    num_of_photos = post_count if post_count < int(num_of_photos) else int(num_of_photos)

    print(f"\nGrabbing {str(num_of_photos)} photos from {user}'s profile...")
    img_links = get_img_links(num_of_photos)

    print(f"\nSaving {user}'s grabbed photos to ./user_photos/{user}...")
    save_images(img_links, user)

    print(f"\nAll links have been grabbed and saved to ./user_photos/{user}/!")
    input("\nPRESS ENTER TO RETURN HOME...")

    print("\nReturning to the home screen...")
    intro(2)


def _get_command() -> str:
    print(TITLE_ART)
    cmds = ('0', '1', '2')
    print("\nType the number corresponding to one of the following options:")
    print("    ( 0 )  Exit Program")
    print("    ( 1 )  Create New Account")
    print("    ( 2 )  Grab a User's Photos")
    command = input(f"\n[{','.join(cmds)}] : ").strip()
    if (command.isdigit()) and (command in cmds):
        return command


def _cls(delay=0):
    time.sleep(delay)
    os.system('cls' if os.name == 'nt' else 'clear')


def attempt_login(email: str, passw: str):
    """Attempts to log into Instagram using email and password"""
    get_elem(driver, By.NAME, "username").send_keys(email)
    get_elem(driver, By.NAME, "password").send_keys(passw)
    get_elem(driver, By.XPATH,
             "/html/body/div[2]/div/div/div[2]/div/div/div[1]/section/main/article/div[2]/div[1]/div[2]/"
             "form/div/div[3]/button").click()
    time.sleep(5)


def get_img_links(n: int) -> list[str]:
    """Returns n image links from the user's profile. if user has m posts and
    m < n, returns m image links instead"""
    time.sleep(5)
    img_links = []
    post_count = _post_count()
    if post_count == 0:
        raise NoPostsException()
    if _is_private():
        raise PrivateAccountException()
    count = 1
    while True:
        img_elem = get_elems(driver, By.XPATH, "//img[@class='x5yr21d xu96u03 x10l6tqk x13vifvy "
                                               "x87ps6o xh8yej3']")
        for elem in img_elem:
            if len(img_links) == n:
                return img_links
            stale = True
            img_src = None
            for i in range(2):
                try:
                    img_src = elem.get_attribute("src")
                    stale = False
                    break
                except StaleElementReferenceException:
                    pass
            if stale:
                continue
            if img_src not in img_links:
                img_links.append(img_src)
                print(f"Grabbing photo {count}...")
                count += 1
                print("DONE")
        _scroll()


def _post_count() -> int:
    """Grabs the number of posts a user has"""
    time.sleep(3)
    post_count = get_elem(driver, By.XPATH,
                          "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div[2]/section/"
                          "main/div/header/section/ul/li[1]/span/span").text
    if not post_count.isdigit():
        post_count.replace(',', '')
    return int(post_count)


def _is_private() -> bool:
    """Returns whether a user's profile is private"""
    try:
        get_elem(driver, By.XPATH, "//h2[text()='This Account is Private']")
    except TimeoutException:
        return False
    return True


def _scroll(delay=1):
    """Waits 'delay' amount of time then scrolls down the page"""
    time.sleep(delay)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


def save_images(image_links: list[str], user):
    if user in os.listdir("./user_photos/"):
        if not conf(f"\n./user_photos/{user} already exists. Would you like to override it?"):
            print("No changes were made. Returning to the home page...")
            intro(2)
        else:
            os.rmdir("./user_photos/" + user)
    os.mkdir("./user_photos/" + user)
    for i, link in enumerate(image_links):
        with open(f"./user_photos/{user}/{user + str(i)}.jpg", 'wb') as handle:
            response = requests.get(link, stream=True)
            if not response.ok:
                print(response)

            for block in response.iter_content(1024):
                if not block:
                    break

                handle.write(block)


if __name__ == '__main__':
    print("\nStarting webdriver...")
    driver = start_webdriver(url="https://www.instagram.com/")
    TITLE_ART = " ___           _        ____  _      ____                       \n" \
                "|_ _|_ __  ___| |_ __ _|  _ \(_) ___/ ___|  __ ___   _____ _ __ \n" \
                " | || '_ \/ __| __/ _` | |_) | |/ __\___ \ / _` \ \ / / _ \ '__|\n" \
                " | || | | \__ \ || (_| |  __/| | (__ ___) | (_| |\ V /  __/ |   \n" \
                "|___|_| |_|___/\__\__,_|_|   |_|\___|____/ \__,_| \_/ \___|_|     "
    ACC_CREATE_ART = " ___ ____  ____           _                             _      ____                _             \n" \
                     "|_ _|  _ \/ ___|   _     / \   ___ ___ ___  _   _ _ __ | |_   / ___|_ __ ___  __ _| |_ ___  _ __ \n" \
                     " | || |_) \___ \  (_)   / _ \ / __/ __/ _ \| | | | '_ \| __| | |   | '__/ _ \/ _` | __/ _ \| '__|\n" \
                     " | ||  __/ ___) |  _   / ___ \ (_| (_| (_) | |_| | | | | |_  | |___| | |  __/ (_| | || (_) | |   \n" \
                     "|___|_|   |____/  (_) /_/   \_\___\___\___/ \__,_|_| |_|\__|  \____|_|  \___|\__,_|\__\___/|_|     "
    PHOTO_GRAB_ART = " ___ ____  ____        ____  _           _           ____           _     _               \n" \
                     "|_ _|  _ \/ ___|   _  |  _ \| |__   ___ | |_ ___    / ___|_ __ __ _| |__ | |__   ___ _ __ \n" \
                     " | || |_) \___ \  (_) | |_) | '_ \ / _ \| __/ _ \  | |  _| '__/ _` | '_ \| '_ \ / _ \ '__|\n" \
                     " | ||  __/ ___) |  _  |  __/| | | | (_) | || (_) | | |_| | | | (_| | |_) | |_) |  __/ |   \n" \
                     "|___|_|   |____/  (_) |_|   |_| |_|\___/ \__\___/   \____|_|  \__,_|_.__/|_.__/ \___|_|     "

    main()
