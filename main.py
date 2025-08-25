import urllib.request
import json
import os.path
import time
import string
from unidecode import unidecode

## Definitions

ALPHABET =  string.punctuation + "1234567890" + string.ascii_uppercase

positiveAwnsers = ["yes", "y", "true", "t", "1", "yup"]  
negativeAwnsers = ["no", "n", "false", "f", "0", "nope"]    
questionsLeft = 20
questionHistory = []
answerHistory = []
remainingCards = []


CatagoryAwnsers = {  

    "Is your card a {insert}?":      ["Artifact", "Creature", "Enchantment", "Instant", "Land", "Planeswalker", "Sorcery", "Battle", "Legendary", "Snow"],
    "Is your card {insert}?":       ["White", "UBlue", "Black", "Red", "Green"],
    "Does your card have {insert}?":  ["Flying", "First strike", "Double strike", "Deathtouch", "Defender", "Haste", "Hexproof", "Indestructible", "Lifelink", "Menace", "Prowess", "Reach", "Trample", "Vigilance"],
    "Is your card legal in {insert}?":   ["Standard", "Pioneer", "Modern", "Vintage", "Commander"]    }

RangeAwnsers = {
    "Is your card's CMC less than {insert}?":         list(range(1, 5)),
    "Is your card's power less than {insert}?":       list(range(1, 13)),
    "Is your card's toughness less than {insert}?":   list(range(1, 13)),
    "Does the first letter of your card's name come before {insert} in the alphabet? (punctuation and numbers are first alphabetically)":  string.ascii_uppercase,
    "Is the price of your card less than ${insert}?":  [1, 3, 5, 10, 15, 20, 30, 50, 100, 200, 500]    }

RangeSpecificAwnsers = {
    "Is your card's CMC {insert}?":         list(range(1, 5)),
    "Is your card's power {insert}?":       list(range(1, 13)),
    "Is your card's toughness {insert}?":   list(range(1, 13)),
    "Is the first letter of your card's name {insert}?":  ALPHABET    }

TrueFalseAwnsers = { # questions that only have a true/false answer (the insert is ignored but a placeholder is needed for formatting consistency)
    "Is your card multicolored?": "tf",
    "Is your card monocolored?": "tf",
    "Is your card colorless?": "tf",
    "Is your card on the reserve list?": "tf",
    "Is your card a game changer in EDH?": "tf"     }

QuestionFuncs = { # lambda functions for each question type, takes card and insert as arguments and returns True/False
    "Is your card a {insert}?": lambda card, insert: insert in card["type_line"],
    "Is your card {insert}?":    lambda card, insert: insert in card["colors"], 
    "Does your card have {insert}?":  lambda card, insert: insert in card["keywords"], 
    "Is your card legal in {insert}?": lambda card, insert: card["legalities"][insert.lower()] == "legal", 

    "Is your card's CMC less than {insert}?":  lambda card, insert: card["cmc"] < insert,   
    "Is your card's power less than {insert}?": lambda card, insert: desymbolize(card["power"]) < int(insert),
    "Is your card's toughness less than {insert}?":  lambda card, insert: desymbolize(card["toughness"]) < int(insert),
    "Does the first letter of your card's name come before {insert} in the alphabet? (punctuation and numbers are first alphabetically)": lambda card, insert: ALPHABET.index(unidecode(card["name"][0])) < ALPHABET.index(insert),
    "Is the price of your card less than ${insert}?": lambda card, insert: True if card["prices"]["usd"] == None else float(card["prices"]["usd"]) < insert,

    "Is your card's CMC {insert}?":  lambda card, insert: card["cmc"] == insert,   
    "Is your card's power {insert}?":  lambda card, insert: card["power"] == insert,
    "Is your card's toughness {insert}?":  lambda card, insert: card["toughness"] == insert,
    "Is the first letter of your card's name {insert}?": lambda card, insert: unidecode(card["name"][0]) == insert,

    "Is your card multicolored?": lambda card, insert: len(card["colors"]) > 1,
    "Is your card monocolored?": lambda card, insert: len(card["colors"]) == 1,
    "Is your card colorless?": lambda card, insert: card["colors"] == [],
    "Is your card on the reserve list?": lambda card, insert: card["reserved"] == True,
    "Is your card a game changer in EDH?": lambda card, insert: card["game_changer"] == True   }

def desymbolize(string): # convert non-numeric power/ toughness to numeric for comparison (X = 0 etc)
    if type(string) != str:
        return string
    string = string.replace("X", "0")
    string = string.replace("*", "0")
    string = string.replace("?", "0") # ? is used in some Mystery Booster cards
    return eval(string) # eval is safe here because we control the input
                        # it will only ever be a number or a simple math expression like "1+0"

