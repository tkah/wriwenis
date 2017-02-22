import os
import re
import string
import random
import json
import time
import markovify
from textblob import TextBlob
from textblob import Word
from flask import Flask
from flask import render_template, url_for, request, jsonify
import requests
import twitter

app = Flask(__name__)

# Used to build up stochastic question
SINGULAR_VERBS = [
    "receives", "accepts", "joins", "agonizes over", "loves", "hates", "wants", "needs", "worries about", "eats", "consumes", "hesitates over", "fights with", "wonders about", "contemplates", "partakes of", "rejoices over", "praises", "is confounded by", "exalts", "finds cohesion in"
]

# Used to build up stochastic response
QUOTE_INTROS_WITH_NOUN = [
    " The Elders may know more of '{noun}'. In the Word, it says: \""," My knowledge is limited. Wriwenis's is infinite. Of '{noun}', the texts say: \""," I'm not able to discern your meaning. I'm sure others could tell you more about '{noun}'. The Book says: \""," I'm sorry, but I tire easily. The subject of '{noun}' is not one I'm familiar with. Perhaps the wisdom of Wriwenis could help: \""
]

# Used to build up stochastic response
QUOTE_INTROS_NO_NOUN = [
    " This is beyond my knowledge. The Word says: \""," I don't know all. That suits me. But for those more inquisitive, the Word says: \""," A wise though. It has been said: \""," That is the purview of the Elders. It is known that: \""
]

LOCATION_SENTENCES = [
    "How is the weather in {location}? Wriwenis has many followers there. You should consider joining them.","I've never visited {location}. Do you enjoy it there?","I've always heard that {location} was beautiful. Perhaps I'll visit. We can meet up and talk of Wriwenis.'"
]

# Create Twitter Client
with open('twitter_config.json') as cred:
    creds = json.load(cred)
    twitter_api = twitter.Api(**creds)

# Create markov text object to create quote
with open("src/directory/markov-src-spaceless.txt") as f:
    text = f.read()

text_model = markovify.Text(text)

# The following Natural Language Processing functions are either directly taken from, or modified from, https://apps.worldwritable.com/tutorials/chatbot/
def preprocess_text(sentence):
    """Handle some weird edge cases in parsing, like 'i' needing to be capitalized
    to be correctly identified as a pronoun"""
    cleaned = []
    words = sentence.split(' ')
    for w in words:
        if w == 'i':
            w = 'I'
        if w == "i'm":
            w = "I'm"
        cleaned.append(w)

    return ' '.join(cleaned)

def starts_with_vowel(word):
    """Check for pronoun compability -- 'a' vs. 'an'"""
    return True if word[0] in 'aeiou' else False

def find_pronoun(sent):
    """Given a sentence, find a preferred pronoun to respond with. Returns None if no candidate
    pronoun is found in the input"""
    pronoun = None

    for word, part_of_speech in sent.pos_tags:
        # Disambiguate pronouns
        if part_of_speech == 'PRP':
            pronoun = word
            break
    return pronoun

def find_verb(sent):
    """Pick a candidate verb for the sentence."""
    verb = None
    for word, part_of_speech in sent.pos_tags:
        if part_of_speech.startswith('VB'):  # This is a verb
            verb = word
            break
    return verb


def find_noun(sent):
    """Given a sentence, find the best candidate noun."""
    noun = None

    if not noun:
        for w, p in sent.pos_tags:
            if p == 'NN':  # This is a noun
                noun = w
                break

    return noun

def find_adjective(sent):
    """Given a sentence, find the best candidate adjective."""
    adj = None
    for w, p in sent.pos_tags:
        if p == 'JJ':  # This is an adjective
            adj = w
            break
    return adj

def find_candidate_parts_of_speech(parsed):
    """Given a parsed input, find the best pronoun, direct noun, adjective, and verb to match their input.
    Returns a tuple of pronoun, noun, adjective, verb any of which may be None if there was no good match"""
    pronoun = None
    noun = None
    adjective = None
    verb = None
    for sent in parsed.sentences:
        pronoun = find_pronoun(sent)
        noun = find_noun(sent)
        adjective = find_adjective(sent)
        verb = find_verb(sent)
    return pronoun, noun, adjective, verb

# End NLP tutorial functions

def multi_tweet(quote):
    twitter_api.PostUpdate(quote[:137] + "...")

    if (len("..." + quote[138:]) > 140):
        multi_tweet("..." + quote[138:])
    else:
        twitter_api.PostUpdate("..." + quote[138:])


# RESTful end point called to load application
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

