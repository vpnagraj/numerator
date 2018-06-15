"""
this skill queries the numbers api for a fact about a given number
http://numbersapi.com/
"""
import json
import urllib2

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': output
        },
        'card': {
            'type': 'Simple',
            'title': "numerator",
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': {},
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    session_attributes = {}
    card_title = "Welcome to numerator"
    speech_output = "<emphasis level = 'strong'>Hi!</emphasis> Numerator here! <break time='600ms'/>" \
                    "<amazon:effect name = 'whispered'>Pick a number, any number.</amazon:effect>"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Hello?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Bye!"
    # Setting this to true ends the session and exits the skill.
    should_end_session = False
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def num_fact(intent, session):

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    
    num = intent['slots']['number']['value']
    
    url = "http://numbersapi.com/" + num + "?json"
    
    req = urllib2.Request(url)
    resp = urllib2.urlopen(req)
    data_json = json.loads(resp.read())
    speech_output = "<speak>" + data_json['text'] + "</speak>"
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, None, should_end_session))
# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "NumberFact":
        return num_fact(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """

    """
    This statement prevents someone else from configuring a skill that sends 
    requests to this function.
    """

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
