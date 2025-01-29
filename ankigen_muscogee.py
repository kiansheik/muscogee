import json
import genanki, random
import requests, os, time
from tqdm import tqdm
from bs4 import BeautifulSoup
import glob
import pandas as pd
from fuzzywuzzy import fuzz

local_folder = "dict_html"


def random_id():
    return random.randrange(
        1 << 30, 1 << 31
    )  # Generate a random number within Anki's expected range for IDs


def create_anki_deck_from_all(data, deck_name, output_file):
    # Create a new Anki deck
    deck_id = 1447502638
    deck = genanki.Deck(deck_id, deck_name)

    # Read CSS for the cards from "styles.css"
    css_style = ""
    with open("styles.css", "r") as f:
        css_style = f.read()
    # Define a Model for the notes
    my_model = genanki.Model(
        1841913421,
        "Muscogee Webonary Entry",
        fields=[
            {"name": "Muscogee"},
            {"name": "English"},
        ],
        templates=[
            {
                "name": "Muscogee -> English",
                "qfmt": """<div id="searchresults" class="vernacular-results center">{{Muscogee}}</div>
                <script>
                    (() => {
                        var replayer = document.getElementsByTagName('audio')[0];
                        replayer.play();
                    })();
                </script>
                """,
                "afmt": '<div id="searchresults" class="vernacular-results center">{{Muscogee}}<br><hr id=answer>{{English}}</div>',
            },
            {
                "name": "English -> Muscogee",
                "qfmt": '<div id="searchresults" class="vernacular-results center">{{English}}</div>',
                "afmt": '<div id="searchresults" class="vernacular-results center">{{English}}<br><hr id=answer>{{Muscogee}}</div>',
            },
        ],
        css=css_style,
    )

    # Download and add notes to the deck
    for item in tqdm(data):
        q = item["muscogee"]
        if q and item["english"]:
            a = item["english"]
            note = genanki.Note(
                model=my_model,
                fields=[
                    q,
                    a,
                ],
            )
            deck.add_note(note)

    # Create a package with the deck and include media files
    deck.notes = list({x.guid: x for x in deck.notes}.values())
    package = genanki.Package(deck)
    package.write_to_file(output_file)


def create_anki_deck_from_100_most_common(data, deck_name, output_file, examples=True):
    # Create a new Anki deck
    deck_id = 1841913421 + sum([ord(x) for x in deck_name])
    deck = genanki.Deck(deck_id, deck_name)

    # Read CSS for the cards from "styles.css"
    css_style = ""
    with open("styles.css", "r") as f:
        css_style = f.read()
    # Define a Model for the notes
    my_model = genanki.Model(
        deck_id,
        "Muscogee Webonary Entry",
        fields=[
            {"name": "Muscogee"},
            {"name": "English"},
            {"name": "Pronunciations"},
            {"name": "Audio"},
        ],
        templates=[
            {
                "name": "Muscogee -> English",
                "qfmt": """<div id="searchresults" class="vernacular-results center">{{Muscogee}}{{type:English}}</div><audio src="{{Audio}}">""",
                "afmt": '<div id="searchresults" class="vernacular-results center">{{Muscogee}}<br><hr id=answer>{{type:English}}</div><audio src="{{Audio}}">',
            },
            {
                "name": "English -> Muscogee",
                "qfmt": '<div id="searchresults" class="vernacular-results center">{{English}}{{type:Muscogee}}</div>',
                "afmt": '<div id="searchresults" class="vernacular-results center">{{English}}<br><hr id=answer>{{type:Muscogee}}</div><audio src="{{Audio}}">',
            },
        ],
        css=css_style,
    )

    # Download and add notes to the deck
    media_files = []
    for item in tqdm(data):
        verb = item["headword"]
        if verb and item["senses"]:
            audio_url = None
            pronunciation = None
            fname = ""
            if item["pronunciations_audio"]:
                audio = item["pronunciations_audio"][0]
                audio_url = audio["server_url"]
                filename = audio_url.split("/")[-1]
                audio_path_local = "audio/" + filename
                if not os.path.exists(audio_path_local):
                    time.sleep(1)  # Be respectful to the website, avoid being too fast
                    audio_response = requests.get(audio_url)
                    with open(audio_path_local, "wb") as audio_file:
                        audio_file.write(audio_response.content)
                media_files.append(audio_path_local)
                fname = f"[sound:{filename}]"
            if item["pronunciations"]:
                pronunciation = item["pronunciations"]
            for sense in item["senses"]:
                definition = sense["definition"]
                sense_verb = f"{verb}"
                if sense["sense_number"]:
                    sense_verb += f" ({sense['sense_number']})"
                note = genanki.Note(
                    model=my_model,
                    fields=[
                        sense_verb,
                        definition,
                        pronunciation,
                        fname,
                    ],
                )
                deck.add_note(note)
                if examples:
                    for example in sense["example_texts"]:
                        example_text = example["example"]
                        example_translation = example["translation"]
                        note = genanki.Note(
                            model=my_model,
                            fields=[
                                example_text,
                                example_translation,
                                pronunciation,
                                fname,
                            ],
                        )
                        deck.add_note(note)

    # remove duplicates from deck.notes based on [x.guid for x in deck.notes]
    deck.notes = list({x.guid: x for x in deck.notes}.values())
    package = genanki.Package(deck)
    package.media_files = media_files
    package.write_to_file(output_file)


