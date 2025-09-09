import requests
import json
from datetime import datetime
import os

class WeatherApp:
    def __init__(self):
        # Get a free API key here: https://openweathermap.org/api
        self.api_key = "YOUR_API_KEY_HERE"  # Put your API key here
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
        self.favorites_file = "favorite_cities.json"
        self.favorites = self.load_favorites()
    
    def load_favorites(self):
        """Load favorite cities"""
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_favorites(self):
        """Save favorite cities"""
        try:
            with open(self.favorites_file, 'w', encoding='utf-8') as f:
                json.dump(self.favorites, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Failed to save favorites: {e}")
    
    def get_weather_icon(self, weather_code):
        """Return an emoji based on the weather code"""
        weather_icons = {
            "01d": "☀️", "01n": "🌙",  # clear sky
            "02d": "⛅", "02n": "☁️",  # few clouds
            "03d": "☁️", "03n": "☁️",  # scattered clouds
            "04d": "☁️", "04n": "☁️",  # broken clouds
            "09d": "🌧️", "09n": "🌧️",  # shower rain
            "10d": "🌦️", "10n": "🌧️",  # rain
            "11d": "⛈️", "11n": "⛈️",  # thunderstorm
            "13d": "❄️", "13n": "❄️",  # snow
            "50d": "🌫️", "50n": "🌫️"   # mist
        }
        return weather_icons.get(weather_code, "🌡️")
    
    def get_current_weather(self, city):
        """Get the current weather for a city"""
        try:
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric",
                "lang": "en"  # Changed to English
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            return {"error": f"API error: {e}"}
        except Exception as e:
            return {"error": f"Unexpected error: {e}"}
    
    def get_forecast(self, city, days=5):
        """Get a 5-day weather forecast"""
        try:
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric",
                "lang": "en"  # Changed to English
            }
            
            response = requests.get(self.forecast_url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            return {"error": f"API error: {e}"}
        except Exception as e:
            return {"error": f"Unexpected error: {e}"}
    
    def display_current_weather(self, weather_data):
        """Display the current weather data"""
        if "error" in weather_data:
            print(f"❌ {weather_data['error']}")
            return
        
        if weather_data.get("cod") != 200:
            print(f"❌ City not found: {weather_data.get('message', 'Unknown error')}")
            return
        
        # Parse the data
        city = weather_data["name"]
        country = weather_data["sys"]["country"]
        temp = weather_data["main"]["temp"]
        feels_like = weather_data["main"]["feels_like"]
        humidity = weather_data["main"]["humidity"]
        pressure = weather_data["main"]["pressure"]
        description = weather_data["weather"][0]["description"].title()
        icon_code = weather_data["weather"][0]["icon"]
        wind_speed = weather_data["wind"]["speed"]
        
        # Sunrise/sunset times
        sunrise = datetime.fromtimestamp(weather_data["sys"]["sunrise"]).strftime("%H:%M")
        sunset = datetime.fromtimestamp(weather_data["sys"]["sunset"]).strftime("%H:%M")
        
        # Visibility (km)
        visibility = weather_data.get("visibility", 0) / 1000
        
        # Emoji
        icon = self.get_weather_icon(icon_code)
        
        print("\n" + "="*60)
        print(f"🌍 {city}, {country} - CURRENT WEATHER")
        print("="*60)
        print(f"🌡️  Temperature: {temp:.1f}°C (Feels like: {feels_like:.1f}°C)")
        print(f"{icon} Condition: {description}")
        print(f"💧 Humidity: %{humidity}")
        print(f"🌪️  Wind: {wind_speed:.1f} m/s")
        print(f"📊 Pressure: {pressure} hPa")
        print(f"👀 Visibility: {visibility:.1f} km")
        print(f"🌅 Sunrise: {sunrise}")
        print(f"🌇 Sunset: {sunset}")
        print(f"📅 Last Updated: {datetime.now().strftime('%H:%M:%S')}")
        print("="*60)
    
    def display_forecast(self, forecast_data):
        """Display the 5-day forecast"""
        if "error" in forecast_data:
            print(f"❌ {forecast_data['error']}")
            return
        
        if forecast_data.get("cod") != "200":
            print(f"❌ Forecast could not be retrieved: {forecast_data.get('message', 'Unknown error')}")
            return
        
        city = forecast_data["city"]["name"]
        country = forecast_data["city"]["country"]
        
        print("\n" + "="*70)
        print(f"📅 {city}, {country} - 5-DAY WEATHER FORECAST")
        print("="*70)
        
        # Group data by day
        daily_forecasts = {}
        
        for item in forecast_data["list"][:40]:  # 5 days * 8 entries (every 3 hours)
            date_str = item["dt_txt"].split()[0]  # Get only the date
            if date_str not in daily_forecasts:
                daily_forecasts[date_str] = []
            daily_forecasts[date_str].append(item)
        
        for date_str, forecasts in list(daily_forecasts.items())[:5]:
            # Min/max temperature for the day
            temps = [f["main"]["temp"] for f in forecasts]
            min_temp = min(temps)
            max_temp = max(temps)
            
            # Most common weather condition
            descriptions = [f["weather"][0]["description"] for f in forecasts]
            most_common_desc = max(set(descriptions), key=descriptions.count).title()
            
            # Icon
            icons = [f["weather"][0]["icon"] for f in forecasts]
            most_common_icon = max(set(icons), key=icons.count)
            emoji = self.get_weather_icon(most_common_icon)
            
            # Average humidity
            avg_humidity = sum(f["main"]["humidity"] for f in forecasts) / len(forecasts)
            
            # Date format
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d/%m/%Y - %A")
            
            print(f"\n📅 {formatted_date}")
            print(f"{emoji} {most_common_desc}")
            print(f"🌡️  Min: {min_temp:.1f}°C | Max: {max_temp:.1f}°C")
            print(f"💧 Average Humidity: %{avg_humidity:.0f}")
            print("-" * 50)
    
    def add_to_favorites(self, city):
        """Add a city to favorites"""
        city = city.strip().title()
        if city not in self.favorites:
            self.favorites.append(city)
            self.save_favorites()
            print(f"✅ '{city}' added to favorites.")
        else:
            print(f"⚠️ '{city}' is already in your favorites.")
    
    def remove_from_favorites(self, city):
        """Remove a city from favorites"""
        city = city.strip().title()
        if city in self.favorites:
            self.favorites.remove(city)
            self.save_favorites()
            print(f"✅ '{city}' removed from favorites.")
        else:
            print(f"⚠️ '{city}' is not in your favorites.")
    
    def view_favorites(self):
        """View the list of favorite cities"""
        if not self.favorites:
            print("⭐ Your favorites list is empty.")
            return
        
        print("\n" + "="*40)
        print("⭐ YOUR FAVORITE CITIES")
        print("="*40)
        for i, city in enumerate(self.favorites, 1):
            print(f"{i}. {city}")
        print("="*40)
    
    def run(self):
        """Main application loop"""
        print("✨ Welcome to the Weather App! ✨")
        while True:
            print("\n" + "="*40)
            print("📋 MAIN MENU")
            print("="*40)
            print("1. Get Current Weather")
            print("2. Get 5-Day Forecast")
            print("3. Add to Favorites")
            print("4. Remove from Favorites")
            print("5. View Favorites")
            print("6. Exit")
            print("="*40)
            
            choice = input("👉 Enter your choice (1-6): ").strip()
            
            if choice == "1":
                city_name = input("Enter a city name: ").strip().title()
                if city_name:
                    weather_data = self.get_current_weather(city_name)
                    self.display_current_weather(weather_data)
            
            elif choice == "2":
                city_name = input("Enter a city name: ").strip().title()
                if city_name:
                    forecast_data = self.get_forecast(city_name)
                    self.display_forecast(forecast_data)
            
            elif choice == "3":
                city_name = input("Enter a city to add to favorites: ").strip().title()
                if city_name:
                    self.add_to_favorites(city_name)
            
            elif choice == "4":
                self.view_favorites()
                city_name = input("Enter the city to remove from favorites: ").strip().title()
                if city_name:
                    self.remove_from_favorites(city_name)
            
            elif choice == "5":
                self.view_favorites()
                if self.favorites:
                    fav_choice = input("Enter a number to get its weather, or 'B' to go back: ").strip().upper()
                    if fav_choice.isdigit():
                        index = int(fav_choice) - 1
                        if 0 <= index < len(self.favorites):
                            city_name = self.favorites[index]
                            weather_data = self.get_current_weather(city_name)
                            self.display_current_weather(weather_data)
                        else:
                            print("❌ Invalid number.")
                    elif fav_choice != "B":
                        print("❌ Invalid choice. Please enter a number or 'B'.")
            
            elif choice == "6":
                print("👋 Thank you for using the Weather App. Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter a number from 1 to 6.")

if __name__ == "__main__":
    app = WeatherApp()
    app.run()