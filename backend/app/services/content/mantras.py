"""
Mantras — planetary Beej mantras and Nakshatra mantras.

Returns the appropriate mantra based on:
  • Dasha lord (for the daily planetary mantra)
  • Moon nakshatra (for the nakshatra mantra)

Includes phonetic pronunciation guide and a YouTube search link for audio.
"""

from __future__ import annotations

from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Planetary mantras (Beej / seed mantras)
# ---------------------------------------------------------------------------

@dataclass
class PlanetaryMantra:
    planet: str
    beej_mantra: str          # Sanskrit seed syllable mantra
    vedic_mantra: str         # longer traditional mantra
    phonetics: str            # pronunciation guide
    meaning: str
    repetitions: int          # traditional count
    best_day: str             # best weekday to chant
    youtube_search: str       # search query for finding audio


_PLANET_MANTRAS: dict[str, PlanetaryMantra] = {
    "Sun": PlanetaryMantra(
        planet="Sun",
        beej_mantra="Om Hraam Hreem Hraum Sah Suryaya Namah",
        vedic_mantra="Om Aakrishnena Rajasa Vartamano Niveshayan Amritam Martyam Cha",
        phonetics="Om Hraam (like 'harm') Hreem (like 'hreem') Hraum (like 'hrowm') Sah Soor-ya-ya Na-mah",
        meaning="Salutations to the Sun — the source of light, wisdom, and vitality.",
        repetitions=7,
        best_day="Sunday",
        youtube_search="Surya Beej Mantra Om Hraam Hreem",
    ),
    "Moon": PlanetaryMantra(
        planet="Moon",
        beej_mantra="Om Shraam Shreem Shraum Sah Chandraaya Namah",
        vedic_mantra="Om Imam Devah Asavindu Chandramsam Vicharatam",
        phonetics="Om Shraam (like 'shrarm') Shreem (like 'shreem') Shraum (like 'shrowm') Sah Chan-dra-ya Na-mah",
        meaning="Salutations to the Moon — the nurturer of mind, emotions, and inner peace.",
        repetitions=11,
        best_day="Monday",
        youtube_search="Chandra Beej Mantra Om Shraam Shreem",
    ),
    "Mars": PlanetaryMantra(
        planet="Mars",
        beej_mantra="Om Kraam Kreem Kraum Sah Bhoumaaya Namah",
        vedic_mantra="Om Agnir Murdhaa Divas Kakut Pati Prithivya Ayam",
        phonetics="Om Kraam (like 'crarm') Kreem (like 'creem') Kraum (like 'crowm') Sah Bhow-ma-ya Na-mah",
        meaning="Salutations to Mars — the planet of courage, energy, and righteous action.",
        repetitions=7,
        best_day="Tuesday",
        youtube_search="Mangal Beej Mantra Om Kraam Kreem",
    ),
    "Mercury": PlanetaryMantra(
        planet="Mercury",
        beej_mantra="Om Braam Breem Braum Sah Budhaya Namah",
        vedic_mantra="Om Udbudhyasvaagne Pratijaagrihi Tvam",
        phonetics="Om Braam (like 'brarm') Breem (like 'breem') Braum (like 'browm') Sah Bud-ha-ya Na-mah",
        meaning="Salutations to Mercury — the planet of intellect, communication, and learning.",
        repetitions=9,
        best_day="Wednesday",
        youtube_search="Budha Beej Mantra Om Braam Breem",
    ),
    "Jupiter": PlanetaryMantra(
        planet="Jupiter",
        beej_mantra="Om Graam Greem Graum Sah Gurave Namah",
        vedic_mantra="Om Brihaspatir Ati Yadaryo Arhaat Dyumad Vibhaaati",
        phonetics="Om Graam (like 'grarm') Greem (like 'greem') Graum (like 'growm') Sah Goo-ra-vey Na-mah",
        meaning="Salutations to Jupiter — the great teacher, bringer of wisdom, grace, and abundance.",
        repetitions=19,
        best_day="Thursday",
        youtube_search="Guru Brihaspati Beej Mantra Om Graam Greem",
    ),
    "Venus": PlanetaryMantra(
        planet="Venus",
        beej_mantra="Om Draam Dreem Draum Sah Shukraya Namah",
        vedic_mantra="Om Annaat Parisruto Rasam Brahmanaa Vyapibat Kshatram",
        phonetics="Om Draam (like 'drarm') Dreem (like 'dreem') Draum (like 'drowm') Sah Shook-ra-ya Na-mah",
        meaning="Salutations to Venus — the planet of love, beauty, pleasure, and harmonious relationships.",
        repetitions=16,
        best_day="Friday",
        youtube_search="Shukra Beej Mantra Om Draam Dreem",
    ),
    "Saturn": PlanetaryMantra(
        planet="Saturn",
        beej_mantra="Om Praam Preem Praum Sah Shanaischaraya Namah",
        vedic_mantra="Om Shannodevirabhistaya Aapo Bhavantu Pitaye",
        phonetics="Om Praam (like 'prarm') Preem (like 'preem') Praum (like 'prowm') Sah Sha-nai-sh-cha-ra-ya Na-mah",
        meaning="Salutations to Saturn — the great teacher of karma, discipline, and timeless truth.",
        repetitions=23,
        best_day="Saturday",
        youtube_search="Shani Beej Mantra Om Praam Preem",
    ),
    "Rahu": PlanetaryMantra(
        planet="Rahu",
        beej_mantra="Om Bhram Bhreem Bhraum Sah Rahave Namah",
        vedic_mantra="Om Kayaana Shchitr Aabhuvadooti Sada Vridhah Sakha",
        phonetics="Om Bhram (like 'bhr-arm') Bhreem (like 'bhreem') Bhraum (like 'bhrowm') Sah Ra-ha-vey Na-mah",
        meaning="Salutations to Rahu — the shadow planet of ambition, innovation, and karmic lessons.",
        repetitions=18,
        best_day="Saturday",
        youtube_search="Rahu Beej Mantra Om Bhram Bhreem",
    ),
    "Ketu": PlanetaryMantra(
        planet="Ketu",
        beej_mantra="Om Sraam Sreem Sraum Sah Ketave Namah",
        vedic_mantra="Om Ketum Krinaannaketave Pesho Maryaa Apo Usashaaktihi",
        phonetics="Om Sraam (like 'srarm') Sreem (like 'sreem') Sraum (like 'srowm') Sah Key-ta-vey Na-mah",
        meaning="Salutations to Ketu — the planet of spiritual liberation, detachment, and inner wisdom.",
        repetitions=17,
        best_day="Saturday",
        youtube_search="Ketu Beej Mantra Om Sraam Sreem",
    ),
}

