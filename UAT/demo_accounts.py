"""Demo accounts grouped by language for Albert Dashboard v2.

This file is read dynamically by the FastAPI backend to populate the
Languages and Demo Accounts dropdowns in the React dashboard.

Each entry is of the form:
    [email, password, region, country, language, account_type]
"""

demo_accounts = {
    # English-language accounts
    'English': [
        ['mhmg_albert_dist1@yopmail.com', 'Login2Bot!', 'EMEA', 'United Kingdom', 'English', 'distri'],
        ['mhmg_albert_dist2@yopmail.com', 'Login2Bot!', 'EMEA', 'United Kingdom', 'English', 'distri'],
        ['mhmg_albert_solp1@yopmail.com', 'Login2Bot!', 'EMEA', 'United Kingdom', 'English', 'T2'],
        ['mhmg_albert_solp2@yopmail.com', 'Login2Bot!', 'EMEA', 'United Kingdom', 'English', 'T2'],
    ],

    # Korean
    'Korean': [
        ['mhmg_albert_dist1@yopmail.com', 'Login2Bot!', 'APJ', 'South Korea', 'Korean', 'distri'],
    ],

    # Simplified Chinese
    'Simplified Chinese': [
        ['mhmg_albert_dist1@yopmail.com', 'Login2Bot!', 'APJ', 'China', 'Simplified Chinese', 'distri'],
        ['mhmg_albert_solp1@yopmail.com', 'Login2Bot!', 'APJ', 'China', 'Simplified Chinese', 'T2'],
    ],

    # Japanese
    'Japanese': [
        ['mhmg_albert_dist1@yopmail.com', 'Login2Bot!', 'APJ', 'Japan', 'Japanese', 'distri'],
        ['mhmg_albert_solp2@yopmail.com', 'Login2Bot!', 'APJ', 'Japan', 'Japanese', 'T2'],
    ],

    # Italian
    'Italian': [
        ['mhmg_albert_dist1@yopmail.com', 'Login2Bot!', 'EMEA', 'Italy', 'Italian', 'distri'],
        ['mhmg_albert_solp1@yopmail.com', 'Login2Bot!', 'EMEA', 'Italy', 'Italian', 'T2'],
    ],

    # Portuguese (Brazil)
    'Portuguese': [
        ['mhmg_albert_dist1@yopmail.com', 'Login2Bot!', 'AMS', 'Brazil', 'Portuguese', 'distri'],
        ['mhmg_albert_solp1@yopmail.com', 'Login2Bot!', 'AMS', 'Brazil', 'Portuguese', 'T2'],
    ],

    # Taiwanese (traditional Chinese / Taiwan)
    'Taiwan': [
        ['mhmg_albert_dist2@yopmail.com', 'Login2Bot!', 'APJ', 'Taiwan', 'Taiwan', 'distri'],
    ],

    # Indonesian
    'Indonesian': [
        ['mhmg_albert_dist2@yopmail.com', 'Login2Bot!', 'APJ', 'Indonesia', 'Indonesian', 'distri'],
        ['mhmg_albert_solp2@yopmail.com', 'Login2Bot!', 'APJ', 'Indonesia', 'Indonesian', 'T2'],
    ],

    # French
    'French': [
        ['mhmg_albert_solp1@yopmail.com', 'Login2Bot!', 'EMEA', 'France', 'French', 'T2'],
    ],

    # German
    'German': [
        ['mhmg_albert_solp1@yopmail.com', 'Login2Bot!', 'EMEA', 'Germany', 'German', 'T2'],
    ],

    # Turkish
    'Turkish': [
        ['mhmg_albert_solp2@yopmail.com', 'Login2Bot!', 'EMEA', 'Turkey', 'Turkish', 'T2'],
    ],

    # Spanish
    'Spanish': [
        ['mhmg_albert_solp2@yopmail.com', 'Login2Bot!', 'EMEA', 'Spain', 'Spanish', 'T2'],
    ],
}
