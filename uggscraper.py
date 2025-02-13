from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

TIER_LIST_URL = "https://u.gg/lol/tier-list"

class UggScraper:

    def __init__(self):
        self.driver = self.prepare_driver()
        self.champions = []
        self.champ_names = set()
        self.champ_roles = ["Top", "Mid", "ADC", "Jungle", "Support"]
        self.scrape_champ_data()
        print("Scraping complete!")


    def prepare_driver(self):
        
        # Run Chrome in headless mode, and ignore certificates
        options = Options()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--allow-insecure-localhost')
        options.add_argument('--ignore-urlfetcher-cert-requests')
        options.add_argument("--headless=new")

        # Initialize Chromedriver
        return webdriver.Chrome(options=options)


    def scrape_champ_data(self):

        # Navigate to the u.gg URL
        self.driver.get(TIER_LIST_URL)
        
        # Get the table of champion data
        champ_table = self.driver.find_element(By.XPATH, "//div[@role = 'rowgroup'][@class = 'rt-tbody']")

        while True:

            # Scroll to the bottom of the page to load more champions
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # If no additional champions have been loaded, then we are done
            champ_rows = champ_table.find_elements(By.XPATH, "//div[@class = 'rt-tr-group xs:max-sm:flex']")
            if len(champ_rows) == len(self.champions):
                break
            
            # Else, iterate through all the newly loaded champions
            for champ_row in champ_rows[len(self.champions):]:

                # Split the champion info (excluding role) by newline characters
                champ_info = champ_row.text.splitlines()

                # Save the champion info as a dictionary
                champion = {}
                champion["rank"] = champ_info[0]
                champion["name"] = champ_info[1]
                champion["role"] = champ_row.find_element(By.XPATH, ".//img[@class = 'w-[20px] h-[20px]']").get_attribute("alt").capitalize()
                champion["tier"] = champ_info[2]
                champion["win_rate"] = champ_info[3]
                champion["pick_rate"] = champ_info[4]
                champion["ban_rate"] = champ_info[5]

                # Exception: if the role is ADC, capitalize ALL letters
                if champion["role"] == "Adc":
                    champion["role"] = "ADC"

                self.champions.append(champion)
                self.champ_names.add(champion["name"])


    def get_matchup_data(self, champ_name, champ_role=None):

        # Generate a URL for this champion's matchup page
        counters_url = f'https://u.gg/lol/champions/{champ_name.lower()}/counter'

        # If a role is specified for this champion, add it. Otherwise, request the most common role
        if champ_role:
            # u.gg uses keyword "middle" instead of "mid" in its url query, so accomodate this
            counters_url += f'?role={champ_role.lower() if champ_role.lower() != "mid" else "middle"}'

        # Navigate to the matchup page and get the column of matchup winrates
        self.driver.get(counters_url)
        matchup_column = self.driver.find_element(By.XPATH, "//div[@class = 'counters-list best-win-rate']")

        # Click on the "See More Champions" button to load all matchups
        matchup_column.find_element(By.XPATH, ".//div[@class = 'view-more-btn']").click()

        # Create a list of matchups. Each matchup is a tuple (name, win rate)
        counters = []

        # Extract matchup data from each row
        for matchup_row in matchup_column.find_elements(By.TAG_NAME, "a"):
            
            # Split the matchup data by newline characters and add a (name, win rate) tuple to the list
            matchup_info = matchup_row.text.splitlines()
            counters.append((matchup_info[0], matchup_info[1]))

        # If the default champ role was requested, find out what this "default" role is
        if not champ_role:
            champ_role = self.driver.find_element(By.XPATH, "//span[@class = 'champion-title']").text[12:]

        # Return this champion's role and matchup data
        return champ_role, counters
    

    def quit(self):
        self.driver.quit()
