import requests
import json
import sqlite3 as sql
import tkinter as tk
import os
from dotenv import load_dotenv
import tkinter as tk



load_dotenv()
api_key = os.getenv("tibla_api")


if not api_key:
    raise ValueError("API key not found! Check your .env file.")
else:
    print("API key loaded successfully!")  

def get_weather(city):    
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    
    
    try:
        response = requests.get(weather_url)        
        response.raise_for_status() # This will check what http error if there is any

    except requests.exceptions.RequestException as e:
        print(f"Network or HTTP error: {e}")
        return None 
    
    try:
        weather_data = response.json()   
        if weather_data.get('cod') != 200:
            print("API error:", weather_data.get("message"))
            return None

        weather_dict = {
        'City': weather_data['name'],
        "Temperature": weather_data['main']['temp'],
        "Humidity": weather_data['main']['humidity'],
        "Description": weather_data['weather'][0]['description']
    }

    except ValueError as err:
        print('Failed to decode JSON:', err)

    return weather_dict
        # The function will return the results once our api is successful.

    


# weather_database will store the values in a database and take the results from the website as an argument
def weather_database(weather_dict):
    if not weather_dict:
        return
    
    conn = sql.connect('weather.db')
    cursor = conn.cursor()

    
    try:
        cursor.execute("""CREATE TABLE IF NOT EXISTS weather(
                city TEXT PRIMARY KEY,
                temperature REAL,
                humidity REAL,
                description TEXT
                )
                """)

       
        
        cursor.execute("SELECT 1 FROM weather WHERE city = ?",
                       (weather_dict['City'],)            
        )

        if cursor.fetchone():
            print("City exists in the database")
            return
        
        cursor.execute("""INSERT INTO weather
                    (city, temperature, humidity, description)
                    VALUES (?,?,?,?)""",
                    (weather_dict['City'], weather_dict['Temperature'], weather_dict['Humidity'], weather_dict['Description']))
        
        conn.commit()
        
        print("Weather added successfully to the database.")



    except sql.Error as err:
        print(f"Failed to store data in the database: {err}")
    except Exception as err:
        print(f"An error occured: {err}")

    finally:
        conn.close()
    





def display_weather():
    conn = sql.connect('weather.db')
    cursor = conn.cursor()

    
    view_data = cursor.execute("SELECT * FROM weather")
    rows = view_data.fetchall()
    
    conn.close()

    root = tk.Tk()
    root.title("Weather Data")
    root.geometry('600x500')


    canvas = tk.Canvas(root)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)


    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))

    )

    canvas.create_window((0,0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    
    headers = ["City", "Temperature (°C)", "Humidity (%)", "Description"]
    for col, text in enumerate(headers):
        label1 = tk.Label(scroll_frame, text=text, font=("Arial", 12, "bold"), borderwidth=1, relief="solid", width=15)
        label1.grid(row=0, column=col)

    
    for row_index, row_data in enumerate(rows, start=1):
        for col_index, value in enumerate(row_data):
            label2 = tk.Label(scroll_frame, text=str(value), font=("Arial", 12), borderwidth=1, relief="solid", width=15)
            label2.grid(row=row_index, column=col_index)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    root.mainloop()



# Main function
def main():
    while True:
        print("1. Search a City Name")
        print("2. Display Weather GUI")
        print("0. Exit")
        question = input("Please enter a number: ")

        if question == '0':
            print("You are now exiting.")
            break
        
        if question == '1':
            try:
                city = input('please enter a city: ').strip().lower() # Preventing blank spaces

                if city:
                    api_result = get_weather(city)
                    print(api_result)
                    if api_result is None:
                        print("Failed to retrive results.")
                    else:
                        try:
                            weather_database(api_result)
                        except Exception as err:
                            print("Error:", err)
                else:
                    print('Invalid City name. Enter a valid City name.')

            except Exception as err:
                print("An error has occured. Ensure all inputs are valid:", err)

        elif question == '2':
            display_weather()

        else:
            print("Invalid input. Enter 1 or 0.")


if __name__ == "__main__":
    main()