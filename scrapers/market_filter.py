"""
Comprehensive Asian keyword filter for Polymarket markets
Filters markets by relevance to Asian audience across 5 categories
"""

# ============================================================================
# SPORTS KEYWORDS (~200 keywords)
# ============================================================================

SPORTS_COUNTRIES = [
    "China", "Japan", "Korea", "South Korea", "North Korea", "India",
    "Pakistan", "Bangladesh", "Indonesia", "Thailand", "Vietnam",
    "Philippines", "Malaysia", "Singapore", "Taiwan", "Hong Kong",
    "Nepal", "Sri Lanka", "Myanmar", "Burma", "Cambodia", "Laos",
    "Mongolia", "Kazakhstan", "Uzbekistan", "Afghanistan", "Iran",
    "Iraq", "Saudi Arabia", "UAE", "Qatar", "Jordan", "Lebanon",
    "Asia", "Asian", "Southeast Asia", "East Asia", "South Asia"
]

SPORTS_TYPES = [
    "cricket", "Cricket", "badminton", "Badminton", "table tennis",
    "Table Tennis", "kabaddi", "Kabaddi", "martial arts", "taekwondo",
    "Taekwondo", "karate", "Karate", "judo", "Judo", "sumo", "Sumo",
    "sepak takraw"
]

SPORTS_LEAGUES = [
    "Chinese Super League", "CSL", "J-League", "J.League", "J League",
    "K-League", "K League", "K.League", "AFC", "Asian Champions League",
    "ACL", "IPL", "Indian Premier League", "BBL", "Big Bash",
    "PSL", "Pakistan Super League", "LCK", "LPL", "PCS", "NPB",
    "Nippon Professional Baseball", "KBO", "Korean Baseball",
    "Asian Cup", "AFC Asian Cup", "Asian Games", "FIBA Asia",
    "Asia Cup", "Badminton Asia", "SEA Games", "Southeast Asian Games"
]

SPORTS_TEAMS = [
    "Al-Hilal", "Al Hilal", "Al-Nassr", "Al Nassr", "Mumbai Indians",
    "Chennai Super Kings", "Royal Challengers", "RCB", "Guangzhou",
    "Shanghai SIPG", "Shanghai Port", "Beijing Guoan", "Urawa Red Diamonds",
    "Kashima Antlers", "Jeonbuk", "Ulsan Hyundai", "Pohang Steelers",
    "Yokohama", "Kawasaki Frontale", "FC Tokyo"
]

SPORTS_PLAYERS = [
    "Son Heung-min", "Son", "Heung-min", "Takefusa Kubo", "Kubo",
    "Shinji Kagawa", "Kagawa", "Park Ji-sung", "Virat Kohli", "Kohli",
    "Rohit Sharma", "MS Dhoni", "Dhoni", "Sachin Tendulkar", "Tendulkar",
    "Babar Azam", "Rashid Khan", "Jasprit Bumrah", "Bumrah",
    "Shohei Ohtani", "Ohtani", "Ryu Hyun-jin", "Wu Lei",
    "Takumi Minamino", "Minamino", "Takehiro Tomiyasu", "Tomiyasu",
    "Kaoru Mitoma", "Mitoma", "Lee Kang-in", "Hwang Hee-chan",
    "Kim Min-jae"
]

# ============================================================================
# ENTERTAINMENT KEYWORDS (~250 keywords)
# ============================================================================

KPOP_GROUPS = [
    "BTS", "Blackpink", "BLACKPINK", "Twice", "TWICE", "EXO", "NCT",
    "Stray Kids", "Seventeen", "TXT", "Tomorrow X Together", "Enhypen",
    "ENHYPEN", "Aespa", "aespa", "NewJeans", "New Jeans", "IVE",
    "Le Sserafim", "LE SSERAFIM", "Red Velvet", "Itzy", "ITZY",
    "(G)I-DLE", "GIDLE", "Mamamoo", "MAMAMOO", "GOT7", "Monsta X",
    "MONSTA X", "Ateez", "ATEEZ", "The Boyz", "Treasure", "Astro",
    "Pentagon", "SF9", "Day6", "BigBang", "BIGBANG", "2NE1",
    "Girls Generation", "SNSD", "Super Junior", "SHINee", "f(x)",
    "Wonder Girls", "Apink", "Oh My Girl", "NMIXX", "Kep1er",
    "Loona", "LOONA", "Everglow", "Dreamcatcher", "Fromis_9"
]

