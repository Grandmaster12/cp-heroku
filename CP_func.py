# code file that imports the pre-written data, runs the randomiser, and makes the OpenAI calls
import random, re, openai, os
from boto.s3.connection import S3Connection

try: 
    openai.api_key = S3Connection(os.environ['S3_KEY'])
except:
    from dotenv import load_dotenv
    load_dotenv()
    openai.api_key = os.getenv("API_KEY")

# file names
files = ["classes", "races", "backgrounds", "subraces", "subclasses", "personalities", "moods"]

# store the information from the Player's Handbook and options for personality, mood, and motivation
database = {}

# import files from the list
def get_info():
    
    # iterate through all the file names
    for file_name in files:
        
         # open them to read information out of
        with open("text/" + file_name + '.txt', 'r') as file:
            
            # create an empty list in the database using the file name as the key
            database[file_name] = []
            
            # append each line to the list, removing any trailing whitespace
            for line in file.readlines():
                database[file_name].append(line.rstrip())

get_info()


# write each alignment and save it to the database too
alignments = [
    "Lawful Good",
    "Lawful Neutral",
    "Lawful Evil",
    "Neutral Good",
    "True Neutral",
    "Neutral Evil",
    "Chaotic Good",
    "Chaotic Neutral",
    "Chaotic Evil"]

database["alignments"] = alignments


# import motivations from text file
motiv_string = ""
with open("text/motivations.txt", 'r') as file:
    for line in file.readlines():
                motiv_string += line

# define the pattern to isolate the main motivation headings from the list
pattern = "\d+[.].+[.]"

# use the pattern to find all 50 motivations from the text
motivs = re.findall(pattern, motiv_string)

# use a lambda function to remove the initial number, period, and space, and the ending fullstop
database["motivations"] = list(map(lambda motiv: motiv[motiv.find(".")+2 : -1], motivs))


# importing race-specific names:
# defining the list of race names to import, except humans and half-elves
race_list = [race.lower() for race in database["races"][:] if race not in ["Human", "Half-Elf"]]

# creating a function that iterates through all races and creates a dictionary of names for each one
def get_race_names():
    """
    Each line in the file {race_name}.txt has the same structure:
    Male: [list of male first names]
    Female: [list of female first names]
    Last: [list of family/clan/last names]
    
    Exceptions:
    Elves have their last names followed by their English translations in brackets
    Gnomes have an additional name category - Nicknames - because they usually go by their nicknames and a first and last name.
    Tieflings might choose a name for themselves based on a concept or virtue that they want to live out in their lives,
        so they have an additional Concept category.
    """
    # final dictionary of names for each race
    race_names = {}
    
    # iterate through races
    for race in race_list:

        # create intermediate dictionary for each file
        temp_dict = {}
        
        # read the file and all its lines
        with open(f'text/names/{race}_names.txt', 'r') as file:
            
            # iterate through the lines - each line is 
            for line in file.readlines():
                
                # divide the lines up by the colon indicating the category, remove trailing whitespace, and store category and list
                key, val = line.rstrip().split(": ")
                
                # store the names list as a value in a dictionary with the category as the key 
                temp_dict[key] = val.split(", ")
        
        race_names[race] = temp_dict
    
    return race_names

# I wanted to preserve the human ethnic groups' common names, so I imported their names separately
def get_human_names():
    """
    Each line in the human names list is organised as follows:
    
    {Ethnicity}; {Male}: [list of names]; {Female}: {list of names}; {Last}: [list of names]
    
    Specifically, semi-colons separating ethnicity from name types, and colons separating name type labels from the names.
    This makes it easy to split them up and store them in an organised way in the final dictionary.
    """
    # create the final dictionary to store the names
    human_names = {}
    
    # open the txt file and read the contents
    with open("text/names/human_names.txt", "r") as file:
        
        # iterate through each line
        for line in file.readlines():
            
            # using tuple assignment, store each line after being divided by semi-colons
            ethnicity, male, female, last = line.rstrip().split("; ")
            
            # store the names as a nested dictionary
            # each value is just the list of names but subsetted to remove the label and split by commas
            human_names[ethnicity] = {
                "Male": male[6:].split(", "),
                "Female": female[8:].split(", "),
                "Last": last[6:].split(", "),
            }
    
    return human_names

# save the dictionary of all race names and then include the human names
race_names = get_race_names()
race_names["human"] = get_human_names()