deck_name = "Muscogee Webonary Vocab"
data = []
data_json = []
# loop through the current directory and make a list of each filename which matches *_page_*.html
matching_files = glob.glob(f"{local_folder}/*_page_*.html")

for html_file_path in tqdm(matching_files):
    # Open the HTML file and parse it
    with open(html_file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file.read(), "html.parser")

    # Iterate through all div.post elements
    for post_div in soup.select("div.post"):
        datum_json = {}
        # Select the main_headword elements (there should be one main_headword per post)
        main_headword = post_div.select_one(".mainheadword")
        # delete any element inside of main_headword that has class 'subentries'
        if main_headword:
            for subentry in post_div.select(".subentries"):
                subentry.decompose()
        pronunciations = post_div.select(".pronunciations")
        senses = post_div.select(".sensecontent")
        see = post_div.select("span.minimallexreferences")

        # We will handle one main_headword at a time
        if main_headword:
            # Get the main headword (HTML structure)
            main_headword_html = str(main_headword)
            datum_json["headword"] = main_headword.get_text(strip=True)

            # Set the initial Muscogee template with just the main headword HTML
            templ_musc = f"{main_headword_html}<br>"

            # Now collect all pronunciations and join them with "/"
            pronunciation_html = " / ".join([str(p) for p in pronunciations])
            pronunciation_json = " / ".join(
                [p.get_text(strip=True) for p in pronunciations]
            )
            datum_json["pronunciations"] = pronunciation_json
            # Look for an 'audio' tag in the pronunciations elements and add them with datum_json['pronunciations_audio'].append()
            datum_json["pronunciations_audio"] = []
            for p in pronunciations:
                audio = p.select_one("audio")
                if audio:
                    audio_src = audio.select_one("source").get("src")
                    # Download the audio file
                    audio_filename = audio_src.split("/")[-1]
                    audio_path_local = f"audio/{audio_filename}"
                    # ENABLE WHEN YOU WANT TO DOWNLOAD AUDIO FILES ONLY
                    if not os.path.exists(audio_path_local):
                        audio_path_local = None  # remove when downloading
                        # time.sleep(3)  # Be respectful to the website, avoid being too fast
                        # audio_response = requests.get(audio_src)
                        # with open(audio_path_local, 'wb') as audio_file:
                        #     audio_file.write(audio_response.content)
                    # Replace the audio src with the local path
                    datum_json["pronunciations_audio"].append(
                        {"server_url": audio_src, "local_url": audio_path_local}
                    )

            # Add pronunciations to the Muscogee template
            templ_musc += pronunciation_html

            # Initialize a list to hold formatted sense details
            formatted_senses = []
            datum_json["senses"] = []

            # Iterate over each sense and extract detailed information
            for sense in senses:
                sense_datum = {}
                # Extract sense number, definition, and examples
                sense_number = sense.select_one(".sensenumber")
                definition = sense.select_one(".definitionorgloss")
                examples = sense.select(".examplescontent")

                # Format sense number (if available)
                sense_number_text = (
                    sense_number.get_text(strip=True) if sense_number else ""
                )
                sense_datum["sense_number"] = sense_number_text

                # Format definition (if available)
                definition_text = definition.get_text(strip=True) if definition else ""
                sense_datum["definition"] = definition_text

                # Format examples (if available)
                example_texts = []
                sense_datum["example_texts"] = []
                for example in examples:
                    example_text = example.select_one(".example")
                    translation = example.select_one(".translation")
                    if example_text and translation:
                        ex = example_text.get_text(strip=True)
                        tr = translation.get_text(strip=True)
                        sense_datum["example_texts"].append(
                            {"example": ex, "translation": tr}
                        )
                        example_texts.append(f"{ex} - {tr}")
                datum_json["senses"].append(sense_datum)

                # Combine all the pieces into a structured format
                formatted_sense = ""
                if sense_number_text:
                    formatted_sense += f"<strong>{sense_number_text}.  </strong>"
                if definition_text:
                    formatted_sense += definition_text
                if example_texts:
                    examples = "<br>".join(example_texts)
                    formatted_sense += (
                        f"""<div class="right"><br><em>{examples}</em></div>"""
                    )

                # Append formatted sense to the list
                formatted_senses.append(formatted_sense)
            for refs in see:
                see_refs = refs.select(".headword > span > a")
                # get the URL and title of the reference in a list of dictionaries {'url', 'headword'}
                see_refs = [
                    {"url": ref.get("href"), "headword": ref.get_text(strip=True)}
                    for ref in see_refs
                ]
                # save the see_refs to the all see refs
                datum_json["see"] = see_refs
                # break loop after first run
                break
            # Join all formatted senses with a line break
            sense_html = "<br><br>".join(formatted_senses)

            # Set the English template with formatted sense HTML
            templ_engl = f"{sense_html}"

            # Store the result in the data list
            datum = {
                "muscogee": templ_musc,
                "english": templ_engl.replace("::before", " || "),
            }
            data.append(datum)
            data_json.append(datum_json)

