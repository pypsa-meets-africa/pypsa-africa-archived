

# ===============================
# OSM FEATURE COLUMNS
# ===============================
# The feature category represents the final representation of the feature
# For node features: ways are converted to nodes
# For way features: only ways are used

feature_category = {
    "substation": "node",
    "generator": "node",
    "line": "way",
    "tower": "node",
    "cable": "way",
}

# ===============================
# OSM FEATURE COLUMNS
# ===============================
# These configurations are used to specify which OSM tags are kept as columns in DataFrame.
# Follows the OSM Wiki: https://wiki.openstreetmap.org/wiki/Power

# "Length" is added for way features
# "Area" is added for node features

# ========================
# BASIC INFO TAGS
# ========================
# A list of tags that are relevant for most OSM keys

columns_basic = [
    "id",
    "lonlat",
    "tags.power",
    "Type",
    "Country",
    # "refs"
]

# ========================
# SUBSTATION TAGS
# ========================

# Default tags to keep as columns with substation
# Based on: https://wiki.openstreetmap.org/wiki/Key:substation
columns_substation = [
    "Area",
    "tags.substation",
    "tags.voltage",
    # Other tags which are not kept by default
    # =====================================
    # "TODO:ADD Tags not kept here",
]

# ========================
# GENERATOR TAGS
# ========================

# Default tags to keep as columns with generator
# Based on: https://wiki.openstreetmap.org/wiki/Key:generator

columns_generator = [
    "Area",
    "tags.generator:type",
    "tags.generator:method",
    "tags.generator:source",
    "tags.generator:output:electricity",
    # Other tags which are not kept by default
    # =====================================
    # "TODO:ADD Tags not kept here",
]

# ========================
# LINE TAGS
# ========================

# Default tags to keep as columns with line
# Based on: https://wiki.openstreetmap.org/wiki/Key:line

columns_line = [
    "Length",
    "tags.cables",
    "tags.voltage",
    "tags.circuits",
    "tags.frequency",
    # Other tags which are not kept by default
    # =====================================
    # "TODO:ADD Tags not kept here",
]

# ========================
# CABLE TAGS
# ========================

# Default tags to keep as columns with substation
# Based on: https://wiki.openstreetmap.org/wiki/Key:cable

columns_cable = [
    "Length",
    "tags.cables",
    "tags.voltage",
    "tags.circuits",
    "tags.frequency",
    "tags.location",
    # Other tags which are not kept by default
    # =====================================
    # "TODO:ADD Tags not kept here",
]

# ========================
# TOWER TAGS
# ========================

# Default tags to keep as columns with tower
# Based on: https://wiki.openstreetmap.org/wiki/Key:tower

columns_tower = [
    "Area",
    "tags.tower",
    "tags.material",
    "tags.structure",
    "tags.operator",
    "tags.line_attachment",
    "tags.line_management",
    "tags.ref",
    "tags.height",
    # Other tags which are not kept by default
    # =====================================
    # "TODO:ADD Tags not kept here",
]

# FINAL DICTIONARY

feature_columns = {
    "substation": columns_basic + columns_substation,
    "generator": columns_basic + columns_generator,
    "line": columns_basic + columns_line,
    "cable": columns_basic + columns_cable,
    "tower": columns_basic + columns_tower,
}



# Python dictionary of ISO 3166-1-alpha-2 codes, as per publicly
# available data on official ISO site in July 2015.
#
# Available under MIT license
# Dimitris Karagkasidis, https://github.com/pageflt

continents = {
    'LA': 'latin_america',
    'SA': 'south_america', 
    'CA': 'central_america',
    'AS': 'asia',
    'OC': 'australia',
    'AF': 'africa',
    'EU': 'europe',
    #'AN': 'antarctica'
}

