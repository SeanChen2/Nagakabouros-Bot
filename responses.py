from random import choice, randint

def get_response(raw_user_input):
    user_input = raw_user_input.lower()    # Turn everything lowercase

    if user_input == "":
        return "Ask Endphite for a list of commands!"
    elif "hello" in user_input:
        return "Hello!"
    elif "illaoi" in user_input:
        return choice(["Best champion in league.", "I am her god.", "Did I hear the most respectable champion in league?"])