KPOP_SOLOISTS = [
    "IU", "Taeyeon", "Jennie", "Rosé", "ROSÉ", "Lisa", "LISA",
    "Jisoo", "JISOO", "Jungkook", "V", "BTS V", "Jimin", "RM",
    "Suga", "SUGA", "Jin", "J-Hope", "Jhope", "Baekhyun", "Kai",
    "Taemin", "G-Dragon", "GD", "Taeyang", "PSY", "Sunmi", "Chungha",
    "Hyuna", "HyunA", "Jay Park", "Zico", "CL", "Somi", "Kang Daniel"
]

ASIAN_ACTORS = [
    "Lee Min-ho", "Lee Min Ho", "Song Joong-ki", "Song Joong Ki",
    "Hyun Bin", "Park Seo-joon", "Park Seo Joon", "Kim Soo-hyun",
    "Kim Soo Hyun", "Song Hye-kyo", "Song Hye Kyo", "Jun Ji-hyun",
    "Bae Suzy", "Suzy", "Park Bo-gum", "Park Bo Gum", "Kim Tae-hee",
    "Lee Jong-suk", "Lee Jong Suk", "Park Shin-hye", "Park Shin Hye",
    "Ken Watanabe", "Rinko Kikuchi", "Takeshi Kaneshiro",
    "Shah Rukh Khan", "SRK", "Salman Khan", "Aamir Khan",
    "Priyanka Chopra", "Deepika Padukone", "Ranveer Singh",
    "Alia Bhatt", "Aishwarya Rai", "Amitabh Bachchan"
]

ENTERTAINMENT_CONTENT = [
    "Bollywood", "Tollywood", "K-drama", "Kdrama", "Korean drama",
    "Japanese cinema", "Hong Kong cinema", "Parasite", "Squid Game",
    "Pachinko", "Shōgun", "Shogun", "Hellbound", "All of Us Are Dead",
    "My Name", "Kingdom", "Alice in Borderland", "anime", "Anime",
    "Studio Ghibli", "Ghibli", "Hayao Miyazaki", "Miyazaki",
    "Attack on Titan", "Demon Slayer", "Kimetsu no Yaiba",
    "One Piece", "Naruto", "Dragon Ball", "Your Name", "Kimi no Na wa",
    "Spirited Away", "Princess Mononoke", "Weathering with You",
    "Jujutsu Kaisen", "Chainsaw Man", "Spy x Family", "My Hero Academia"
]

ENTERTAINMENT_AWARDS = [
    "Baeksang", "Baeksang Arts Awards", "Blue Dragon", "Golden Horse",
    "Golden Horse Awards", "Filmfare", "Filmfare Awards",
    "MAMA", "MAMA Awards", "Melon Music Awards", "MMA",
    "Mnet Asian Music Awards", "Golden Disc", "Seoul Music Awards",
    "SMA", "Gaon Chart", "Circle Chart", "Oscar Asia", "Grammy Asia"
]

ENTERTAINMENT_PLATFORMS = [
    "Netflix Asia", "Viu", "iQIYI", "Youku", "Tencent Video",
    "WeTV", "Viki", "Rakuten Viki", "Disney+ Hotstar", "Hotstar"
]

# ============================================================================
# POLITICS KEYWORDS (~120 keywords)
# ============================================================================

