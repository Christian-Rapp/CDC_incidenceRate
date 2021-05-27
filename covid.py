from countryinfo import CountryInfo

import csv
import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np


class Country:
    def __init__(self):
        self.iso_code = None
        self.continent = None
        self.location = None
        self.population = 0
        self.case_data = []
        self.death_data = []
        self.incidence_data = []
    
    def set(self, csv_row):
        self.iso_code = csv_row['iso_code']
        self.continent = csv_row['continent']
        self.location = csv_row['location']

    def __str__(self) -> str:
        return self.iso_code + " " + self.location

class case_day:
    def __init__(self):
        self.date = None
        self.total_cases = 0
        self.new_cases = 0
    
    def set(self, csv_row):
        self.date = csv_row['date']
        self.total_cases = int(csv_row['total_cases'].split(".")[0])
        if(csv_row['new_cases']):
            self.new_cases = int(csv_row['new_cases'].split(".")[0])

    def __str__(self) -> str:
        return self.date + " " + self.new_cases + " = " + self.total_cases

    def __repr__(self) -> str:
        return self.date + " " + self.new_cases + " = " + self.total_cases

class incidence_day:
    def __init__(self):
        self.date = None
        self.incidence = 0
    
    def __repr__(self) -> str:
        return self.date + " " + str(self.incidence)
    
    def __str__(self) -> str:
        return self.date + " " + str(self.incidence)


def getData(country, startDate=None, endDate=None, allData=True):
    """
    Reads the Our World in Data file for a specific country and get's some of the relevant information
    """
    with open('owid-covid-data.csv', newline='') as csvfile:
        found = 0
        countryStruct = Country()
        covidreader = csv.DictReader(csvfile)
        for row in covidreader:
            if row['location'] == country or row['iso_code'] == country:
                case_data = case_day()
                case_data.set(row)

                if not found:
                    countryStruct.set(row)
                    found = 1
                    
                if allData:
                    countryStruct.case_data.append(case_data)
                else:
                    if startDate <= row['date'] <= endDate:
                        countryStruct.case_data.append(case_data)
        return countryStruct

def calculate_incidence(country: Country):
    """
    Calculates the CDC 28 Day incidence rate for a country
    """
    sliding_window_start = 0
    sliding_window_end = 27
    relevant_cases = 0
    sliding_window_total = [0 for i in range(0,len(country.case_data))]
    incidence_list = [incidence_day() for i in range(0,len(country.case_data))]

    for i in range(0, 28): # Calculate first 28 days cumulative total
        relevant_cases += country.case_data[i].new_cases

    for i in range(27, len(country.case_data)-1): # Calculate Number of Relevant Cases
        relevant_cases -= country.case_data[sliding_window_start].new_cases
        sliding_window_start += 1
        sliding_window_end += 1
        relevant_cases += country.case_data[sliding_window_end].new_cases
        sliding_window_total[i+1] = relevant_cases

    for i in range(0, len(country.case_data)): # Calculate Incidence
        incidence_list[i].incidence = (sliding_window_total[i]/country.population)*100000
        incidence_list[i].date = country.case_data[i].date
    

    return incidence_list

def graph_incidence(country: Country): 
    """
    Graphs the CDC 28 Day incidence rate for a country 
    """

    x = []
    y = []
    for data in country.incidence_data:
        x.append(data.date)
        y.append(data.incidence)

    # print(x)
    fig, ax = plt.subplots()
    ax.plot_date(x, y, fmt='o', tz=None, xdate=True, data=None)

    ax.plot_date(["2020-02-25","2021-05-25"], [100, 100], color='red', linestyle='-', linewidth=2) # 100 Cases per 100,000. Above this line is Level 4 
    ax.plot_date(["2020-02-25","2021-05-25"], [50, 50], color='orange', linestyle='-', linewidth=2) # 50 Cases per 100,000 Above this line is level 3
    ax.plot_date(["2020-02-25","2021-05-25"], [5, 5], color='yellow', linestyle='-', linewidth=2) # 5 Cases per 100,000 Above this line is level 2

    ax.set(xlabel='Date', ylabel='Incidence Rate', title='28-Day Incidence Rate per 100,000 for '+country.location)

    fmt_half_year = mdates.MonthLocator(interval=3)
    ax.xaxis.set_major_locator(fmt_half_year)
    plt.yticks(np.arange(min(y), max(y), 100))
    ax.grid(True)
    plt.show()



def findCountry(country_name):
    country = getData(country_name, True)
    country.population = CountryInfo(country_name).population()
    
    country.incidence_data = calculate_incidence(country)

    print(country_name)
    print("Population", country.population)
    print("Most recent incidence rate", country.incidence_data[-1])

    graph_incidence(country)
    

if __name__ == "__main__":
    findCountry(sys.argv[1])