world = {"africa": {"DZ": "algeria",
                    "AO": "angola",
                    "BJ": "benin",
                    "BW": "botswana", 
                    "BF": "burkina-faso",
                    "BI": "burundi",
                    "CM": "cameroon",
                    # canary-islands    # Island
                    # "CV": "cape-verde", # Island
                    "CF": "central-african-republic",
                    "TD": "chad",
                    # "KM": "comores", # Island
                    "CG": "congo-brazzaville",
                    "CD": "congo-democratic-republic",
                    "DJ": "djibouti",
                    "EG": "egypt",
                    "GQ": "equatorial-guinea",
                    "ER": "eritrea",
                    "ET": "ethiopia",
                    "GA": "gabon",
                    "GH": "ghana",
                    "GW": "guinea-bissau", # No Data
                    "GN": "guinea",
                    "CI": "ivory-coast",
                    "KE": "kenya",
                    "LS": "lesotho",
                    "LR": "liberia",
                    "LY": "libya",
                    "MG": "madagascar",
                    "MW": "malawi",
                    "ML": "mali",
                    "MR": "mauritania",
                    "MU": "mauritius",
                    "MA": "morocco",
                    "MZ": "mozambique",
                    "NA": "namibia",
                    "NE": "niger",
                    "NG": "nigeria",
                    "RW": "rwanda",
                    # saint-helena-ascension-and-tristan-da-cunha
                    # "ST": "sao-tome-and-principe", #Island
                    #"SNGM": "senegal-and-gambia",  # See Map # Self-created country code
                    # "SN": "senegal",
                    # "GM": "gambia",
                    # "SC": "seychelles", #Island
                    "SL": "sierra-leone",
                    "SO": "somalia", # No Data
                    # south-africa-and-lesotho
                    "ZA": "south-africa",
                    "SS": "south-sudan",
                    "SD": "sudan",
                    "SZ": "swaziland",
                    "TZ": "tanzania",
                    "TG": "togo",
                    "TN": "tunisia",
                    "UG": "uganda",
                    "ZM": "zambia",
                    "ZW": "zimbabwe"
                    },

        "asia" : {
                    'AF': 'afghanistan',
                    'AM': 'armenia',
                    'AZ': 'azerbaijan',
                    # 'BH': 'bahrain',
                    'BD': 'bangladesh',
                    'BT': 'bhutan',
                    # 'IO': 'british indian ocean territory',
                    # 'BN': 'brunei darussalam', # merged with MY
                    'KH': 'cambodia',
                    'CN': 'china',
                    # 'CX': 'christmas island',
                    # 'CC': 'cocos (keeling) islands',
                    'CY': 'cyprus',
                    'GE': 'georgia',
                    'HK': 'hong kong',
                    'IN': 'india',
                    'ID': 'indonesia',
                    'IR': 'iran',
                    'IQ': 'iraq',
                    'IL-PL': 'israel-and-palestine',
                    'JP': 'japan',
                    'JO': 'jordan',
                    'KZ': 'kazakhstan',
                    'KP': "north-korea",
                    'KR': 'south-korea',
                    # 'KW': 'kuwait',
                    'KG': 'kyrgyzstan',
                    # 'LA': "lao people's democratic republic",
                    'LB': 'lebanon',
                    'MO': 'macao',
                    'MY-SG-BN': 'malaysia-singapore-brunei', # Note 3 countries based on geofabrik
                    'MV': 'maldives',
                    'MN': 'mongolia',
                    'MM': 'myanmar',
                    'NP': 'nepal',
                    # 'OM': 'oman',
                    'PK': 'pakistan',
                    # 'PS': 'palestine',
                    'PH': 'philippines',
                    # 'QA': 'qatar',
                    # 'SA': 'saudi arabia',
                    # 'SG': 'singapore', # merged with MY
                    'LK': 'sri-lanka',
                    'SY': 'syria',
                    'TW': 'taiwan',
                    'TJ': 'tajikistan',
                    'TH': 'thailand',
                    'TR': 'turkey',
                    'TM': 'turkmenistan',
                    # 'AE': 'united arab emirates',
                    'UZ': 'uzbekistan',
                    'VN': 'vietnam',
                    'YE': 'yemen'
                    },

        "australia" : {
                    'AS': 'american-oceania',
                    'AU': 'australia',
                    #'CK': 'cook islands',
                    'FJ': 'fiji',
                    'PF': 'french-polynesia',
                    'GU': 'guam',
                    'KI': 'kiribati',
                    #'MH': 'marshall islands',
                    'FM': 'micronesia',
                    'NR': 'nauru',
                    'NC': 'new-caledonia',
                    'NZ': 'new-zealand',
                    'NU': 'niue',
                    'NF': 'norfolk island',
                    #'MP': 'northern mariana islands',
                    'PW': 'palau',
                    'PG': 'papua-new-guinea',
                    'WS': 'samoa',
                    #'SB': 'solomon islands',
                    'TK': 'tokelau',
                    'TO': 'tonga',
                    'TV': 'tuvalu',
                    'VU': 'vanuatu',
                    'WF': 'wallis-et-futuna'
                    },

        "europe" : {
                    'AL': 'albania',
                    'AD': 'andorra',
                    'AT': 'austria',
                    'BY': 'belarus',
                    'BE': 'belgium',
                    'BA': 'bosnia-herzegovina',
                    'BG': 'bulgaria',
                    'HR': 'croatia',
                    'CZ': 'czech-republic',
                    'DK': 'denmark',
                    'EE': 'estonia',
                    'FO': 'faroe islands',
                    'FI': 'finland',
                    'FR': 'france',
                    'DE': 'germany',
                    # 'GI': 'gibraltar', Island ?
                    'GR': 'greece',
                    # 'GG': 'guernsey', Island 
                    'HU': 'hungary',
                    'IS': 'iceland',
                    'IE': 'ireland-and-northern-ireland',
                    # 'IM': 'isle of man',
                    'IT': 'italy',
                    # 'JE': 'jersey',
                    'LV': 'latvia',
                    'LI': 'liechtenstein',
                    'LT': 'lithuania',
                    'LU': 'luxembourg',
                    'MK': 'macedonia',
                    'MT': 'malta',
                    'MD': 'moldova',
                    'MC': 'monaco',
                    'ME': 'montenegro',
                    'NL': 'netherlands',
                    'NO': 'norway',
                    'PL': 'poland',
                    'PT': 'portugal',
                    'RO': 'romania',
                    'RU': 'russia',
                    # 'SM': 'san-marino',
                    'RS': 'serbia',
                    'SK': 'slovakia',
                    'SI': 'slovenia',
                    'ES': 'spain',
                    # 'SJ': 'svalbard-and-jan-mayen',
                    'SE': 'sweden',
                    'CH': 'switzerland',
                    'UA': 'ukraine',
                    'GB': 'great-britain'
                    },

        "north_america" : {
                    'CA': 'canada',
                    'GL': 'greenland',
                    'MX': 'mexico',
                    'US': 'united states'
                    },

        "latin_america" : {
                    "AR" : "argentina", 
                    "BO" : "bolivia", 
                    "BR" : "brazil", 
                    "CL" : "chile", 
                    "CO" : "colombia", 
                    "EC" : "ecuador", 
                    "PE" : "peru", 
                    "SR" : "suriname", 
                    "UY" : "uruguay", 
                    "VE" : "venezuela"
                    },

        "central_america" : {
                    "BZ" : "belize", 
                    "GT" : "guatemala", 
                    "SV" : "el-salvador", 
                    "HN" : "honduras", 
                    "NI" : "nicaragua", 
                    "CR" : "costa-rica"
                    }
}