POLITICAL_LEADERS = [
    "Xi Jinping", "Xi", "Narendra Modi", "Modi", "Fumio Kishida",
    "Kishida", "Yoon Suk-yeol", "Yoon", "Moon Jae-in",
    "Joko Widodo", "Jokowi", "Prabowo", "Ferdinand Marcos Jr",
    "Marcos Jr", "Rodrigo Duterte", "Duterte", "Sheikh Hasina",
    "Imran Khan", "Lee Hsien Loong", "Anwar Ibrahim",
    "Tsai Ing-wen", "William Lai", "Lai Ching-te", "Kim Jong-un",
    "Shinzo Abe", "Abe"
]

POLITICAL_PARTIES = [
    "CCP", "Chinese Communist Party", "BJP", "Bharatiya Janata Party",
    "Indian National Congress", "Congress Party", "LDP",
    "Liberal Democratic Party", "DPP", "Democratic Progressive Party",
    "KMT", "Kuomintang", "PAP", "People's Action Party",
    "UMNO", "PKR", "Democratic Party of Korea"
]

POLITICAL_COUNTRIES = [
    "China", "PRC", "People's Republic of China", "Japan", "Korea",
    "South Korea", "North Korea", "DPRK", "India", "Pakistan",
    "Bangladesh", "Indonesia", "Philippines", "Thailand", "Vietnam",
    "Taiwan", "Hong Kong", "Singapore", "Malaysia", "Myanmar",
    "Burma", "Cambodia", "Laos", "Nepal", "Sri Lanka", "Mongolia",
    "Afghanistan", "Iran", "Iraq", "Saudi Arabia", "UAE", "Qatar",
    "Kazakhstan", "Uzbekistan", "Turkmenistan", "Kyrgyzstan"
]

POLITICAL_ISSUES = [
    "South China Sea", "Kashmir", "China-Taiwan", "Taiwan Strait",
    "Hong Kong protests", "Hong Kong", "Uyghur", "Tibet", "Xinjiang",
    "North Korea nuclear", "ASEAN", "RCEP", "Belt and Road", "BRI",
    "Quad", "AUKUS", "India-Pakistan", "India-China", "border dispute",
    "East China Sea", "Senkaku", "Diaoyu", "One China", "reunification",
    "democracy Hong Kong", "National Security Law"
]

# ============================================================================
# ECONOMICS KEYWORDS (~150 keywords)
# ============================================================================

STOCK_MARKETS = [
    "Nikkei", "Nikkei 225", "Hang Seng", "HSI", "Shanghai Composite",
    "SSE", "Shanghai Stock Exchange", "Shenzhen", "SZSE", "KOSPI",
    "Sensex", "BSE Sensex", "NSE", "National Stock Exchange India",
    "Nifty", "Nifty 50", "Straits Times Index", "STI",
    "Jakarta Composite", "JCI", "Taiwan Weighted", "TAIEX",
    "SET Index", "Thailand stock", "PSE", "Philippine Stock Exchange"
]

ASIAN_COMPANIES = [
    "Samsung", "TSMC", "Taiwan Semiconductor", "Toyota", "Sony",
    "Honda", "Nissan", "Mazda", "Subaru", "Tencent", "Alibaba",
    "Baidu", "ByteDance", "TikTok", "Xiaomi", "Huawei", "NIO", "BYD",
    "XPeng", "Li Auto", "Reliance", "Reliance Industries", "TCS",
    "Tata", "Tata Motors", "Infosys", "Wipro", "SoftBank", "Mitsubishi",
    "Mitsui", "Sumitomo", "Hyundai", "Kia", "LG", "SK Hynix",
    "Samsung Electronics", "Foxconn", "Hon Hai", "ICBC",
    "China Mobile", "China Construction Bank", "Agricultural Bank of China",
    "Bank of China", "Ping An", "Ant Group", "Meituan", "JD.com",
    "JD", "Pinduoduo", "PDD", "DiDi", "Sea Limited", "Grab", "Gojek",
    "Rakuten", "SBI Holdings", "Naver", "Kakao", "Coupang",
    "SK Telecom", "China Telecom", "Sinopec", "PetroChina"
]

