import logging

# --- ArXiv Fetcher Configuration ---
# On the very first run, how many of the latest papers should be fetched to seed the database.
ARXIV_FETCHER_JOB_NAME = "arxiv_stack_pointer_fetcher"  # New name to avoid conflicts

# Categories to fetch from ArXiv. This list can be customized as needed.
ARXIV_CATEGORIES = [
    "cs.AI", "cs.CL", "cs.CV", "cs.LG", "cs.MA", "cs.RO", "math.OC", "eess.SY", "q-bio.NC", "stat.ML"
]

# --- Pruning Configuration ---
PAPER_SHELF_LIFE_MONTHS = 6

# --- OpenReview Fetcher Configuration ---
# Sets how many papers to fetch per page when syncing a full conference/journal.
OPENREVIEW_API_PAGE_SIZE = 1000

# --- Semantic Scholar & Reputation Configuration ---
# This dictionary defines what constitutes a "top-tier" publication venue.
# The key is the canonical name, and the value is a set of lowercase string
# variations used for matching against the 'venue' field from Semantic Scholar.
TOP_TIER_VENUES = {
    # == General AI & Machine Learning ==
    "NeurIPS": {"neurips", "nips", "neural information processing systems"},
    "ICML": {"icml", "international conference on machine learning"},
    "ICLR": {"iclr", "international conference on learning representations"},
    "AISTATS": {"aistats", "artificial intelligence and statistics"},
    "UAI": {"uai", "conference on uncertainty in artificial intelligence"},
    "COLT": {"colt", "conference on learning theory"},
    "AAAI": {"aaai", "conference on artificial intelligence"},
    "IJCAI": {"ijcai", "international joint conference on artificial intelligence"},
    "RLC": {"rlc", "reinforcement learning conference"},
    "JMLR": {"jmlr", "journal of machine learning research"},
    "TMLR": {"tmlr", "transactions on machine learning research"},

    # == Computer Vision ==
    "CVPR": {"cvpr", "conference on computer vision and pattern recognition"},
    "ICCV": {"iccv", "international conference on computer vision"},
    "ECCV": {"eccv", "european conference on computer vision"},
    "WACV": {"wacv", "winter conference on applications of computer vision"},

    # == Natural Language Processing ==
    "ACL": {"acl", "association for computational linguistics"},
    "EMNLP": {"emnlp", "empirical methods in natural language processing"},
    "NAACL": {"naacl", "north american chapter of the association for computational linguistics"},
    "TACL": {"tacl", "transactions of the association for computational linguistics"},

    # == Robotics ==
    "ICRA": {"icra", "international conference on robotics and automation"},
    "IROS": {"iros", "intelligent robots and systems"},
    "CoRL": {"corl", "conference on robot learning"},
    "RSS": {"rss", "robotics: science and systems"},
    
    # == Human-Computer Interaction ==
    "CHI": {"acm chi", "chi conference on human factors in computing systems"},
    
    # == Information Retrieval & Data Mining ==
    "KDD": {"kdd", "conference on knowledge discovery and data mining"},
    "SIGIR": {"sigir", "conference on research and development in information retrieval"},
    "TheWebConf": {"www", "the web conference"},

    # == Multi-Agent Systems ==
    "AAMAS": {"aamas", "autonomous agents and multiagent systems"},

    # == Sound & Audio Processing ==
    "ICASSP": {"icassp", "acoustics, speech, and signal processing"},

    # == Top-Tier General Science Journals (NEW) ==
    "Nature": {"nature"},
    "PNAS": {"pnas", "proceedings of the national academy of sciences"},
}

# This creates a single, flattened set of all possible venue name variations.
# The Semantic Scholar service will import and use this set for efficient matching.
ALL_VENUE_VARIATIONS = {variation for variations in TOP_TIER_VENUES.values() for variation in variations}

# --- Base Venue Configurations for OpenReview Fetcher ---
BASE_VENUE_CONFIGS = [
    {'name_prefix': 'ICLR.cc', 'display_name': 'ICLR', 'venueid_pattern': '{base}/{year}/Conference', 'start_year': 2024, 'type': 'conference', 'category_logic': 'parse_from_venue_string'},
    {'name_prefix': 'NeurIPS.cc', 'display_name': 'NeurIPS', 'venueid_pattern': '{base}/{year}/Conference', 'start_year': 2024, 'type': 'conference', 'category_logic': 'parse_from_venue_string'},
    {'name_prefix': 'ICML.cc', 'display_name': 'ICML', 'venueid_pattern': 'ICML.cc/{year}/Conference', 'start_year': 2024, 'type': 'conference', 'category_logic': 'parse_from_venue_string'},
    {'name_prefix': 'rl-conference.cc/RLC', 'display_name': 'RLC', 'venueid_pattern': '{base}/{year}/Conference', 'start_year': 2024, 'type': 'conference'},
    {'name_prefix': 'robot-learning.org/CoRL', 'display_name': 'CoRL', 'venueid_pattern': '{base}/{year}/Conference', 'start_year': 2024, 'type': 'conference'},
    {'name_prefix': 'aistats.org/AISTATS', 'display_name': 'AISTATS', 'venueid_pattern': '{base}/{year}/Conference', 'start_year': 2024, 'type': 'conference', 'category_logic': 'parse_from_venue_string'},
    {'name_prefix': 'TMLR', 'display_name': 'TMLR', 'venueid_pattern': 'TMLR', 'type': 'journal', 'category_logic': 'parse_from_direct_field', 'category_field_name': 'certifications', 'sync_strategy': 'incremental_sync'},
    {'name_prefix': 'DMLR', 'display_name': 'DMLR', 'venueid_pattern': 'DMLR', 'type': 'journal', 'category_logic': 'parse_from_direct_field', 'category_field_name': 'certifications', 'sync_strategy': 'incremental_sync'}
]

# --- NEW: Centralized ArXiv Fetcher Internals ---
# These parameters control the behavior of the arxiv_fetcher script.
# Initial number of papers to fetch on the first run or in each exponential search step.
ARXIV_API_PAGE_SIZE = 200
# The absolute maximum number of papers to fetch in a single API call. MUST be <= 2000.
ARXIV_MAX_FETCH_SIZE = 2000
# The maximum number of exponential search attempts to find the high-water mark.
ARXIV_MAX_FETCH_ATTEMPTS = 5
# The maximum number of concurrent calls to the Semantic Scholar API.
ARXIV_MAX_CONCURRENT_SEMANTIC_CALLS = 10

# --- OpenReview Fetcher Configuration ---
OPENREVIEW_API_PAGE_SIZE = 1000
OPENREVIEW_MAX_FETCH_ATTEMPTS = 5  # For exponential search

# --- Service-Wide Configuration ---
# The number of papers to process before committing to the database.
DB_COMMIT_BATCH_SIZE = 20

# --- Logging Configuration ---
LOGGING_CONFIG = {
    "level": logging.INFO,
    "format": "%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
}