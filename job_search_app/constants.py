"""Shared constants: colours, version, and country list."""

VERSION = "1.0.0"
VERSION_URL = (
    "https://gist.githubusercontent.com/Moyo-x/"
    "7144732583323615545bde54ed69638a/raw/version.json"
)

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
C_BG         = "#F4F6F9"
C_HEADER     = "#1A2B4A"
C_ACCENT     = "#2E6FD8"
C_ACCENT_DK  = "#1E5BBF"
C_SUCCESS    = "#27AE60"
C_WARN       = "#E67E22"
C_TEXT       = "#2C3E50"
C_MUTED      = "#7F8C8D"
C_WHITE      = "#FFFFFF"
C_BORDER     = "#DCE1E7"
C_ROW_ALT    = "#F8FAFC"
C_ROW_VISA   = "#EAF7F0"
C_ROW_MAYBE  = "#FEF9EE"

# Status row colours
C_ROW_APPLIED     = "#E8F5E9"
C_ROW_INTERESTED  = "#E3F2FD"
C_ROW_REJECTED    = "#FFEBEE"

# ---------------------------------------------------------------------------
# Country list (~80 job-market countries, alphabetically sorted)
# ---------------------------------------------------------------------------
COUNTRIES: list[str] = sorted([
    # Americas
    "Argentina", "Brazil", "Canada", "Chile", "Colombia", "Mexico",
    "Peru", "United States",
    # Europe
    "Austria", "Belgium", "Croatia", "Czech Republic", "Denmark",
    "Finland", "France", "Germany", "Greece", "Hungary", "Ireland",
    "Italy", "Netherlands", "Norway", "Poland", "Portugal", "Romania",
    "Serbia", "Spain", "Sweden", "Switzerland", "Turkey", "Ukraine",
    "United Kingdom",
    # Middle East
    "Bahrain", "Israel", "Kuwait", "Qatar", "Saudi Arabia", "UAE",
    # Africa
    "Egypt", "Ghana", "Kenya", "Morocco", "Nigeria", "South Africa",
    # Asia Pacific
    "Australia", "Bangladesh", "China", "Hong Kong", "India",
    "Indonesia", "Japan", "Malaysia", "New Zealand", "Pakistan",
    "Philippines", "Singapore", "South Korea", "Sri Lanka", "Taiwan",
    "Thailand", "Vietnam",
])
