import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkcalendar import DateEntry  # 需要安装 tkcalendar 库
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import requests
import datetime
import os
import time
from calendar import monthrange


# Function to calculate the number of weeks a month spans, given a year and month,
def count_spanned_weeks(year, month):
    days_in_month = monthrange(year, month)[1] # Get total number of days in the month
    first_day_of_month_weekday = monthrange(year, month)[0] # Get the weekday of the first day of the month
    complete_weeks = days_in_month // 7 # Calculate the number of complete weeks
    extra_days = days_in_month % 7 # Check if there are extra days that spill over into a partial week
    spanned_weeks = complete_weeks # Start counting weeks with complete weeks
    # Check if extra days cause the month to span into an additional week
    if extra_days > 0:
        if (first_day_of_month_weekday + extra_days) > 6: # If the first day of the month + extra days spills over the week boundary, add another week
            spanned_weeks += 2  # one for the partial start week, one for the partial end week
        else:
            spanned_weeks += 1  # only the partial end week
    return spanned_weeks


def get_previous_month(month_name): # month_name: str
    month_number = datetime.datetime.strptime(month_name, '%B').month
    previous_month_number = (month_number - 2) % 12 + 1
    return previous_month_number # return: int


def select_date(driver, target_date, target_month, target_year): # 沒辦法找三月
    wait = WebDriverWait(driver, 10)
    date_picker = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "date-picker-wrapper")))

    # Check 右半邊 'month2'
    month_element = date_picker.find_elements(By.CLASS_NAME, "month-name")[1] # 右半邊
    month_name = month_element.find_elements(By.CLASS_NAME, "month-element")[0].text.lower()
    year = month_element.find_elements(By.CLASS_NAME, "month-element")[1].text
    if target_month.lower() == month_name and target_year == year:
        days = date_picker.find_elements(By.CLASS_NAME, "day")
        prev_spanned_weeks = count_spanned_weeks(int(year), get_previous_month(month_name))
        for day in days[7*prev_spanned_weeks:]:
            if day.text.zfill(2) == target_date.zfill(2):
                day.click()
                return  
        
    # Check 左半邊 'month1'
    month_element = date_picker.find_elements(By.CLASS_NAME, "month-name")[0] # 左半邊
    month_name = month_element.find_elements(By.CLASS_NAME, "month-element")[0].text.lower()
    year = month_element.find_elements(By.CLASS_NAME, "month-element")[1].text
    while target_month.lower() != month_name or target_year != year:
        next_button = date_picker.find_element(By.CLASS_NAME, "prev")
        next_button.click()
        month_element = date_picker.find_elements(By.CLASS_NAME, "month-name")[0] # 左半邊
        month_name = month_element.find_elements(By.CLASS_NAME, "month-element")[0].text.lower()
        year = month_element.find_elements(By.CLASS_NAME, "month-element")[1].text
    days = date_picker.find_elements(By.CLASS_NAME, "day")
    for day in days:
        if day.text.zfill(2) == target_date.zfill(2):
            day.click()
            break


def download_data():
    # Get input time
    start_date = str(start_date_entry.get_date().strftime("%d"))
    start_month = start_date_entry.get_date().strftime("%B").lower()
    start_year = str(start_date_entry.get_date().strftime("%Y"))
    end_date = str(end_date_entry.get_date().strftime("%d"))
    end_month = end_date_entry.get_date().strftime("%B").lower()
    end_year = str(end_date_entry.get_date().strftime("%Y"))

    # Check if the date is valid
    if start_date_entry.get_date() > end_date_entry.get_date(): # Validate start date is less than or equal to end date
        result_label.config(text="Start date should be less than or equal to end date", fg="red")
        return
    yesterday = datetime.datetime.now().date() - datetime.timedelta(days=1)
    if end_date_entry.get_date() > yesterday: # Validate end date is yesterday or earlier
        result_label.config(text="End date should be yesterday or earlier", fg="red")
        return
    
    result_label.config(text=f"Downloading data from {start_date_entry.get_date()} to {end_date_entry.get_date()}...", fg="green")
    window.update()  # 强制界面更新
    
    # Open website
    url = input("Input the URL: ")

    # Allow driver to download data
    download_directory = file_location_var.get().replace("/", "\\")  # 将正斜杠替换为反斜杠
    print(download_directory)
    chrome_options = Options()
    chrome_options.add_experimental_option('prefs', {
        "download.default_directory": download_directory
    })
    driver = webdriver.Chrome(options=chrome_options) # executable_path=driver_path, 
    driver.get(url)

    # Select dataset
    dataset_dropdown = driver.find_element(By.CSS_SELECTOR, '#dropdown')
    dataset_dropdown.send_keys("Prof.Hsieh's Solar Panel")

    # Select dates: 先選 end 再按 prev 選 start
    select_date(driver, end_date, end_month, end_year)
    select_date(driver, start_date, start_month, start_year)

    # Click submit button and wait for the file to download
    submit_button = driver.find_element(By.NAME, 'export')
    submit_button.click()
    time.sleep(5)

    # Quit the driver
    driver.quit()

    result_label.config(text="Data downloaded successfully", fg="green")


def select_file_location():
    file_location = filedialog.askdirectory()
    file_location_var.set(file_location)


# Calculate default download directory
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
default_download_dir = os.path.join(root_dir, "data", "ntu_pv")
if not os.path.exists(default_download_dir):
    os.makedirs(default_download_dir)


window = tk.Tk()
window.title("Data Downloader")

# Start date input
start_date_label = tk.Label(window, text="Start Date:")
start_date_label.grid(row=0, column=0, padx=10, pady=5)
start_date_entry = DateEntry(window, date_pattern="yyyy/mm/dd")
start_date_entry.grid(row=0, column=1, padx=10, pady=5)

# End date input
end_date_label = tk.Label(window, text="End Date:")
end_date_label.grid(row=1, column=0, padx=10, pady=5)
end_date_entry = DateEntry(window, date_pattern="yyyy/mm/dd")
end_date_entry.grid(row=1, column=1, padx=10, pady=5)

# File location selection
file_location_label = tk.Label(window, text="File Location:")
file_location_label.grid(row=2, column=0, padx=10, pady=5)
file_location_var = tk.StringVar(window)
file_location_var.set(default_download_dir)
file_location_entry = tk.Entry(window, textvariable=file_location_var, state='readonly')
file_location_entry.grid(row=2, column=1, padx=10, pady=5)
file_location_button = tk.Button(window, text="Select", command=select_file_location)
file_location_button.grid(row=2, column=2, padx=10, pady=5)

# Download button
download_button = tk.Button(window, text="Download Data", command=download_data)
download_button.grid(row=3, column=0, columnspan=3, padx=10, pady=5)

# Result label
result_label = tk.Label(window, text="", fg="green")
result_label.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

window.mainloop()