def loadData():  # Load data from cache or download fresh data from scryfall api
    if os.path.isfile("oracle-cards.json"): # if cache file exists
        if os.path.getmtime("oracle-cards.json") > time.time() - 24 * 60 * 60: # if less than 24 hours old
            with open("oracle-cards.json", mode="r", encoding="utf-8") as cache_file:
                return json.load(cache_file)
        
    print("Downloading fresh data")
    scryfallContents = urllib.request.urlopen("https://data.scryfall.io/oracle-cards/oracle-cards-20250823090430.json").read()
    data = json.loads(scryfallContents) # list of all cards in scryfall database
    usableData = []
    
    for i in data: # filter out cards that are not useful for this game (ie tokens, art series, etc)
        # un-sets aren't included becuase they have weird mechanics like non-int cmc costs
        if (i["set_type"] == "funny" or
            i["set_type"] == "memorabilia" or
            "Art Series" in i["set_name"] or
            "Token" in i["type_line"] or 
            "Card" in i["type_line"]):
            continue

        unused = ["id","all_parts", "oracle_id", "mtgo_id", "tcgplayer_id", "cardmarket_id", "lang", "uri", "layout", "highres_image", "image_status", "image_uris", "foil", "nonfoil", "finishes", "oversized", "promo", "reprint", "variation", "set_id", "set_uri", "set_search_uri", "scryfall_set_uri", "rulings_uri", "prints_search_uri", "digital", "watermark", "card_back_id", "artist_ids", "illustration_id", "border_color", "frame", "frame_effects", "security_stamp", "full_art", "textless", "booster", "story_spotlight", "edhrec_rank", "preview", "related_uris", "purchase_uris"]
        for characteristic in unused: # remove unused characteristics to save space
            if characteristic in i:
                del i[characteristic]

        usableData.append(i) # add the cleaned card to the usable data list

    with open("oracle-cards.json", mode="w", encoding="utf-8") as cache_file:
        json.dump(usableData, cache_file, indent=2) # save cleaned data to cache file

    with open("oracle-cards.json", mode="r", encoding="utf-8") as cache_file:
        data = json.load(cache_file) # reload data from cache to ensure consistency
    return data

def findQuestion(cards): # find the best question to ask to split the remaining cards in half
    
    best = [] # will contain question and insert
    bestScore = len(cards) # worst possible score, ie all questions will be better than this
    target = int(len(cards) / 2) # ideal score is half the remaining cards

    # go through each card and get a score of how many cards would answer yes to this question
    # it is aiming for a question that splits the remaining cards in half
    for questionType in [CatagoryAwnsers, RangeAwnsers, RangeSpecificAwnsers, TrueFalseAwnsers]:
        for question in questionType:
            for questionInsert in questionType[question]: # Insert is the variable part of the question (ie "Artifact" in "Is your card an Artifact?")
                score = 0
                for card in cards:
                    
                    # if card doesnt have power/ toughness, skip questions about power/toughness
                    if ((question == "Is your card's power less than {insert}?" or
                            question == "Is your card's toughness less than {insert}?" or
                            question == "Is your card's power {insert}?" or
                            question == "Is your card's toughness {insert}?") and
                            "power" not in card):
                        break

                    # if question is color and its a multifaced card, combine colors of all faces
                    elif ((question == "Is your card {insert}?" or
                            question == "Is your card multicolored?" or
                            question == "Is your card monocolored?" or
                            question == "Is your card colorless?") 
                            and "colors" not in card
                            and "card_faces" in card):
                        # create a amalgamation card with combined colors of all faces
                        amalgamationCard = {"colors": set(card["card_faces"][0]["colors"] + card["card_faces"][1]["colors"])}
                        answer = QuestionFuncs[question](amalgamationCard, questionInsert)
                        
                    # if question isnt an exception above, just ask normally
                    else:
                        answer = QuestionFuncs[question](card, questionInsert)

                    if answer:
                        score += 1

                else: # if we didn't hit a break in the inner loop (ie it wasnt an invalid question)
                    continue
                break # if we hit a break in the inner loop, break the outer loop too (ie skip this question becuase it didnt apply to at least one card)
            
            if abs(target - score) < abs(target - bestScore): # if this question is a better split than the best so far
                best = [question, questionInsert]
                bestScore = score
                if bestScore == target: # skip rest of search if perfect question found
                    return best
        
    return best


remainingCards = loadData()
    
toask = findQuestion(remainingCards)
print("Best question is: " + toask[0].format(insert = toask[1]))