CURRENCIES = [
    "yuan", "renminbi", "RMB", "CNY", "yen", "JPY", "rupee", "INR",
    "won", "KRW", "ringgit", "MYR", "baht", "THB", "peso", "PHP",
    "dong", "VND", "rupiah", "IDR", "Singapore dollar", "SGD",
    "Hong Kong dollar", "HKD", "Taiwan dollar", "TWD", "taka", "BDT",
    "riyal", "SAR", "dirham", "AED"
]

ECONOMIC_EVENTS = [
    "Chinese GDP", "China economy", "Japanese inflation", "Bank of Japan",
    "BoJ", "Reserve Bank of India", "RBI", "Indian economy",
    "Asian recession", "China property", "Evergrande", "Country Garden",
    "China tech crackdown", "Chinese tech", "Asian growth",
    "China manufacturing", "PMI China", "PMI Japan", "PMI India",
    "PBOC", "People's Bank of China", "China stimulus"
]

# ============================================================================
# TECHNOLOGY/GAMING KEYWORDS (~150 keywords)
# ============================================================================

TECH_COMPANIES = [
    "TikTok", "WeChat", "Weixin", "Line", "LINE", "Kakao", "KakaoTalk",
    "Naver", "Grab", "Gojek", "Sea Limited", "Shopee", "Lazada",
    "Rakuten", "Mercari", "Paytm", "PhonePe", "Flipkart", "Coupang",
    "Tokopedia", "Bukalapik", "Zomato", "Swiggy", "Ola", "Careem",
    "Agora", "Zoom China", "DingTalk", "Lark", "Tencent Cloud",
    "Alibaba Cloud", "Aliyun", "Huawei Cloud", "Samsung Cloud"
]

GAMING_COMPANIES = [
    "Nintendo", "PlayStation Asia", "Sony Interactive", "Konami",
    "Capcom", "Bandai Namco", "Square Enix", "Sega", "From Software",
    "FromSoftware", "NetEase", "Perfect World", "Netmarble", "NCSoft",
    "Nexon", "miHoYo", "HoYoverse", "Krafton", "Pearl Abyss", "Smilegate"
]

GAMES = [
    "League of Legends", "LoL", "LCK", "LPL", "LMS", "PCS",
    "Valorant", "VCT Pacific", "PUBG Mobile", "PUBG", "PMGC",
    "Honor of Kings", "Arena of Valor", "Genshin Impact", "Genshin",
    "Mobile Legends", "MLBB", "Free Fire", "Crossfire", "CF",
    "Dungeon Fighter Online", "DFO", "Lost Ark", "Black Desert",
    "Lineage", "MapleStory", "Blade & Soul", "Tower of Fantasy",
    "Honkai Star Rail", "Honkai Impact", "Blue Archive", "Azur Lane",
    "Pokemon", "Pokémon", "Digimon", "Final Fantasy XIV", "FFXIV"
]

ESPORTS_TEAMS = [
    "T1", "Gen.G", "GenG", "DRX", "DWG KIA", "Hanwha Life", "HLE",
    "KT Rolster", "Edward Gaming", "EDG", "JD Gaming", "JDG",
    "Royal Never Give Up", "RNG", "FunPlus Phoenix", "FPX",
    "Invictus Gaming", "IG", "Top Esports", "TES", "Bilibili Gaming",
    "BLB", "LNG Esports", "Weibo Gaming", "WBG", "Paper Rex",
    "PRX", "DRX Valorant", "ZETA Division"
]

ESPORTS_PLAYERS = [
    "Faker", "Lee Sang-hyeok", "Uzi", "Rookie", "TheShy", "Deft",
    "Chovy", "ShowMaker", "Canyon", "Ruler", "Viper", "Knight",
    "Bin", "369", "Xiaohu", "Meiko", "Zeus", "Keria", "Gumayusi",
    "Oner", "JackeyLove", "Crisp", "Yagao", "Kanavi"
]