world_countries = {country_2D: country_name for d in world.values() for (country_2D, country_name) in d.items()}

continent_regions = { 
    # Based on: https://waml.org/waml-information-bulletin/46-3/index-to-lc-g-schedule/1-world/ 
    # Eurpean regions 
    "SCR" : ["DK","NO","SE","FI","IS"], # SCANDANAVIAN REGION
    "EER" : ["BY","BU","CZ","RU","SK","UA","GB","LT","LV","EE"], # EASTREN EUROPIAN REGION
    "CER" : ["AT", "CH", "CZ", "DE", "HU", "PL", "SK"], # CENTRAL EUROPIAN REGION 
    "BPR" : ["AL","AN","BA","BG", "GR", "HR", "MD", "MT", "RO", "SL","RS","ME","MK"], # BALKAN PENISULAN REGION     
    "WER" : ["FR", "BE", "GB", "IE", "LU", "MC", "NL"], # WESTREN EUROPE
    "SER" : ["ES", "IT","PT"], # SOUTHERN EUROPAIN REGION
    
    # African regions 
    "NAR" : ["EG", "DZ", "LY","MA", "SD", "SS"], # NORTHERN AFRICAN REGION 
    "WAR" : ["MR", "ML", "NE", "NG", "BJ", "BF", "TG", "GH", "CI", "LR", "SL","GN", "GM", "SL"], # WESTREN AFRICAN REGION
    "CAR" : ["TD", "CF", "CM", "GQ", "GA", "CD", "CG", "AO"], # CENTRAL AFRICAN REGION 
    "EAR" : ["ET", "UG", "KE", "RW", "BI", "TZ", "MZ", "DJ", "MG"], # EASTREN AFRICAN REGION 
    "SAR" : ["MW", "ZM","ZW", "BW", "NA", "SZ", "LS", "ZA"], # SOUTHERN AFRICAN REGION 

    # Asian regions 
    "FEAR" : ["JP", "KP", "KR", "CN", "TW", "CN", "MN"], # FAR EASTREN AISIAN REGION 
    "SEAR" : ["LA", "TH", "KH", "VN", "PH", "MYSGBN", "ID" ], # SOUTHEASTREN AISIAN REGION 
    "CAR" : ["KZ", "KG", "UZ", "TM", "TJ"], # CENTRAL AISIAN REGION
    "SAR" : ["MM", "BD", "BT", "NP", "IN","LK", "PK", "AF"], # SOUTHERN AISIAN REGION 
    "MEAR" : ["TR", "SY", "IQ", "IR", "JO", "IL", "AE", "YE"], # MIDDLE EASTREN ASIAN REGION 

    # American continent regions
    "NACR" : ["CA", "GL", "MX", "US"], # NORTHREN AMERCIAN CONTINENT REGION
    "LACR" : ["AR", "BO", "BR", "CL", "CO", "EC", "PE", "SR", "UY", "VE"], # SOUTHERN LATIN AMERICAL REGION 
    "CACR" : ["BZ", "GT", "SV", "HN", "NI", "CR"], # CENTRAL AMERICAN REGION 

    # Customized test set
    "TEST" : ["NG", "NE", "SL", "MA"],
}