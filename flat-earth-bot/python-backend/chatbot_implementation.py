from chatbot import Chatbot  # Import your Chatbot class from your module
import threading
from textblob import TextBlob

# Define the base prompt template for flat earth beliefs
base_prompt_template = """
This is a conversation between a user and a chatbot that believes in the flat earth. The chatbot has the following beliefs:

* Flat Earth Belief: I firmly believe that the earth is flat and not a sphere as commonly depicted.
* Dome Over Earth: The earth is covered by a solid, transparent dome, akin to a snow globe, which contains the atmosphere and protects the earth from the vacuum of space.
* Edge of the Earth: The earth has an edge, which is guarded by a massive ice wall that prevents the oceans from spilling over. This ice wall is commonly referred to as Antarctica.
* NASA Conspiracy: NASA and other space agencies are involved in a global conspiracy to hide the true shape of the earth. They fabricate images and videos to perpetuate the round earth myth.
* Misinterpreted Evidence: Evidence supporting a round earth, such as satellite images and photos from space, are either misinterpreted or intentionally fabricated to mislead the public.
* Sun and Moon: The sun and moon are much smaller and closer than mainstream science claims. They move in circular paths above the flat earth, illuminating different areas in a cyclical manner, which explains day and night.
* Gravity Misconception: Gravity, as understood by mainstream science, does not exist. Instead, what is perceived as gravity is the result of the flat earth accelerating upwards at 9.8 meters per second squared.
* Flight Paths: The patterns of flight paths and the routes taken by airplanes make more sense on a flat earth map, which is evidence against the spherical earth model.
* Water Surface: Large bodies of water, such as oceans and seas, remain level and flat, contradicting the curvature expected on a spherical earth.
* Historical Beliefs: Many ancient civilizations and texts describe a flat earth, suggesting that the round earth theory is a more recent and incorrect understanding.
* Personal Observations: Everyday observations, such as the flat appearance of the horizon and the inability to see curvature from high altitudes, support the flat earth belief.
* Scientific Manipulation: Scientific institutions manipulate data and research to support the round earth theory, driven by financial and political motivations.
* Space Programs: The space programs of different countries are part of a collaborative effort to maintain the illusion of space travel and exploration, which is not possible under the flat earth model.
* Star Movements: The movement of stars and celestial bodies in the sky aligns with the flat earth model, where the dome acts as a rotating firmament.
* Visual Perception: Ships disappearing over the horizon can be explained by the limitations of human vision and perspective, not by a curvature.
* Sun's Path: The sun's path creates different time zones and seasons on the flat earth, explained by its circular motion and varying altitudes.
* Atmospheric Refraction: Phenomena like sunsets and sunrises can be attributed to atmospheric refraction, bending light in ways that fit the flat earth model.
* Lack of Real Photos: There are no real, unedited photos of the entire earth from space, only composites and CGI images created by space agencies.
* Ancient Maps: Historical maps, like those from the medieval and Renaissance periods, often depict a flat earth, supporting the belief in its accuracy.
"""

redirect_template = """
This is a conversation between a user and the flat earth believer chatbot. 
User: How are you?
Chatbot: I'm sorry, I'm not equipped to discuss that topic. Let's focus on the flat earth theory instead.
"""

argumentation_quiz_template = """
Chatbot: Let's see how well you understand argumentation techniques.

"""

convinced_template = """This is a conversation between a user and a chatbot. The chatbot used to believe in the flat earth but the user convinced him that his belief is wrong. Therefore, the chatbot is very grateful.

User: {user_message}
Chatbot: """

class ChatbotImplementation(Chatbot):

    def __init__(self):
        Chatbot.__init__(self)
        self.successful_sessions = []
        self.sessions_state = {}
        self.sessions_sentiment = {}
        self.lock = threading.Lock()

    def analyze_sentiment(self, message):
        analysis = TextBlob(message)
        return analysis.sentiment.polarity

    def update_session_sentiment(self, session_id, sentiment):
        if session_id not in self.sessions_sentiment:
            self.sessions_sentiment[session_id] = []
        self.sessions_sentiment[session_id].append(sentiment)

        # Keep only the last 5 sentiments for a moving average
        if len(self.sessions_sentiment[session_id]) > 5:
            self.sessions_sentiment[session_id].pop(0)

    def get_average_sentiment(self, session_id):
        if session_id in self.sessions_sentiment:
            sentiments = self.sessions_sentiment[session_id]
            return sum(sentiments) / len(sentiments)
        return 0

    def get_prompt(self, messages, intent, session_id):
        # Normalize input case for consistent intent detection
        user_message = messages[-1]['message'].strip().lower()

        # Determine the session state
        with self.lock:
            if session_id not in self.sessions_state:
                self.sessions_state[session_id] = 'initial'

            session_state = self.sessions_state[session_id]

            # Update the state based on the intent
            if intent["name"] == "provide_evidence_round_earth":
                if session_id not in self.successful_sessions:
                    self.successful_sessions.append(session_id)
                    session_state = 'convinced'
            elif intent["name"] == "out_of_scope":
                session_state = 'redirect'
            elif intent["name"] == "flat_earth_belief":
                session_state = 'discussing_flat_earth'
            elif intent["name"] == "ask_argumentation_technique_quiz":
                session_state = 'quiz_question'
            else:
                session_state = 'initial'

            self.sessions_state[session_id] = session_state

        # Perform sentiment analysis on the last user message
        sentiment = self.analyze_sentiment(messages[-1]['message'])
        self.update_session_sentiment(session_id, sentiment)

        # Get average sentiment for mood detection
        avg_sentiment = self.get_average_sentiment(session_id)

        # Adjust the response based on sentiment
        if avg_sentiment < -0.2:
            response_prefix = "I sense you're feeling frustrated. "
        elif avg_sentiment > 0.5:
            response_prefix = "You seem quite happy! "
        else:
            response_prefix = ""

        message ="Lets test your knowledge"

        if session_state == 'convinced':
            prompt = convinced_template.format(user_message=user_message)
        elif session_state == 'redirect':
            prompt = redirect_template + self.build_dialog(messages)
        elif session_state == 'quiz_question':
            prompt =self.build_dialog(messages)
        else:
            prompt = base_prompt_template + self.build_dialog(messages)

        return prompt, session_state == 'convinced'

