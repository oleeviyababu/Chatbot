from chatbot import Chatbot
import threading
from textblob import TextBlob
import prompts

lock = threading.Lock()


class ChatbotImplementation(Chatbot):

    def __init__(self):
        Chatbot.__init__(self)
        self.succesful_sessions = []

    def get_sentiment_analysis_prompt(self, text):

        analysis = TextBlob(text)
        if analysis.sentiment.polarity > 0.2:
            sentiment = "positive"
            sentiment_prompt = prompts.positive_sentiment_prompt
        elif analysis.sentiment.polarity < 0:
            sentiment = "negative"
            sentiment_prompt = prompts.negative_sentiment_prompt
        else:
            sentiment = "neutral"
            sentiment_prompt = prompts.neutral_sentiment_prompt
        return sentiment_prompt, sentiment

    def get_intent_prompt(self, intent):
        intent_name = intent["name"]
        if intent_name == "provide_evidence_round_earth":
            intent_prompt = prompts.prompt_template_success
        elif intent_name == "greeting":
            intent_prompt = prompts.greet_intent_prompt
        elif intent_name == "disagree_flat_earth":
            intent_prompt = prompts.argumentation_intent_prompt
        elif intent_name == "curiosity_about_flat_earth":
            intent_prompt = prompts.curiosity_intent_prompt
        elif intent_name == "user_asks_for_clearer_explanation":
            intent_prompt = prompts.clarification_intent_prompt
        elif intent_name == "out_of_scope":
            intent_prompt = prompts.out_of_scope_prompt
        else:
            intent_prompt = prompts.argumentation_intent_prompt
        return intent_prompt, intent_name

    def get_prompt(self, messages, intent, session_id):
        print("*********************")
        print("intent", intent)
        latest_user_ip = messages[-1]["message"]
        sentiment_prompt, sentiment = self.get_sentiment_analysis_prompt(latest_user_ip)
        intent_prompt, intent_name = self.get_intent_prompt(intent)
        print("*********************")
        print(f"Sentiment: {sentiment} , Intent: {intent_name} ", "latest input :",latest_user_ip)
        print("*********************")
        # find out if this user session reached the success state or not
        session_is_succesful = False
        with lock:
            if intent["name"] == "provide_evidence_round_earths":
                if session_id not in self.succesful_sessions:
                    self.succesful_sessions.append(session_id)
            session_is_succesful = session_id in self.succesful_sessions

        if session_is_succesful:
            # generate the prompt that the user succeeded
            prompt = prompts.prompt_template_success.format(
                user_message=latest_user_ip)  # + self.build_dialog(messages)
            print("Prompt to llm:", prompt)

        else:
            # # generate the normal prompt
            # # prompt = prompt_template_oos + self.build_dialog(messages)
            # if intent["name"] == "out_of_scope":
            #     intent_prompt = prompts.out_of_scope_prompt
            # else:
            #     intent_prompt = prompts.argumentation_intent_prompt  # default to out of scope if no match found

            prompt = prompts.prompt_template_persona + sentiment_prompt + intent_prompt + self.build_dialog(messages)
            # print("*****************************************************")
            # print("prompt template is :", prompt_template)
            print("*****************************************************")
            print("Prompt to llm:", prompt)
            print("*****************************************************")

        return prompt, session_is_succesful
