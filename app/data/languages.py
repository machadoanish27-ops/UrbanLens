"""Authoritative Country Languages and Cultural Metadata Registry.

Source: ISO-639 / UN Official Languages and UNESCO Linguistic Database.
All entries reflect country-level verified linguistic status.
"""

from typing import Any

# Authoritative country-level linguistic mapping verified against ISO 639-1 / UN data.
COUNTRY_LANGUAGE_REGISTRY: dict[str, dict[str, Any]] = {
    "JP": {
        "official_languages": ["Japanese"],
        "spoken_languages": ["Japanese"],
        "language_codes": ["ja"],
        "cultural_notes": "Japanese is the national language and official medium of government, education, and commerce across Japan.",
        "source": "ISO-639 / UN Linguistic Statistics & UNESCO World Languages",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
    "GB": {
        "official_languages": ["English"],
        "spoken_languages": ["English", "Scots", "Welsh", "Scottish Gaelic", "Irish"],
        "language_codes": ["en", "sco", "cy", "gd", "ga"],
        "cultural_notes": "English is the de facto official language of the United Kingdom. Welsh has de jure official status in Wales.",
        "source": "ISO-639 / UN Linguistic Statistics & UNESCO World Languages",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
    "IN": {
        "official_languages": ["Hindi", "English"],
        "spoken_languages": [
            "Hindi", "Bengali", "Marathi", "Telugu", "Tamil", "Gujarati",
            "Urdu", "Kannada", "Odia", "Malayalam", "Punjabi", "Assamese", "English"
        ],
        "language_codes": ["hi", "en", "bn", "mr", "te", "ta", "gu", "ur", "kn", "or", "ml", "pa", "as"],
        "cultural_notes": "Hindi in Devanagari script and English are the official languages of the Union of India under Article 343; the Eighth Schedule recognizes 22 scheduled languages.",
        "source": "ISO-639 / UN Linguistic Statistics & Constitution of India",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
    "US": {
        "official_languages": ["English"],
        "spoken_languages": ["English", "Spanish", "Chinese", "Tagalog", "Vietnamese", "Arabic", "French"],
        "language_codes": ["en", "es", "zh", "tl", "vi", "ar", "fr"],
        "cultural_notes": "English is the de facto national language of the United States and official in 32 individual states; the US has no federal de jure official language.",
        "source": "ISO-639 / US Census Bureau & UN Linguistic Database",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
    "FR": {
        "official_languages": ["French"],
        "spoken_languages": ["French", "Occitan", "Breton", "Alsatian", "Corsican", "Basque"],
        "language_codes": ["fr"],
        "cultural_notes": "French is the sole official language of the French Republic under Article 2 of the Constitution.",
        "source": "ISO-639 / UN Linguistic Statistics & Académie Française",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
    "SG": {
        "official_languages": ["English", "Malay", "Mandarin Chinese", "Tamil"],
        "spoken_languages": ["English", "Mandarin Chinese", "Malay", "Tamil", "Hokkien", "Teochew", "Cantonese"],
        "language_codes": ["en", "ms", "zh", "ta"],
        "cultural_notes": "Singapore has four official languages: English is the primary administrative and business language; Malay is the ceremonial national language.",
        "source": "ISO-639 / Government of Singapore & UN Linguistic Database",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
    "AE": {
        "official_languages": ["Arabic"],
        "spoken_languages": ["Arabic", "English", "Hindi", "Urdu", "Bengali", "Tagalog", "Persian"],
        "language_codes": ["ar", "en"],
        "cultural_notes": "Modern Standard Arabic is the official language of the United Arab Emirates. English is ubiquitous in business, commerce, and international services.",
        "source": "ISO-639 / UN Linguistic Statistics & UAE Government",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
    "DE": {
        "official_languages": ["German"],
        "spoken_languages": ["German", "Low German", "Sorbian", "Danish", "Frisian", "Romani"],
        "language_codes": ["de"],
        "cultural_notes": "Standard German (Hochdeutsch) is the official language throughout the Federal Republic of Germany.",
        "source": "ISO-639 / UN Linguistic Statistics",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
    "CN": {
        "official_languages": ["Standard Chinese (Mandarin)"],
        "spoken_languages": ["Mandarin", "Yue (Cantonese)", "Wu", "Min", "Xiang", "Hakka", "Gan", "Tibetan", "Uyghur", "Mongolian"],
        "language_codes": ["zh", "bo", "ug", "mn"],
        "cultural_notes": "Standard Chinese (Putonghua based on Beijing dialect) is the official national language of the People's Republic of China.",
        "source": "ISO-639 / UN Linguistic Statistics",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
    "IT": {
        "official_languages": ["Italian"],
        "spoken_languages": ["Italian", "German (South Tyrol)", "French (Aosta Valley)", "Sardinian", "Friulian", "Ladin"],
        "language_codes": ["it", "de", "fr"],
        "cultural_notes": "Italian is the official language throughout Italy; German and French have co-official regional status in Trentino-Alto Adige and Valle d'Aosta.",
        "source": "ISO-639 / UN Linguistic Statistics",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
    "ES": {
        "official_languages": ["Spanish (Castilian)"],
        "spoken_languages": ["Spanish", "Catalan", "Galician", "Basque", "Valencian", "Aranese"],
        "language_codes": ["es", "ca", "gl", "eu"],
        "cultural_notes": "Castilian Spanish is the official language of the state under Article 3 of the Spanish Constitution; Catalan, Galician, and Basque have co-official status in respective autonomous communities.",
        "source": "ISO-639 / UN Linguistic Statistics",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
    "CA": {
        "official_languages": ["English", "French"],
        "spoken_languages": ["English", "French", "Mandarin", "Cantonese", "Punjabi", "Spanish", "Tagalog", "Arabic", "Inuktitut", "Cree"],
        "language_codes": ["en", "fr"],
        "cultural_notes": "Canada is officially bilingual at the federal level under the Official Languages Act; French is the official language of Quebec.",
        "source": "ISO-639 / Statistics Canada & UN Linguistic Database",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
    "AU": {
        "official_languages": ["English"],
        "spoken_languages": ["English", "Mandarin", "Arabic", "Cantonese", "Vietnamese", "Italian", "Greek", "Hindi"],
        "language_codes": ["en"],
        "cultural_notes": "English is the de facto national and official language of Australia.",
        "source": "ISO-639 / Australian Bureau of Statistics & UN",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
    "BR": {
        "official_languages": ["Portuguese"],
        "spoken_languages": ["Portuguese", "Guarani", "Tikuna", "Kaingang", "German dialects (Hunsrik, Pomeranian)"],
        "language_codes": ["pt"],
        "cultural_notes": "Portuguese is the sole official language of the Federative Republic of Brazil.",
        "source": "ISO-639 / UN Linguistic Statistics",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
    "RU": {
        "official_languages": ["Russian"],
        "spoken_languages": ["Russian", "Tatar", "Chechen", "Bashkir", "Chuvash", "Avar"],
        "language_codes": ["ru", "tt", "ce", "ba", "cv"],
        "cultural_notes": "Russian is the official state language throughout the Russian Federation; individual republics co-recognize regional titular languages.",
        "source": "ISO-639 / UN Linguistic Statistics",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
    "ZA": {
        "official_languages": [
            "isiZulu", "isiXhosa", "Afrikaans", "Sepedi", "Setswana", "English",
            "Sesotho", "Xitsonga", "siSwati", "Tshivenda", "isiNdebele", "South African Sign Language"
        ],
        "spoken_languages": ["isiZulu", "isiXhosa", "Afrikaans", "Sepedi", "English", "Setswana"],
        "language_codes": ["zu", "xh", "af", "nso", "tn", "en", "st", "ts", "ss", "ve", "nr"],
        "cultural_notes": "South Africa has 12 official languages recognized in its Constitution; English is widely used in governance, higher education, and commerce.",
        "source": "ISO-639 / Constitution of the Republic of South Africa & UN",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
    "AF": {
        "official_languages": ["Pashto", "Dari"],
        "spoken_languages": ["Dari", "Pashto", "Uzbek", "English", "Turkmen", "Balochi"],
        "language_codes": ["ps", "fa", "uz", "tk"],
        "cultural_notes": "Pashto and Dari (Afghan Persian) are the official languages of Afghanistan.",
        "source": "ISO-639 / UN Linguistic Statistics",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
    "AO": {
        "official_languages": ["Portuguese"],
        "spoken_languages": ["Portuguese", "Umbundu", "Kimbundu", "Kikongo", "Chokwe", "Kwanyama"],
        "language_codes": ["pt"],
        "cultural_notes": "Portuguese is the sole official language of Angola; six Bantu languages are recognized as national languages.",
        "source": "ISO-639 / UN Linguistic Statistics",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
    "NL": {
        "official_languages": ["Dutch", "Frisian"],
        "spoken_languages": ["Dutch", "Frisian", "English", "Papiamento"],
        "language_codes": ["nl", "fy"],
        "cultural_notes": "Dutch is the official language throughout the Netherlands; West Frisian is co-official in Friesland.",
        "source": "ISO-639 / UN Linguistic Statistics",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
    "CH": {
        "official_languages": ["German", "French", "Italian", "Romansh"],
        "spoken_languages": ["Swiss German", "French", "Italian", "Romansh", "English"],
        "language_codes": ["de", "fr", "it", "rm"],
        "cultural_notes": "Switzerland has four national languages: German, French, and Italian are official federal languages; Romansh is official for relations with Romansh speakers.",
        "source": "ISO-639 / Swiss Federal Chancellery & UN",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
    "SE": {
        "official_languages": ["Swedish"],
        "spoken_languages": ["Swedish", "Finnish", "Meänkieli", "Sámi", "Romani", "Yiddish"],
        "language_codes": ["sv", "fi", "se"],
        "cultural_notes": "Swedish is the principal official language of Sweden under the 2009 Language Act; five national minority languages are officially recognized.",
        "source": "ISO-639 / UN Linguistic Statistics",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
    "KR": {
        "official_languages": ["Korean", "Korean Sign Language"],
        "spoken_languages": ["Korean"],
        "language_codes": ["ko"],
        "cultural_notes": "Korean is the official language of the Republic of Korea, written in Hangul.",
        "source": "ISO-639 / UN Linguistic Statistics",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
    "MX": {
        "official_languages": ["Spanish"],
        "spoken_languages": ["Spanish", "Nahuatl", "Maya", "Mixtec", "Zapotec"],
        "language_codes": ["es"],
        "cultural_notes": "Spanish is the de facto national language; the General Law on the Linguistic Rights of Indigenous Peoples recognizes 68 indigenous language families as national languages.",
        "source": "ISO-639 / INALI Mexico & UN",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
    "ID": {
        "official_languages": ["Indonesian"],
        "spoken_languages": ["Indonesian", "Javanese", "Sundanese", "Madurese", "Minangkabau", "Balinese"],
        "language_codes": ["id", "jv", "su"],
        "cultural_notes": "Indonesian (Bahasa Indonesia) is the sole official language of Indonesia; over 700 regional languages are spoken across the archipelago.",
        "source": "ISO-639 / Badan Bahasa Indonesia & UN",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
    "SA": {
        "official_languages": ["Arabic"],
        "spoken_languages": ["Arabic", "English"],
        "language_codes": ["ar"],
        "cultural_notes": "Arabic is the official language of the Kingdom of Saudi Arabia under Article 1 of the Basic Law of Governance.",
        "source": "ISO-639 / UN Linguistic Statistics",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
    "TR": {
        "official_languages": ["Turkish"],
        "spoken_languages": ["Turkish", "Kurdish (Kurmanji)", "Arabic", "Zaza", "Circassian"],
        "language_codes": ["tr", "ku"],
        "cultural_notes": "Turkish is the sole official language of the Republic of Turkey under Article 3 of the Constitution.",
        "source": "ISO-639 / Turkish Language Association & UN",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
    "AR": {
        "official_languages": ["Spanish"],
        "spoken_languages": ["Spanish (Rioplatense)", "Italian", "German", "English", "Guarani", "Quechua", "Mapudungun"],
        "language_codes": ["es"],
        "cultural_notes": "Spanish is the de facto official language of the Argentine Republic; Rioplatense dialect with voseo is predominant.",
        "source": "ISO-639 / UN Linguistic Statistics",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
    "NG": {
        "official_languages": ["English"],
        "spoken_languages": ["Hausa", "Yoruba", "Igbo", "Fulfulde", "Nigerian Pidgin", "English"],
        "language_codes": ["en", "ha", "yo", "ig"],
        "cultural_notes": "English is the official language of the Federal Republic of Nigeria; Hausa, Yoruba, and Igbo are the major national languages.",
        "source": "ISO-639 / UN Linguistic Statistics",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
    "EG": {
        "official_languages": ["Arabic"],
        "spoken_languages": ["Egyptian Arabic", "Modern Standard Arabic", "Sa'idi Arabic", "Bedawi Arabic", "Siwi"],
        "language_codes": ["ar"],
        "cultural_notes": "Modern Standard Arabic is the official language of the Arab Republic of Egypt under Article 2 of the Constitution; Egyptian Arabic is the spoken vernacular.",
        "source": "ISO-639 / UN Linguistic Statistics",
        "source_url": "https://www.iso.org/iso-639-language-codes.html",
        "level": "country",
    },
}


COMMON_NAME_TO_ISO2: dict[str, str] = {
    "japan": "JP",
    "united kingdom": "GB",
    "uk": "GB",
    "great britain": "GB",
    "england": "GB",
    "india": "IN",
    "united states": "US",
    "usa": "US",
    "france": "FR",
    "singapore": "SG",
    "united arab emirates": "AE",
    "uae": "AE",
    "germany": "DE",
    "china": "CN",
    "italy": "IT",
    "spain": "ES",
    "canada": "CA",
    "australia": "AU",
    "brazil": "BR",
    "russia": "RU",
    "south africa": "ZA",
    "afghanistan": "AF",
    "angola": "AO",
    "netherlands": "NL",
    "switzerland": "CH",
    "sweden": "SE",
    "south korea": "KR",
    "korea": "KR",
    "mexico": "MX",
    "indonesia": "ID",
    "saudi arabia": "SA",
    "turkey": "TR",
    "argentina": "AR",
    "nigeria": "NG",
    "egypt": "EG",
}


def get_country_languages(country_identifier: str | None, iso2_hint: str | None = None) -> dict[str, Any]:
    """Resolve authoritative country language metadata with provenance.
    
    Accepts country_id (e.g. 'country_JP', 'japan'), ISO2 code (e.g. 'JP'), or ISO3.
    Returns structured dict adhering to the CountryLanguageInfo contract.
    """
    if iso2_hint and iso2_hint.strip().upper() in COUNTRY_LANGUAGE_REGISTRY:
        iso2 = iso2_hint.strip().upper()
        entry = COUNTRY_LANGUAGE_REGISTRY[iso2]
        return {
            "country_id": f"country_{iso2}",
            "country_iso2": iso2,
            "status": "available",
            "official_languages": list(entry["official_languages"]),
            "spoken_languages": list(entry["spoken_languages"]),
            "language_codes": list(entry["language_codes"]),
            "cultural_notes": entry["cultural_notes"],
            "source": entry["source"],
            "source_url": entry["source_url"],
            "level": "country",
        }

    if not country_identifier:
        return {
            "country_id": "unknown",
            "country_iso2": None,
            "status": "unavailable",
            "official_languages": [],
            "spoken_languages": [],
            "language_codes": [],
            "cultural_notes": "No country identifier supplied.",
            "source": None,
            "source_url": None,
            "level": "country",
        }

    raw = country_identifier.strip()
    iso2 = ""
    country_id = raw

    if raw.startswith("country_"):
        code_part = raw.split("_", 1)[1].strip()
        if len(code_part) == 2:
            iso2 = code_part.upper()
            country_id = f"country_{iso2}"
        elif code_part.lower() in COMMON_NAME_TO_ISO2:
            iso2 = COMMON_NAME_TO_ISO2[code_part.lower()]
            country_id = f"country_{iso2}"
    elif len(raw) == 2:
        iso2 = raw.upper()
        country_id = f"country_{iso2}"
    elif len(raw) == 3:
        iso3_to_iso2 = {
            "JPN": "JP", "GBR": "GB", "IND": "IN", "USA": "US", "FRA": "FR",
            "SGP": "SG", "ARE": "AE", "DEU": "DE", "CHN": "CN", "ITA": "IT",
            "ESP": "ES", "CAN": "CA", "AUS": "AU", "BRA": "BR", "RUS": "RU",
            "ZAF": "ZA", "AFG": "AF", "AGO": "AO", "NLD": "NL", "CHE": "CH",
            "SWE": "SE", "KOR": "KR", "MEX": "MX", "IDN": "ID", "SAU": "SA",
            "TUR": "TR", "ARG": "AR", "NGA": "NG", "EGY": "EG",
        }
        iso2 = iso3_to_iso2.get(raw.upper(), "")
        country_id = f"country_{iso2}" if iso2 else raw
    elif raw.lower() in COMMON_NAME_TO_ISO2:
        iso2 = COMMON_NAME_TO_ISO2[raw.lower()]
        country_id = f"country_{iso2}"

    entry = COUNTRY_LANGUAGE_REGISTRY.get(iso2)
    if entry:
        return {
            "country_id": country_id,
            "country_iso2": iso2,
            "status": "available",
            "official_languages": list(entry["official_languages"]),
            "spoken_languages": list(entry["spoken_languages"]),
            "language_codes": list(entry["language_codes"]),
            "cultural_notes": entry["cultural_notes"],
            "source": entry["source"],
            "source_url": entry["source_url"],
            "level": "country",
        }

    return {
        "country_id": country_id,
        "country_iso2": iso2 if iso2 else None,
        "status": "unavailable",
        "official_languages": [],
        "spoken_languages": [],
        "language_codes": [],
        "cultural_notes": f"Authoritative language metadata is not currently indexed in UrbanLens for territory '{raw}'.",
        "source": None,
        "source_url": None,
        "level": "country",
    }
