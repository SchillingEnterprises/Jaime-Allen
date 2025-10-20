import openai
import json
from django.conf import settings


class TherapyAI:
    def __init__(self):
        self.sentiment_analyzer = None
        self.ai_enabled = bool(settings.OPENAI_API_KEY)

        # Only initialize if AI is enabled
        if self.ai_enabled:
            try:
                openai.api_key = settings.OPENAI_API_KEY
                # Only import transformers when needed
                from transformers import pipeline
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english"
                )
            except ImportError:
                print("Warning: Transformers not installed. Sentiment analysis disabled.")
            except Exception as e:
                print(f"Warning: Failed to initialize AI components: {e}")
                self.ai_enabled = False

    def analyze_sentiment(self, text):
        """AI-powered sentiment analysis for user messages"""
        if not self.sentiment_analyzer:
            return {'label': 'NEUTRAL', 'score': 0.5}

        try:
            result = self.sentiment_analyzer(text[:512])
            return result[0]
        except Exception as e:
            return {'label': 'NEUTRAL', 'score': 0.5}

    def generate_therapy_response(self, user_message, context=None):
        """Generate empathetic AI responses for therapy context"""
        if not self.ai_enabled:
            return "I'm here to listen. Could you tell me more about how you're feeling?"

        prompt = f"""
        As a compassionate therapy assistant, respond to this client message with empathy and professional insight.

        Client: {user_message}
        Context: {context or 'General relationship therapy'}

        Response should be:
        - Empathetic and validating
        - Professional and therapeutic
        - Suggest helpful perspectives
        - Encourage further discussion
        - Under 150 words
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system",
                     "content": "You are a compassionate therapy assistant providing supportive, professional responses."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return "Thank you for sharing. It takes courage to discuss these feelings. Would you like to explore this further in our session?"


class ContentOptimizer:
    def optimize_content(self, content_type, user_profile=None):
        """AI-driven content personalization"""
        optimizations = {
            'conflict_resolution': {
                'title': 'Conflict Resolution with Empathy',
                'keywords': ['communication', 'understanding', 'compromise', 'boundaries'],
                'ai_suggestions': ['Practice active listening without interrupting',
                                   'Use "I feel" statements instead of "You always"']
            },
            'renewing_connections': {
                'title': 'Renewing Emotional Connections',
                'keywords': ['reconnection', 'intimacy', 'communication', 'trust'],
                'ai_suggestions': ['Schedule weekly quality time without distractions',
                                   'Express appreciation for small daily actions']
            },
            'relationship_stages': {
                'title': 'Navigating Relationship Stages',
                'keywords': ['growth', 'intimacy', 'trust', 'communication'],
                'ai_suggestions': ['Celebrate relationship milestones together',
                                   'Maintain individual identities within the relationship']
            },
            'serenity': {
                'title': 'Finding Relationship Serenity',
                'keywords': ['peace', 'acceptance', 'mindfulness', 'balance'],
                'ai_suggestions': ['Practice mindfulness meditation together',
                                   'Focus on what you can control in the relationship']
            },
            'effective_communication': {
                'title': 'Mastering Effective Communication',
                'keywords': ['active listening', 'nonviolent communication', 'emotional intelligence',
                             'relationship skills'],
                'ai_suggestions': ['Practice the 3-second pause before responding',
                                   'Use "I feel" statements instead of "You always"']
            }
        }
        return optimizations.get(content_type, {})


# Initialize AI components
therapy_ai = TherapyAI()
content_optimizer = ContentOptimizer()
