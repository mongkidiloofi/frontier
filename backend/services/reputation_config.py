# in frontier/backend/services/reputation_config.py

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
    "EMNLP": {"emnlp", "empiricaal methods in natural language processing"},
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
}

ALL_VENUE_VARIATIONS = {variation for variations in TOP_TIER_VENUES.values() for variation in variations}