# create new char
def new_char(input_params, num_char):
    if num_char == "":
        num_char = 1
    else:
        num_char = int(num_char)

    # final list of characters to be returned
    chars_out = []

    for _ in range(num_char): 
        # tuple assignment for all input parameters
        init_name, init_class, init_race, init_bg, init_motiv, init_align, init_personality, init_mood = input_params

        # defining the potential values of empty strings
        invalid = ["", " "]
        
        sex = random.choice(["Male", "Female"])
        new_race = init_race if init_race not in invalid else random.choice(database["races"])
        subrace =  random.choice([subs for subs in database["subraces"] if new_race.title() in subs])

        # if user inputs were not blank or space, save that as the character feature
        # otherwise, make a random choice from the saved information
        char = {
            "Name": init_name if init_name not in invalid else name_from_race(new_race.lower(), sex),
            "Race": subrace,
            "Class": init_class if init_class not in invalid else sub_from_main(database["subclasses"], database["classes"]), 
            "Background": init_bg if init_bg not in invalid else random.choice(database["backgrounds"]),
            "Motivation": init_motiv if init_motiv not in invalid else random.choice(database["motivations"]),
            "Alignment": init_align if init_align not in invalid else random.choice(database["alignments"]),
            "Personality": init_personality if init_personality not in invalid else random.sample(database["personalities"], 4),
            "Mood": init_mood if init_mood not in invalid else random.sample(database["moods"], 3)
        }
        chars_out.append(char)

    return chars_out


def name_from_race(race, sex):
    """ 
    A function that generates the name of a character based on their race.
    Uses the standard race name options and conventions from the PHB
    
    Input
    -----
    race : string stating the race of the character
    sex  : string stating the character's sex
    
    Output
    -----
    String : containing the character's full name, following the conventions defined by each race.
    
    """
    
    if race == "human":
        
        # choose a random ethnicity and then use the helper function to choose first and last names based on sex
        ethn = random.choice(list(race_names["human"].keys()))
        first, last = choose_name(race_names["human"][ethn], sex)
        
        # for the Shou People, they place their family names first, but every other ethnicity uses first name first
        return f"{last} {first}, Shou People" if ethn == "Shou" else f"{first} {last}, {ethn} People"
    
    elif race == "gnome":
        first, last = choose_name(race_names["gnome"], sex)
        
        # in addition to first and last names, gnomes also have a nickname, so I added the nickname in brackets before their names
        nickname = random.choice(race_names["gnome"]["Nickname"])
        return f"({nickname}) {first} {last}"
    
    elif race == "dragonborn":
        first, last = choose_name(race_names["dragonborn"], sex)
        
         # all dragonborn use their clan names first
        return f"{last} {first}"
    
    elif race == "half-elf":
        
        # half-elves use human and elf names depending on their situation, so I arbitrarily assigned 50% probability for each
        if round(random.random()):
            first, last = choose_name(race_names["elf"], sex)
            return f"{first} {last}"
        else:
            # if human is chosen, then the code calls this function again using human names specifically
            return name_from_race("human", sex)
        
    elif race == "half-orc":
        # half-orcs also choose either orc-ish names or human names, so I chose 75% orc-ish names, also arbitrarily
        if random.random() > 0.75:
            return random.choice(race_names["half-orc"][sex])
        else:
            return name_from_race("human", sex)
        
    elif race == "tiefling":
        """
        Tieflings can take either: 
        - Infernal names related to their bloodline,
        - A name of a concept/virtue that they try to embody with their lives, or
        - A name characteristic to the culture theiy grew up in.
        
        I then assigned a 20% chance to take a different race's naming convention
        and from the remaining 80%, a 50% chance to have either an infernal or conceptual name
        """
        if random.random() < 0.2:
            new_choice = random.choice([race.lower() for race in database["races"] if race != "Tiefling"])
            return name_from_race(new_choice, sex)
        else:
            if round(random.random()):
                return random.choice(race_names["tiefling"][sex])
            else:
                return random.choice(race_names["tiefling"]["Concept"])
    else:
        # for all other races, their names follow the "First Last" structure
        first, last = choose_name(race_names[race], sex)
        return f"{first} {last}"


# helper function that uses the race_names dictionary for a specific race and the chosen sex to choose a name
def choose_name(names, sex):
    last = random.choice(names["Last"])
    if sex == "Female":
        first = random.choice(names["Female"])
    elif sex == "Male":
        first = random.choice(names["Male"])
    return first, last

def sub_from_main(subset, mainset):
    """
    Randomly chooses a main item from the shortened list, then uses that main item to choose a sub-item.
    Specifically - choose subclass and subrace from main class and race
    
    First makes a random choice within the main set then uses that item to filter the subset items and makes random choice from filteredlist
    
    Parameters
    ----------
    subset  : the list of subcategory items with uneven balance across categories
    mainset : the list of the larger categories of items
    
    """
    # make the random choice from the main list, then use that choice to filter the sublist and then make the random sublist choice
    main = random.choice(mainset)
    sub = random.choice([subs for subs in subset if main in subs])
    return sub

# function that makes the respective calls to OpenAI's API depending on the desired type of output
def OpenAIcall(prompt_in): #next step - takes type and prompt as input
    
    text_response = openai.Completion.create(
        model="text-davinci-003",
        prompt= prompt_in,
        temperature=0.6,
        max_tokens = 1000
        )
    print(text_response["choices"][0]["text"])
    return text_response["choices"][0]["text"].replace('\n', '')