# ---------------------------------------------------------------------------
# Nakshatra mantras
# ---------------------------------------------------------------------------

@dataclass
class NakshatraMantra:
    nakshatra: str
    number: int
    deity: str
    mantra: str
    phonetics: str
    energy_theme: str    # plain-English daily energy card
    youtube_search: str


_NAK_MANTRAS: list[NakshatraMantra] = [
    NakshatraMantra("Ashwini", 1, "Ashwini Kumaras",
        "Om Ashwibhyam Namah",
        "Om Ash-wee-bhyam Na-mah",
        "Swift beginnings, healing energy, and the courage to start fresh.",
        "Ashwini Nakshatra mantra chanting"),
    NakshatraMantra("Bharani", 2, "Yama",
        "Om Yamaya Namah",
        "Om Ya-ma-ya Na-mah",
        "A day of transformation, truth, and clearing what is no longer needed.",
        "Bharani Nakshatra mantra"),
    NakshatraMantra("Krittika", 3, "Agni",
        "Om Agni Devaya Namah",
        "Om Ag-ni Dev-a-ya Na-mah",
        "Purifying fire energy — burn away what holds you back and shine brighter.",
        "Krittika Nakshatra Agni mantra"),
    NakshatraMantra("Rohini", 4, "Brahma / Prajapati",
        "Om Prajapataye Namah",
        "Om Pra-ja-pa-ta-ye Na-mah",
        "A day of abundance, beauty, and creative manifestation. Plant seeds with love.",
        "Rohini Nakshatra mantra"),
    NakshatraMantra("Mrigashira", 5, "Soma (Moon)",
        "Om Somaya Namah",
        "Om So-ma-ya Na-mah",
        "Gentle seeking, curiosity, and the joy of exploring new paths.",
        "Mrigashira Nakshatra mantra"),
    NakshatraMantra("Ardra", 6, "Rudra (Shiva)",
        "Om Rudraya Namah",
        "Om Rud-ra-ya Na-mah",
        "A storm that clears the air — intensity serves growth today.",
        "Ardra Nakshatra Rudra mantra"),
    NakshatraMantra("Punarvasu", 7, "Aditi",
        "Om Aditi Devyai Namah",
        "Om A-di-ti Dev-yai Na-mah",
        "Return and renewal — today is perfect for restoration and second chances.",
        "Punarvasu Nakshatra mantra"),
    NakshatraMantra("Pushya", 8, "Brihaspati (Jupiter)",
        "Om Brihaspataye Namah",
        "Om Brih-as-pa-ta-ye Na-mah",
        "The most nourishing nakshatra — a day to give, receive, and grow.",
        "Pushya Nakshatra mantra"),
    NakshatraMantra("Ashlesha", 9, "Naga (Serpents)",
        "Om Nagaya Namah",
        "Om Na-ga-ya Na-mah",
        "Deep perception and intuitive wisdom — trust what you sense beneath the surface.",
        "Ashlesha Nakshatra mantra"),
    NakshatraMantra("Magha", 10, "Pitrs (Ancestors)",
        "Om Pitru Devaya Namah",
        "Om Pit-ru Dev-a-ya Na-mah",
        "Honour your roots. Ancestral support and regal confidence are with you today.",
        "Magha Nakshatra mantra"),
    NakshatraMantra("Purva Phalguni", 11, "Bhaga",
        "Om Bhagaya Namah",
        "Om Bha-ga-ya Na-mah",
        "Joy, pleasure, and the sweetness of life — savour every moment today.",
        "Purva Phalguni Nakshatra mantra"),
    NakshatraMantra("Uttara Phalguni", 12, "Aryaman",
        "Om Aryamanaya Namah",
        "Om Ar-ya-ma-na-ya Na-mah",
        "Contracts, commitments, and lasting partnerships are blessed today.",
        "Uttara Phalguni Nakshatra mantra"),
    NakshatraMantra("Hasta", 13, "Savitar (Sun of skill)",
        "Om Savitri Devaya Namah",
        "Om Sa-vit-ri Dev-a-ya Na-mah",
        "Skilled hands and a focused mind — craftsmanship and healing are favoured.",
        "Hasta Nakshatra mantra"),
    NakshatraMantra("Chitra", 14, "Vishwakarma / Tvashtr",
        "Om Vishwakarmane Namah",
        "Om Vish-wa-kar-ma-ne Na-mah",
        "Creative brilliance and the desire to build something beautiful.",
        "Chitra Nakshatra mantra"),
    NakshatraMantra("Swati", 15, "Vayu (Wind)",
        "Om Vayave Namah",
        "Om Va-ya-ve Na-mah",
        "Independent movement — a day for freedom, flexibility, and fresh air.",
        "Swati Nakshatra mantra"),
    NakshatraMantra("Vishakha", 16, "Indra-Agni",
        "Om Indragni Devabhyam Namah",
        "Om In-dra-gni Dev-a-bhyam Na-mah",
        "Purposeful ambition — stay focused on your goal and persevere.",
        "Vishakha Nakshatra mantra"),
    NakshatraMantra("Anuradha", 17, "Mitra",
        "Om Mitraya Namah",
        "Om Mit-ra-ya Na-mah",
        "Friendship, cooperation, and loyal bonds are the themes of today.",
        "Anuradha Nakshatra mantra"),
    NakshatraMantra("Jyeshtha", 18, "Indra",
        "Om Indraya Namah",
        "Om In-dra-ya Na-mah",
        "Seniority and leadership — take responsibility with grace and authority.",
        "Jyeshtha Nakshatra mantra"),
    NakshatraMantra("Mula", 19, "Niritti / Kali",
        "Om Niritidevyai Namah",
        "Om Ni-ri-ti Dev-yai Na-mah",
        "Get to the root of things. Deep inquiry and radical honesty set you free.",
        "Mula Nakshatra mantra"),
    NakshatraMantra("Purva Ashadha", 20, "Apas (Waters)",
        "Om Apas Devaya Namah",
        "Om A-pas Dev-a-ya Na-mah",
        "Cleanse and purify — release what's stagnant and let fresh energy flow.",
        "Purva Ashadha Nakshatra mantra"),
    NakshatraMantra("Uttara Ashadha", 21, "Vishwe Devas",
        "Om Vishwedevabhyo Namah",
        "Om Vish-we Dev-a-bhyo Na-mah",
        "Universal harmony — today's effort benefits not just you but everyone around you.",
        "Uttara Ashadha Nakshatra mantra"),
    NakshatraMantra("Shravana", 22, "Vishnu",
        "Om Vishnave Namah",
        "Om Vish-na-ve Na-mah",
        "Deep listening and sacred learning — wisdom comes through stillness today.",
        "Shravana Nakshatra Vishnu mantra"),
    NakshatraMantra("Dhanishtha", 23, "Vasus (8 divine beings)",
        "Om Vasubhyo Namah",
        "Om Va-sub-hyo Na-mah",
        "Prosperity and rhythm — align your actions with the natural flow of abundance.",
        "Dhanishtha Nakshatra mantra"),
    NakshatraMantra("Shatabhisha", 24, "Varuna",
        "Om Varunaya Namah",
        "Om Va-ru-na-ya Na-mah",
        "Healing, mystery, and the hidden dimensions of existence beckon today.",
        "Shatabhisha Nakshatra Varuna mantra"),
    NakshatraMantra("Purva Bhadrapada", 25, "Aja Ekapad",
        "Om Ajaika Padaya Namah",
        "Om A-jai-ka Pa-da-ya Na-mah",
        "Fierce transformation — the fire that forges diamonds from coal.",
        "Purva Bhadrapada Nakshatra mantra"),
    NakshatraMantra("Uttara Bhadrapada", 26, "Ahir Budhnya",
        "Om Ahir Budhnyaya Namah",
        "Om A-hir Budh-nya-ya Na-mah",
        "Depth, wisdom, and the comfort of ancient knowing. Rest in what is eternal.",
        "Uttara Bhadrapada Nakshatra mantra"),
    NakshatraMantra("Revati", 27, "Pushan",
        "Om Pushnay Namah",
        "Om Push-na-ye Na-mah",
        "Safe passage, nourishment, and the grace of completion. You are protected.",
        "Revati Nakshatra Pushan mantra"),
]

_NAK_BY_NAME: dict[str, NakshatraMantra] = {m.nakshatra: m for m in _NAK_MANTRAS}

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_planetary_mantra(planet: str) -> PlanetaryMantra:
    """Return the planetary mantra for the given Dasha lord."""
    return _PLANET_MANTRAS.get(planet, _PLANET_MANTRAS["Sun"])


def get_nakshatra_mantra(nakshatra_name: str) -> NakshatraMantra:
    """Return the mantra and energy card for the given Moon nakshatra."""
    return _NAK_BY_NAME.get(nakshatra_name, _NAK_MANTRAS[0])