# Output the data for verification (optional)
for entry in data_json:
    print(entry)
# save file of dictionary
with open("mvskoke_dic.json", "w") as f:
    json.dump(data_json, f, indent=4)
with open("mvskoke/mvskoke/mvskoke_dic.json", "w") as f:
    json.dump(data_json, f, indent=4)
most_common = pd.read_csv("100_most_common.csv")


def fuzzy_best_match(word, dat, top_n=1):
    scores = [(i, fuzz.ratio(word, x["headword"])) for (i, x) in enumerate(dat)]
    scores.sort(key=lambda x: x[1], reverse=True)
    return [dat[i[0]] for i in scores[:top_n]]


# for each word in the most_common list, find the best match in the data_json list
most_data_json = []
for i, row in most_common.iterrows():
    word = row["Words1"]
    best_match = fuzzy_best_match(word, data_json)[0]
    most_data_json.append(best_match)
# breakpoint()
create_anki_deck_from_all(
    data,
    f"{deck_name}",
    deck_name.lower().replace(" ", "_") + ".apkg",
)
deck_name = "Muscogee Vocab 100 Most common (Frye, 2020) 1"
create_anki_deck_from_100_most_common(
    most_data_json,
    f"{deck_name}",
    deck_name.lower().replace(" ", "_") + ".apkg",
    examples=False,
)

chapter_data = [
    ("estonko", 2),
    "est!nkis os",
    "mvtô",
    "hērscē",
    ("ehe", 2),
    "monkos",
    "enka",
    "hvo",
    "etvlwv",
    # "okmulke",
    "wohkv",
    "ue",
    # the alphabet
    "cokv",
    "eshoccickv",
    "vhvoke",
    "vhvokuce",
    "mvhayv",
    "cokv-hecv",
    "cvhocefkv",
    "ayo",
    "akketv",
    "cesse",
    "ēcko",
    "efv",
    "fo",
    "halo",
    "ehiwv",
    "lētkis",
    "kapv",
    "lucv",
    "meskē",
    "nerē",
    "ofv",
    "opv",
    "penwv",
    "rvro",
    "svmpv",
    "tvffo",
    "sutv",
    "vce",
    "wakv",
    "yvnvsv",
    "aeha!",
    "iemetv",
    "vhvoke",
    "cēmeu",
    "uewv",
    "fvkv",
    "fakke",
    "fakv",
    "ecke",
    "cuko",
    "cokwv",
    "cokv",
    "nake",
    "eto",
    "hvce",
    "cetto",
    "hvcce",
]
chapter_data_json = []
for word in chapter_data:
    verb = word
    count = 1
    if type(word) == tuple:
        verb = word[0]
        count = word[1]
    best_match = fuzzy_best_match(verb, data_json, top_n=count)
    for match in best_match:
        chapter_data_json.append(match)


deck_name = "Pum Opunvkv (Smith, 2003)"
create_anki_deck_from_100_most_common(
    chapter_data_json,
    f"{deck_name}",
    deck_name.lower().replace(" ", "_") + ".apkg",
    examples=False,
)
