from bs4 import BeautifulSoup as bs
import requests
import re

url = "http://sofifa.com/players?offset=0"


fifa_stats = [
    "Crossing",
    "Finishing",
    "Heading Accuracy",
    "Short Passing",
    "Volleys",
    "Dribbling",
    "Curve",
    "Free Kick Accuracy",
    "Long Passing",
    "Ball Control",
    "Acceleration",
    "Sprint Speed",
    "Agility",
    "Reactions",
    "Balance",
    "Shot Power",
    "Jumping",
    "Stamina",
    "Strength",
    "Long Shots",
    "Aggression",
    "Interceptions",
    "Positioning",
    "Vision",
    "Penalties",
    "Composure",
    "Marking",
    "Standing Tackle",
    "Sliding Tackle",
    "GK Diving",
    "GK Handling",
    "GK Kicking",
    "GK Positioning",
    "GK Reflexes",
]


def soup_maker(url):
    r = requests.get(url)
    markup = r.content
    soup = bs(markup, "lxml")
    return soup


def find_top_players(soup):
    final_details = {}
    table = soup.find("table", {"class": "table table-hover persist-area"})
    tbody = table.find("tbody")
    all_a = tbody.find_all("a", {"class": "", "role": "tooltip"})
    for player in all_a:
        try:
            final_details["short_name"] = player.text
            final_details.update(
                player_all_details("http://sofifa.com" + player["href"])
            )
        except Exception as e:
            print(f"Error in finding for {player.text}")
            print(f"Error: {e}")
            raise
        else:
            print(f"Successfully found for {player.text}")


def find_player_info(soup):
    player_data = {}
    player_data["image"] = soup.find("img")["data-src"]
    player_data["full_name"] = soup.find("h1").text.split(" (")[0]
    # span = soup.find("span", attrs={"class": "pos"}).text.strip()
    span = soup.find("div", attrs={"class": "meta ellipsis"}).text.strip()
    dob = re.search("(\(.*)\)", span).group(0)
    player_data["dob"] = dob.replace("(", "").replace(")", "")
    infos = span.replace(dob + " ", "").split(" ")
    player_data["pref_pos"] = infos[0]
    for info in infos:
        age_yo = re.search("y.o.", info)
        if age_yo is not None:
            player_data["age"] = int(info.replace("y.o.", ""))
        height = re.search("(.*)cm", info)
        if height is not None:
            player_data["height"] = int(info.replace("cm", ""))
        weight = re.search("(.*)kg", info)
        if weight is not None:
            player_data["weight"] = int(info.replace("kg", ""))
    player_data["country"] = soup.find("a", attrs={"rel": "nofollow"}).title
    return player_data


def find_player_stats(soup):
    player_data = {}
    info = re.findall("\d+", soup.text)
    player_data["rating"] = int(info[0])
    player_data["potential"] = int(info[1])
    player_data["value"] = int(info[2])
    player_data["wage"] = int(info[3])
    return player_data


def find_player_secondary_info(soup):
    player_data = {}
    player_data["preff_foot"] = soup.find(
        "label", text="Preferred Foot"
    ).next_sibling.text
    player_data["club"] = (
        soup.find_all("div", attrs={"class": "card"})[-1].find("a").text
    )
    player_data["club_pos"] = (
        soup.find("label", text="Position").parent.find("span").text
    )
    player_data["club_jersey"] = soup.find("label", text="Kit Number").next_sibling.text
    if soup.find("label", text="Joined"):
        player_data["club_joined"] = soup.find("label", text="Joined").next_sibling.text
    if soup.find(
        "label", text="Contract Valid Until"
    ):
        player_data["contract_valid"] = soup.find(
            "label", text="Contract Valid Until"
        ).next_sibling.text
    return player_data


def find_fifa_info(soup):
    player_data = {}
    divs_without_skill = soup.find_all("div", {"class": "card"})[:3]
    more_lis = [div.find_all("li") for div in divs_without_skill]
    # lis = soup.find_all("li") + more_lis[0]
    lis = more_lis[0]
    for li in lis:
        for stats in fifa_stats:
            if stats in li.text:
                player_data[stats.replace(" ", "_").lower()] = int(
                    re.split(r"\D+",(li.text.split(" ")[0]).replace("\n", ""))[0]
                )
    traits = soup.find("h4", text="Traits")
    if traits:
        player_data["traits"] = [
            li.text.replace("\xa0", "")
            for li in traits.parent.next_sibling.next_sibling.find_all("li")
        ]
    specialities = soup.find("h4", text="Specialities")
    if specialities:
        player_data["specialities"] = [
            li.text.replace("\xa0", "")
            for li in specialities.parent.next_sibling.next_sibling.find_all("li")
        ]
    return player_data


def player_all_details(url):
    all_details = {}
    soup = soup_maker(url)
    player_info = soup.find("div", {"class": "player"})
    all_details.update(find_player_info(player_info))
    player_stats = soup.find("section", {"class": "card spacing"})
    all_details.update(find_player_stats(player_stats))
    secondary_info = soup.find_all("div", {"class": "col col-12"})[0]
    all_details.update(find_player_secondary_info(secondary_info))
    fifa_info = soup.find_all("div", {"class": "col col-12"})[1]
    all_details.update(find_fifa_info(fifa_info))
    return all_details


soup = soup_maker(url)
find_top_players(soup)
