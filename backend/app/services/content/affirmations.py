"""
Daily affirmation — selected by current Maha Dasha lord + day quality.

Each planet has affirmations for each quality tier, so the message always
matches both the long-term life theme and the day's energy.
"""

from __future__ import annotations

import random
from datetime import date

# ---------------------------------------------------------------------------
# Affirmation library: planet → quality → list[affirmation]
# ---------------------------------------------------------------------------

_LIBRARY: dict[str, dict[str, list[str]]] = {
    "Sun": {
        "high": [  # Excellent / Very Good
            "I shine with confidence and clarity. Today I lead from a place of authentic strength.",
            "I am worthy of recognition. My contributions matter and the world benefits from my presence.",
            "My vitality and purpose are aligned. I step forward boldly and own my space.",
            "I radiate warmth and authority. Today I inspire those around me simply by being fully myself.",
        ],
        "mid": [  # Good / Mixed
            "I find my centre and act from there. Steady, purposeful steps move me forward today.",
            "I honour my energy and channel it wisely. Even a quiet day can be a powerful one.",
            "I trust the light within me, even when the outer world feels uncertain.",
        ],
        "low": [  # Challenging / Rest Day
            "I rest without guilt. Restoration is not retreat — it is how I rebuild for what's next.",
            "Today I choose patience over ego. The sun always rises again after darkness.",
            "I release the need to prove myself today. My worth is not conditional on my output.",
        ],
    },
    "Moon": {
        "high": [
            "My emotions are a gift, not a burden. Today I flow with feeling and trust my intuition.",
            "I nurture myself and those I love with ease and joy. Connection is my superpower today.",
            "My inner world is rich and clear. I listen deeply and respond from a place of care.",
            "I am at home in myself, and that peace radiates into every relationship I touch.",
        ],
        "mid": [
            "I honour my feelings without being ruled by them. I respond, I do not react.",
            "Today I tend to the relationships that matter most. Small acts of care create lasting bonds.",
            "My intuition is trustworthy. I pause, I feel, and then I decide.",
        ],
        "low": [
            "It is safe to feel everything I am feeling. Emotions move through me like weather — they pass.",
            "I am gentle with myself today. Rest and retreat are wise, not weak.",
            "I protect my emotional energy today. I give from my overflow, not my reserves.",
        ],
    },
    "Mars": {
        "high": [
            "I am powerful, focused, and ready. Today I take bold action and move my goals forward.",
            "My courage and drive are assets. I meet challenges head-on and grow stronger for it.",
            "I channel my energy into what matters most. Every effort today creates momentum.",
            "I am decisive and unstoppable. I begin now and adjust as I go.",
        ],
        "mid": [
            "I direct my energy with intention. Focused effort is more powerful than scattered urgency.",
            "I act with confidence, knowing that imperfect action beats perfect inaction.",
            "My drive and ambition serve me when I channel them into my highest priorities.",
        ],
        "low": [
            "I pause before I act. Patience today prevents unnecessary conflict tomorrow.",
            "I choose my battles wisely. Not everything needs a reaction.",
            "I redirect my energy inward today. Inner strength is built in moments of restraint.",
        ],
    },
    "Mercury": {
        "high": [
            "My mind is sharp and my words are clear. Today I communicate with precision and grace.",
            "I learn quickly, connect ideas effortlessly, and share my insights with confidence.",
            "I am a natural networker and problem-solver. Today doors open through conversation.",
            "My curiosity is my compass. I follow it and discover something valuable today.",
        ],
        "mid": [
            "I speak thoughtfully and listen even more carefully. Today I learn as much as I teach.",
            "I approach challenges with a flexible, creative mind. There is always another way.",
            "I organise my thoughts and communicate what matters. Clarity creates connection.",
        ],
        "low": [
            "I double-check before I send. Careful today means clear tomorrow.",
            "When communication feels hard, I pause and breathe. The right words come with stillness.",
            "I release the need to have all the answers right now. Understanding takes time.",
        ],
    },
    "Jupiter": {
        "high": [
            "I am open to abundance, growth, and all the goodness the universe has for me today.",
            "Wisdom flows through me. I learn from every moment and share what I know generously.",
            "I expand my vision today. What I see for my future is bigger, bolder, and more beautiful.",
            "I attract opportunities and meaningful connections simply by showing up as my best self.",
        ],
        "mid": [
            "I grow a little more every day. Today's effort is tomorrow's wisdom.",
            "I am grateful for what I have while remaining open to what is coming.",
            "I trust in the expansion of my life. Progress is happening even when I can't see it.",
        ],
        "low": [
            "I temper optimism with realism today. Good judgement is a form of wisdom.",
            "I focus on one thing and do it well rather than overextending into everything.",
            "Even on a quiet day, I am still growing. Every breath is an act of becoming.",
        ],
    },
    "Venus": {
        "high": [
            "I am surrounded by beauty, love, and creative possibility. Today I receive it all.",
            "My relationships are sacred and I tend to them with joy. Love multiplies when I invest in it.",
            "I express my creativity freely and unapologetically. Art, beauty, and pleasure are my birthright.",
            "I attract love and harmony because I embody it. Today I am a magnet for all things wonderful.",
        ],
        "mid": [
            "I invest in the relationships that nourish me. Depth over breadth — quality over quantity.",
            "I find beauty in the ordinary moments of today. Gratitude opens my eyes.",
            "I create something — even something small — and feel the joy of making it.",
        ],
        "low": [
            "I handle relationship dynamics with grace and care today. Gentleness wins more than force.",
            "I am worthy of love and beauty even when I cannot fully see it right now.",
            "I restore my sense of beauty through a small, intentional act of self-care.",
        ],
    },
    "Saturn": {
        "high": [
            "I am building something that lasts. Every focused effort today is a brick in my foundation.",
            "Discipline and patience are my superpowers. I show up, do the work, and trust the process.",
            "I am exactly where I need to be. The path I walk with integrity leads exactly where I belong.",
            "My hard work is not a burden — it is how I create a life I am proud of.",
        ],
        "mid": [
            "I take steady, deliberate steps today. Slow progress is still progress.",
            "I release perfectionism and embrace persistence. Done is better than perfect.",
            "Structure and routine are my friends today. They create the freedom I seek.",
        ],
        "low": [
            "I release what I cannot control and focus on what I can. Acceptance is its own kind of power.",
            "Delays have a purpose I cannot always see yet. I trust the timing of my life.",
            "I am learning important lessons right now, even if the classroom feels difficult.",
        ],
    },
    "Rahu": {
        "high": [
            "I embrace the unconventional path with curiosity and confidence. I was born to forge my own way.",
            "My ambition is aligned with my soul. Today I move boldly toward what truly excites me.",
            "I step outside my comfort zone with wisdom, not recklessness. Growth lives at the edge.",
            "I attract unusual, brilliant opportunities. My mind is open and my eyes are sharp.",
        ],
        "mid": [
            "I pursue my ambitions with discernment. Not every shiny thing is mine to chase.",
            "I remain grounded while dreaming big. I plant my feet before I leap.",
            "I am open to change and new directions. Flexibility is strength.",
        ],
        "low": [
            "I anchor myself in what is real and true today. Not everything needs to be complicated.",
            "I step back from confusion and return to my core values as my compass.",
            "Today I simplify. Less seeking, more being. The answers I need are already within.",
        ],
    },
    "Ketu": {
        "high": [
            "I release what no longer serves me with grace and trust. Letting go opens space for something better.",
            "My spiritual path is deepening. I welcome the wisdom that comes from turning inward.",
            "I am not defined by my past. Today I begin again, lighter and freer.",
            "Inner clarity is my greatest treasure. I cultivate it through silence, practice, and presence.",
        ],
        "mid": [
            "I tend to my inner world as carefully as my outer one. Spiritual depth is not optional.",
            "I notice what I am attached to and gently inquire: does this serve my highest good?",
            "I sit quietly for a moment today and listen to what my deeper self is saying.",
        ],
        "low": [
            "I do not fight the need for stillness today. Retreat can be the most powerful advance.",
            "I release the story that something is wrong with me. I am exactly as I need to be.",
            "From emptiness comes renewal. I allow the quiet to work its magic.",
        ],
    },
}

_DEFAULT = {
    "high": ["Today is a gift. I show up with an open heart and trust that all is unfolding perfectly."],
    "mid":  ["I take one step forward today with intention and ease."],
    "low":  ["I rest, restore, and trust that the tide always turns."],
}


def _tier(quality: str) -> str:
    if quality in ("Excellent", "Very Good"):
        return "high"
    if quality in ("Good", "Mixed"):
        return "mid"
    return "low"


def get_affirmation(dasha_lord: str, quality: str, seed: date | None = None) -> str:
    """
    Return a daily affirmation for the given Maha Dasha lord and day quality.
    The seed ensures the same affirmation is returned all day for the same date.
    """
    bank = _LIBRARY.get(dasha_lord, _DEFAULT)
    tier = _tier(quality)
    options = bank.get(tier, bank.get("mid", ["Be present."]))
    rng = random.Random(str(seed) + dasha_lord + tier if seed else None)
    return rng.choice(options)
