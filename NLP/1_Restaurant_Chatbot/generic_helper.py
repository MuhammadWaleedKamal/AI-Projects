import re

def extract_session_id(session_str: str):
    match_session = re.search("sessions/(.*?)/contexts/", session_str)
    
    if match_session:
        return match_session.group(1)
    
    return ""

def get_str_from_food_dict(food_item: dict):
    return ', '.join(f"{int(value)} {key}" for key, value in food_item.items())

if __name__ == "__main__":
    print(get_str_from_food_dict({"samoosa": 2, "roll": 5}))
    # print(extract_session_id("projects/mira-chatbot-for-food-del-fpri/agent/sessions/a31b2666-702c-b491-8202-5ef305fb3f6b/contexts/ongoing-order"))