# RESTful end point called by application when it's the chatbots turn to speak
@app.route('/input', methods=['POST'])
def get_response():
    # Load input from user and make lower case to more easily match
    input_msg_obj = json.loads(request.data.decode())
    input_msg = input_msg_obj["text"].lower()
    input_msg_array = input_msg.split(". ")
    input_msg = input_msg_array[len(input_msg_array) - 1]
    output=pronoun=noun=adjective=verb= ""
    quote= ""
    is_random = 0

    print(input_msg_obj)

    # Grab user name if present (defualts to You)
    author = input_msg_obj["author"]
    location = input_msg_obj["location"]

    # Confirm desire to join if last output was about joining or if user expresses an interest
    if author.lower().find("initiate") == -1 and input_msg_obj["lastOutput"].lower().find("you would like to join with us in wriwenis") > -1 and input_msg.find("ye") > -1:
        output = "Excellent! Welcome initiate. The merging will progress in due time. Focus your mind on Wriwenis and his love. Come speak with us again in the morrow for your next step."
        if author == "You":
            author = "Initiate"
        else:
            author = "Initiate " + author

    # Confirm desire to join if last output was about joining or if user expresses an interest
    if author.lower().find("initiate") == -1 and input_msg_obj["lastOutput"].lower().find("You would like to join with us in Wriwenis") > -1 and input_msg.find("no") > -1:
        output = "That is unfotunate to hear, but every minute of every hour is a new opportunity to meet Wriwenis. Soon you will have a change of heart. I am sure."

    # Confirm desire to join if last output was about joining or if user expresses an interest
    if author.lower().find("initiate") == -1 and (input_msg_obj["lastOutput"].lower().find("join") > -1 or input_msg.find("join") > -1):
        output = "You would like to join with us in Wriwenis?"
        if output.lower() == input_msg_obj["lastOutput"].lower():
            output = ''

    # How many times since last asked name
    if (input_msg_obj["since_name_check"] != -1):
        since_name_check = input_msg_obj["since_name_check"] + 1
    else:
        since_name_check = -1

    # How many times since last asked profession
    if (input_msg_obj["since_profession_check"] != -1):
        since_profession_check = input_msg_obj["since_profession_check"] + 1
    else:
        since_profession_check = -1

    # Confirm profession if last output was profession question or if user is
    if input_msg_obj["lastOutput"].lower().find("your profession") > -1 or input_msg.find("my profession is") > -1:
        words = input_msg.split()
        profession = words[len(words) - 1].capitalize()
        output = author + ", you are a " + profession + "?"

    # Profession is correct, greet
    if input_msg_obj["lastOutput"].lower().find("you are a") > -1 and input_msg.find("ye") > -1:
        words = input_msg_obj["lastOutput"].split()
        profession = words[len(words) - 1][:-1].capitalize()
        author_array = author.split()
        if author_array[1] == "of":
            author = author_array[0] + ", " + profession + " of " + location
        else:
            author = author_array[0] + " " + author_array[1] + ", " + profession + " of " + location
        output = "Being a " + profession + " is an admirable vocation and a fitting one for you, " + author + "."
        since_profession_check = -1

    # Profession is incorrect, apologize
    if input_msg_obj["lastOutput"].lower().find("your are a") > -1 and input_msg.find("no") > -1:
        output = "I apologize, " + author + ". Sometimes in my excitement to invite another to merge with Wriwenis, I make careless mistakes."

    # Check for repeating input from user
    if input_msg_obj["lastInput"].lower() == input_msg.lower():
        if author != "You":
            output += author + ', '
        output += "Why do you repeat yourself? It is fine with me, but feel comfortable to share what you wish. Wriwenis is open to all."

    # Confirm name if last output was name question or if user is
    if input_msg_obj["lastOutput"].lower().find("your name") > -1 or input_msg.find("my name is") > -1:
        words = input_msg.split()
        name = words[len(words) - 1].capitalize()
        output = "Your name is " + name + "?"

    # Name is correct, greet
    if input_msg_obj["lastOutput"].lower().find("your name is") > -1 and input_msg.find("ye") > -1:
        words = input_msg_obj["lastOutput"].split()
        if author == "You":
            author = words[len(words) - 1][:-1].capitalize() + " of " + location
        else:
            author = author + words[len(words) - 1][:-1].capitalize() + " of " + location
        output = "It is nice to meet you " + author + "."
        since_name_check = -1

    # Name is incorrect, apologize
    if input_msg_obj["lastOutput"].lower().find("your name is") > -1 and input_msg.find("no") > -1:
        output = "I apologize. Sometimes in my excitement to invite another to merge with Wriwenis, I make careless mistakes."

    # Respond if no input
    if input_msg == "" or input_msg == None:
        return "Please, take your time"

    # Remove punctuation for direct matching and keyword matching
    input_msg_nopunc = re.sub('['+string.punctuation+']', '', input_msg)

    # Open direct response json file to look for direct and keyword matches
    with open('src/directory/direct-resp.json') as data_file:
        direct = json.load(data_file)

    # Iterate through direct response objects
    for obj in direct:
        # Iterate through direct response object input arrays looking for input phrase
        for msg in obj["input"]:
            # If input phrase matches object input text, set output equal to random object output phrase
            if (msg == input_msg_nopunc):
                print(msg)
                output = random.choice(obj["output"])
                break

        if output != "":
            break

    # Add spaces to beginning and end for keyword search
    input_msg_nopunc = ' ' + input_msg_nopunc + ' '

    # If no direct response, iterate again through canned phrases looking for keyword matches
    if output == '':
        # Iterate through direct response objects
        for obj in direct:
            # Iterate through direct response object input arrays looking for input phrase
            for word in obj["keywords"]:
                # If input phrase matches object input text, set output equal to random object output phrase
                if input_msg_nopunc.find(' ' + word + ' ') > -1:
                    print(word)
                    output = random.choice(obj["output"])
                    break

            if output != "":
                break

    if output != "" and output.lower().find("turner") > -1:
        output = output.replace("Turner", input_msg_obj["acolyte"])

    # If direct phrase and keyword/phrase match not found, create randomized response, trying to use as much of the sentence as possible for a seed
    if output == "":
        cleaned = preprocess_text(input_msg)

        # Use TextBlob for natural language processing in order to extract parts of speech from sentence
        parsed = TextBlob(cleaned)
        pronoun, noun, adjective, verb = find_candidate_parts_of_speech(parsed)

        # Flip pronouns if relevant
        if pronoun is not None:
            if pronoun == 'I':
                pronoun = 'you'
            elif pronoun == 'you':
                pronoun = 'i'

        if noun is not None:
            print("resp_object: " + noun)
        if pronoun is not None:
            print("resp_subj: " + pronoun)
        if verb is not None:
            print("resp_verb: " + verb)

        # Get Markov quote, using the noun and verb as a seed if both present
        # Also, choose a random quote introductory phrase
        if noun is not None and verb is not None:
            seed = str(noun) + ' ' + str(verb)
            try:
                quote = text_model.make_sentence_with_start(seed)
            except:
                quote = ""

        # Skipping to shorten response time
        # print("start prnoun and verb")
        # Try to make quote using pronoun and verb
        # if pronoun is not None and verb is not None and quote == "":
        #    seed = str(pronoun) + ' ' + str(verb)
        #    try:
        #        quote = text_model.make_sentence_with_start(seed)
        #    except:
        #        quote = ""

        print("start noun alone")
        # Try to make a quote using the noun as a seed
        if quote == "" and noun is not None:
            seed = str(noun) + ' is'
            try:
                quote = text_model.make_sentence_with_start(seed)
            except:
                seed = 'The ' + str(noun)
                try:
                    quote = text_model.make_sentence_with_start(seed)
                except:
                    quote = ""

        print("start verb alone")
        # Try to make a quote using the base form of the verb
        if quote == "" and verb is not None and verb[0] != "'":
            verb = Word(verb)

            try:
                verb = verb.lemmatize("v")
            except:
                print("couldn't lemmatize verb")

            seed = verb
            v_text_model = markovify.Text(text, state_size=1)
            try:
                quote = v_text_model.make_sentence_with_start(seed)
            except:
                quote = ""

        # print("start pronoun alone")
        # Skipping to shorten response time
        # Try to make quote using pronoun as seed
        # if quote == "" and pronoun is not None:
        #    seed = str(pronoun) + ' is'
        #    try:
        #        quote = text_model.make_sentence_with_start(seed)
        #    except:
        #        seed = 'The ' + str(pronoun)
        #        try:
        #            quote = text_model.make_sentence_with_start(seed)
        #        except:
        #            quote = ""

        if quote != "":
            is_random = 1

        if quote == "" and location == "":
            ip_address = request.headers['X-Forwarded-For'] #request.environ['REMOTE_ADDR']
            r = requests.get('http://freegeoip.net/json/' + ip_address)
            location = r.json()["city"]
            quote = random.choice(LOCATION_SENTENCES).format(**{'location': location})
        elif quote == "" and (author == "You" or author == "Initiate") and since_name_check >= 10:
            quote = "What is your name?"
            since_name_check = 0
        elif quote == "" and author.find("initiate") == -1 and (since_name_check % 3 == 0 or since_profession_check % 3 == 0):
            if author != "You":
                quote += " " + author + ", "
            quote += "Have you thought anymore about joining with us in Wriwenis?"
        elif quote == "" and since_name_check == -1 and since_profession_check >= 5:
            quote += " " + author + ", what is your profession?"


        # If all else fails, create a random sentence using no seed
        if quote == "" or quote is None:
            quote = text_model.make_short_sentence(70)
            is_random = 1

        print(quote)
        # Capitalize first word of sentence and set quote as output
        quote = quote[0].upper() + quote[1:]
        if is_random == 1:
            if len(quote) > 140:
                multi_tweet(quote)
            # Tweet random response
            twitter_api.PostUpdate(quote)
        output = quote

    # Future development will try to pull out user's name
    res = {'output': output, 'author': author, 'since_name_check': since_name_check, 'since_profession_check': since_profession_check, 'location': location}

    # Delay response if no quote created in order to simulate a similar delay as if a person was typing a response
    if quote == "":
        time.sleep(4)

    return jsonify(**res)

if __name__ == '__main__':
    app.run()
