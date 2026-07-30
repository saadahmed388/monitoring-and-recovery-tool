# ---------------- config/db_configs.py ----------------
ENVIRONMENTS_DSN = {
                        "Okayama": "SIEBFDPO", 
                        "Aomori": "SIEBFDPA", 
                        "Hakodate": "SIEBFDPH", 
                        "Iwate": "SIEBFDPI", 
                        "Shikoku": "SIEBFDPS", 
                        "Okinawa": "SIEBFDPN", 
                        "Wakayama": "SIEBFDPW", 
                        "Chugoku": "SIEBFDPC",
                        "UAT1": "SIEBQA",
                        "UAT2": "SIEBQA2",
                        "UAT3": "SIEBQA3"
                    }
DB_CONFIGS = {
    "Okayama": {"user": "READUSER", "password": "READUSER", "dsn": "SIEBFDPO"},
    "Aomori": {"user": "READUSER", "password": "READUSER", "dsn": "SIEBFDPA"},
    "Hakodate": {"user": "READUSER", "password": "READUSER", "dsn": "SIEBFDPH"},
    "Iwate": {"user": "READUSER", "password": "READUSER", "dsn": "SIEBFDPI"},
    "Shikoku": {"user": "READUSER", "password": "READUSER", "dsn": "SIEBFDPS"},
    "Okinawa": {"user": "READUSER", "password": "READUSER", "dsn": "SIEBFDPN"},
    "Wakayama": {"user": "READUSER", "password": "READUSER", "dsn": "SIEBFDPW"},
    "Chugoku": {"user": "READUSER", "password": "READUSER", "dsn": "SIEBFDPC"}
}