import re

def extract_dates(info_text):
    # Regular expression to match the two dates
    version_pattern = r"Version au (\d{1,2} \w+ \d{4})"
    vigueur_pattern = r"En vigueur depuis le (\d{1,2} \w+ \d{4})"
    
    # Match the dates using regex
    version_match = re.search(version_pattern, info_text)
    vigueur_match = re.search(vigueur_pattern, info_text)
    
    if version_match and vigueur_match:
        # Convert the dates to "DD/MM/YYYY" format
        version_date = convert_date(version_match.group(1))
        vigueur_date = convert_date(vigueur_match.group(1))
        
        return {
            "version": version_date,
            "vigueur": vigueur_date
        }
    else:
        return None

def convert_date(date_str):
    # Mapping for French month names to numbers
    month_map = {
        "janvier": "01", "février": "02", "mars": "03", "avril": "04", "mai": "05", "juin": "06",
        "juillet": "07", "août": "08", "septembre": "09", "octobre": "10", "novembre": "11", "décembre": "12"
    }
    
    # Split the date string into day, month, year
    day, month, year = date_str.split()
    
    # Convert to the desired format: DD/MM/YYYY
    month_number = month_map.get(month.lower())
    if month_number:
        return f"{day}/{month_number}/{year}"
    else:
        return None