import urllib.request
import json
import os.path
import time
import string

def loadData():
    if os.path.isfile("oracle-cards.json"):
        if os.path.getmtime("oracle-cards.json") > time.time() - 24 * 60 * 60: # if less than 24 hours old
            with open("oracle-cards.json", mode="r", encoding="utf-8") as cache_file:
                print("Using cached data")
                return json.load(cache_file)
        
    print("Downloading fresh data")
    scryfallContents = urllib.request.urlopen("https://data.scryfall.io/oracle-cards/oracle-cards-20250823090430.json").read()
    data = json.loads(scryfallContents)
    unused = ["id","all_parts", "oracle_id", "mtgo_id", "tcgplayer_id", "cardmarket_id", "lang", "uri", "layout", "highres_image", "image_status", "image_uris", "foil", "nonfoil", "finishes", "oversized", "promo", "reprint", "variation", "set_id", "set_uri", "set_search_uri", "scryfall_set_uri", "rulings_uri", "prints_search_uri", "digital", "watermark", "card_back_id", "artist_ids", "illustration_id", "border_color", "frame", "frame_effects", "security_stamp", "full_art", "textless", "booster", "story_spotlight", "edhrec_rank", "preview", "related_uris", "purchase_uris"]
    for i in data:
        for characteristic in unused:
            try:
                del i[characteristic]
            except KeyError:
                pass
    with open("oracle-cards.json", mode="w", encoding="utf-8") as cache_file:
        json.dump(data, cache_file, indent=2)

data = loadData()
remainingCards = []
print("Start")
for card in data:
    try:
        if "G" in card["colors"]:
            remainingCards.append(card)
    except KeyError:
        pass
print("end")

insert = None

CatagoryAwnsers = {  

    "Is your card a {insert}?":      ["Artifact", "Creature", "Enchantment", "Instant", "Land", "Planeswalker", "Sorcery", "Battle", "Legendary", "Snow"],
    "Is your card {insert}?":       ["White", "UBlue", "Black", "Red", "Green"],
    "Does your card have {insert}?":  ["Flying", "First strike", "Double strike", "Deathtouch", "Defender", "Haste", "Hexproof", "Indestructible", "Lifelink", "Menace", "Prowess", "Reach", "Trample", "Vigilance"],
    "Is your card legal in {insert}?":   ["Standard", "Pioneer", "Modern", "Vintage", "Commander"]    }

RangeAwnsers = {
    "Is your card's CMC less than {insert}?":         list(range(1, 5)),
    "Is your card's power less than {insert}?":       list(range(1, 13)),
    "Is your card's toughness less than {insert}?":   list(range(1, 13)),
    "Does the first letter of your card's name come before {insert} in the alphabet?":  string.ascii_uppercase,
    "Is the price of your card less than ${insert}?":  [1, 3, 5, 10, 15, 20, 30, 50, 100, 200, 500]    }

RangeSpecificAwnsers = {
    "Is your card's CMC {insert}?":         list(range(1, 5)),
    "Is your card's power {insert}?":       list(range(1, 13)),
    "Is your card's toughness {insert}?":   list(range(1, 13)),
    "Is the first letter of your card's name {insert}?":  string.ascii_uppercase   }

TrueFalseAwnsers = {
    "Is your card multicolored?": "tf",
    "Is your card monocolored?": "tf",
    "Is your card colorless?": "tf",
    "Is your card on the reserve list?": "tf",
    "Is your card a game changer in EDH?": "tf"     }

QuestionFuncs = {
    "Is your card a {insert}?": lambda card, insert: insert in card["type_line"],
    "Is your card {insert}?":    lambda card, insert: insert in card["colors"], 
    "Does your card have {insert}?":  lambda card, insert: insert in card["keywords"], 
    "Is your card legal in {insert}?": lambda card, insert: card["legalities"][insert.lower()] == "legal", 

    "Is your card's CMC less than {insert}?":  lambda card, insert: card["cmc"] < insert,   
    "Is your card's power less than {insert}?": lambda card, insert: card["power"] < insert,
    "Is your card's toughness less than {insert}?":  lambda card, insert: card["toughness"] < insert,
    "Does the first letter of your card's name come before {insert} in the alphabet?": lambda card, insert: string.ascii_uppercase[card["name"][0]] < string.ascii_uppercase[insert],
    "Is the price of your card less than ${insert}?": lambda card, insert: card["prices"]["usd"] < insert,

    "Is your card's CMC {insert}?":  lambda card, insert: card["cmc"] == insert,   
    "Is your card's power {insert}?":  lambda card, insert: card["power"] == insert,
    "Is your card's toughness {insert}?":  lambda card, insert: card["toughness"] == insert,
    "Is the first letter of your card's name {insert}?": lambda card, insert: card["name"][0] == insert,

    "Is your card multicolored?": lambda card, insert: len(card["colors"]) > 1,
    "Is your card monocolored?": lambda card, insert: len(card["colors"]) == 1,
    "Is your card colorless?": lambda card, insert: card["colors"] == [],
    "Is your card on the reserve list?": lambda card, insert: card["reserved"] == True,
    "Is your card a game changer in EDH?": lambda card, insert: card["game_changer"] == True   }

positiveAwnsers = ["yes", "y", "true", "t", "1", "yup"]  
negativeAwnsers = ["no", "n", "false", "f", "0", "nope"]    


questionsLeft = 20

for i in CatagoryAwnsers:
    print(i.format(insert = "boo"))