AI_TECH = [
    "SenseTime", "Megvii", "Face++", "Alibaba Cloud AI", "Tencent Cloud AI",
    "Huawei AI", "Samsung AI", "LG AI", "Naver AI", "Kakao Brain",
    "LINE Brain", "Baidu AI", "Baidu Ernie", "Alibaba Tongyi"
]

# ============================================================================
# COMBINED KEYWORDS
# ============================================================================

ALL_ASIAN_KEYWORDS = (
    SPORTS_COUNTRIES + SPORTS_TYPES + SPORTS_LEAGUES + SPORTS_TEAMS + SPORTS_PLAYERS +
    KPOP_GROUPS + KPOP_SOLOISTS + ASIAN_ACTORS + ENTERTAINMENT_CONTENT +
    ENTERTAINMENT_AWARDS + ENTERTAINMENT_PLATFORMS +
    POLITICAL_LEADERS + POLITICAL_PARTIES + POLITICAL_COUNTRIES + POLITICAL_ISSUES +
    STOCK_MARKETS + ASIAN_COMPANIES + CURRENCIES + ECONOMIC_EVENTS +
    TECH_COMPANIES + GAMING_COMPANIES + GAMES + ESPORTS_TEAMS + ESPORTS_PLAYERS + AI_TECH
)

# Convert to lowercase for case-insensitive matching
ALL_ASIAN_KEYWORDS_LOWER = [kw.lower() for kw in ALL_ASIAN_KEYWORDS]


def is_asian_relevant(market):
    """
    Check if a market is relevant to Asian audience

    Args:
        market: Dictionary containing market information

    Returns:
        Boolean indicating Asian relevance
    """
    # Combine all searchable text
    question = market.get('question', '').lower()
    description = market.get('description', '').lower()
    tags = ' '.join(market.get('tags', [])).lower()

    search_text = f"{question} {description} {tags}"

    # Check for keyword matches
    for keyword in ALL_ASIAN_KEYWORDS_LOWER:
        if keyword in search_text:
            return True

    return False


def get_matching_keywords(market):
    """
    Get list of Asian keywords that match this market

    Args:
        market: Dictionary containing market information

    Returns:
        List of matching keywords
    """
    question = market.get('question', '').lower()
    description = market.get('description', '').lower()
    tags = ' '.join(market.get('tags', [])).lower()

    search_text = f"{question} {description} {tags}"

    matching = []
    for i, keyword in enumerate(ALL_ASIAN_KEYWORDS_LOWER):
        if keyword in search_text:
            matching.append(ALL_ASIAN_KEYWORDS[i])  # Return original case

    return matching


# Print keyword count for verification
if __name__ == "__main__":
    print(f"Total Asian keywords: {len(ALL_ASIAN_KEYWORDS)}")
    print(f"\nBreakdown:")
    print(f"  Sports: {len(SPORTS_COUNTRIES + SPORTS_TYPES + SPORTS_LEAGUES + SPORTS_TEAMS + SPORTS_PLAYERS)}")
    print(f"  Entertainment: {len(KPOP_GROUPS + KPOP_SOLOISTS + ASIAN_ACTORS + ENTERTAINMENT_CONTENT + ENTERTAINMENT_AWARDS + ENTERTAINMENT_PLATFORMS)}")
    print(f"  Politics: {len(POLITICAL_LEADERS + POLITICAL_PARTIES + POLITICAL_COUNTRIES + POLITICAL_ISSUES)}")
    print(f"  Economics: {len(STOCK_MARKETS + ASIAN_COMPANIES + CURRENCIES + ECONOMIC_EVENTS)}")
    print(f"  Technology/Gaming: {len(TECH_COMPANIES + GAMING_COMPANIES + GAMES + ESPORTS_TEAMS + ESPORTS_PLAYERS + AI_TECH)}")
