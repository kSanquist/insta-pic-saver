import os
import random
import string
import pickle
import time
import selenium_cs as cs
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select

driver = cs.start_webdriver("https://www.instagram.com/accounts/emailsignup/")

# Main, seen it a million times. BORING!
def main(ACC_CREATE_ART):
    cs.load_ua()

    accounts = load_accounts("./ig_bot_creator/pickled_accounts.txt")

    print(ACC_CREATE_ART)
    print("\nStarting Account Creation...")

    print("\nGenerating Credentials...")
    email = get_email()
    name, username = create_name()
    password = create_password()
    print("DONE")

    print("\nInputting Credentials...")
    input_credentials(email, name, username, password)

    print("\nAccount Created Successfully!")
    print(f"   email : {email} \npassword : {password}")

    accounts[email] = password
    save_accounts(accounts_=accounts, pickled_txt="./ig_bot_creator/pickled_accounts.txt",
                  plain_txt="./ig_bot_creator/plain_accounts.txt")

    input("\nPRESS ENTER TO CONTINUE...")


def get_email() -> str:
    """Uses incognitomail.com to generate a temporary email for the bot"""
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get("https://incognitomail.co/")
    time.sleep(5)
    email = cs.get_elem(driver, By.XPATH, "//*[@id='root']/div/div[2]/div/div/div[1]/div/span").text
    return email


def create_password() -> str:
    """Creates password for the bot (12 random letters and numbers)"""
    password_characters = string.ascii_letters + string.digits
    return ''.join(random.choice(password_characters) for _ in range(12))


def create_name() -> tuple:
    """Randomly grabs two names from names.txt for bot's full name."""
    '''Also creates bot's username: firstname_lastname[random # 1000 - 9999]'''
    with open('./ig_bot_creator/names.txt', 'r') as f:
        names = [name[:-1] for name in f]
        name_list = random.choices(names, k=2)

    name = name_list[0] + ' ' + name_list[1]
    username = name_list[0] + '_' + name_list[1] + str(random.randint(1000, 9999))

    return name, username


def input_credentials(email: str, name: str, username: str, password: str):
    """Inputs all the previously generated sign-up info into Instagram and"""
    '''handles confirmation code'''
    driver.switch_to.window(driver.window_handles[0])

    cs.get_elem(driver, By.NAME, "emailOrPhone").send_keys(email)  # email
    cs.get_elem(driver, By.NAME, "fullName").send_keys(name)  # name
    username_in = cs.get_elem(driver, By.NAME, "username").send_keys(username)  # username
    cs.get_elem(driver, By.NAME, "password").send_keys(password)  # password
    while True:  # Checks to make sure username is allowed
        try:
            cs.get_elem(driver, By.XPATH,
                        "//*[@id='mount_0_0_OW']/div/div/div[2]/div/div/div/div[1]/section/main/div/div/div[1]/"
                        "div[2]/form/div[6]/div/div/span")
            username_in.clear()
            new_username = username[:-4] + str(random.randint(1000, 9999))
            username_in.send_keys(new_username)
        except TimeoutException:
            break

    cs.get_elem(driver, By.CSS_SELECTOR, "button[type='submit']").click()

    add_birthday()  # Birthday input
    print("DONE")

    # Confirmation code
    print("\nDealing With Confirmation Code...")
    conf_code = get_conf_code()
    driver.switch_to.window(driver.window_handles[0])
    cs.get_elem(driver, By.NAME, "email_confirmation_code").send_keys(conf_code)
    cs.get_elem(driver, By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/section/main/div/div/div[1]/"
                                  "div[2]/form/div/div[2]/div").click()
    print("DONE")


def add_birthday():
    """Gets random number from birth month, day, and year for the bot."""
    titles = {'Month:': (1, 12), 'Day:': (1, 28), 'Year:': (1940, 2004)}

    for title, rng in titles.items():
        select_elem = cs.get_elem(driver, By.CSS_SELECTOR, f"select[title='{title}']")
        select = Select(select_elem)
        select.select_by_value(str(random.randint(rng[0], rng[1])))

    cs.get_elem(driver, By.XPATH,
                "/html/body/div[2]/div/div/div[2]/div/div/div[1]/section/main/div/div/div[1]/div/div[6]/button").click()


def get_conf_code() -> str:
    """Loops through bot's temporary email until confirmation code appears"""
    driver.switch_to.window(driver.window_handles[1])
    while True:
        try:
            email_subject = cs.get_elem(driver, By.CLASS_NAME, "dataSubject").text
            code = email_subject.split(' ')[0]
            return code
        except TimeoutException:
            continue


def load_accounts(txt_file: str) -> dict[str, str]:
    """Unpickles picked_accounts.txt"""
    accounts = {}
    if os.path.getsize(txt_file) != 0:
        with open(txt_file, 'rb') as f:
            accounts = pickle.load(f)
    return accounts


def save_accounts(accounts_: dict, pickled_txt: str, plain_txt: str):
    """Pickles accounts dict to pickled_accounts.txt and saves readable"""
    '''account info String to plain_accounts.txt'''
    with open(pickled_txt, 'wb') as f:
        pickle.dump(accounts_, f)

    with open(plain_txt, "w") as f:
        for email, passwd in accounts_.items():
            f.write(f"   email : {email} \npassword : {passwd}\n\n")


if __name__ == '__main__':
    main()
