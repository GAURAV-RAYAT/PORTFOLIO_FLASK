import requests

def get_visitor_location(ip_address):
    """Fetch location details from IP address"""
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}")
        loc_data = response.json()
        return {
            "city": loc_data.get("city", "Unknown City"),
            "country": loc_data.get("country", "Unknown Country"),
            "isp": loc_data.get("isp", "Unknown ISP")
        }
    except Exception as e:
        print(f"Geolocation Error: {e}")
        return {
            "city": "Unknown",
            "country": "Unknown",
            "isp": "Unknown"
        }


def get_visitor_ip(request_obj):
    """Extract visitor IP from Flask request"""
    if request_obj.headers.getlist("X-Forwarded-For"):
        return request_obj.headers.getlist("X-Forwarded-For")[0]
    return request_obj.remote_addr
