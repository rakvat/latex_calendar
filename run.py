#!/usr/bin/python3

import sys
import calendar
import os

import mycalendar


INPUT_DATA_FOLDER = "input"
OUTPUT_DATA_FOLDER = "output"
BASE_FILENAME = "calendar"


def main():
    print("creating a new calendar")

    if len(sys.argv) != 2:
        print("usage: ./run.py [year]\n  e.g. ./run.py 2042")
        sys.exit(0)

    year = int(sys.argv[1])

    # use Latex calendar
    latex_calendar = mycalendar.LatexCalendar()

    latex_calendar.process_input_data(INPUT_DATA_FOLDER, year)
    output = latex_calendar.format_year(year)

    # create latex, dvi and pdf output
    base_file_name = BASE_FILENAME + "_" + str(year)
    latex_file = open(OUTPUT_DATA_FOLDER + "/" + base_file_name + ".tex", "w")
    latex_file.write(output)
    latex_file.close()
    os.system("cd " + OUTPUT_DATA_FOLDER + " && latex -interaction=nonstopmode " + base_file_name + ".tex")
    os.system("cd " + OUTPUT_DATA_FOLDER + " && dvipdf " + base_file_name + ".dvi")
    os.system("cd " + OUTPUT_DATA_FOLDER + " && evince " + base_file_name + ".pdf")



if __name__ == '__main__':
    main()
