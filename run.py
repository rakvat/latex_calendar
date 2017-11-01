#!/usr/bin/python3

import sys
import glob
import calendar
import os
from calendar import monthrange
from datetime import date
from xml.dom import minidom

import pdb
    # pdb.set_trace()

EVENT_TYPES = [
        "birthday",
        "fixed_day_event",
        "nth_weekday_in_month_event",
        "last_week_in_month_event"
        ]

# global variables
chosen_categories = []
year = 0
year_map = {}

def get_data(node, key):
    sub_node = node.getElementsByTagName(key)
    if len(sub_node) > 0 and len(sub_node[0].childNodes) > 0:
        return sub_node[0].childNodes[0].data
    else:
        return ""

def init_year_map():
   global yearmap
   for month in range(1, 12 + 1):
       month_map = {}
       mr = monthrange(year, month)
       for day in range(1, mr[1] + 1):
           month_map[day] = []
       year_map[month] = month_map

def get_all_categories(events):
    categories = []
    global chosen_categories

    category_nodes = events.getElementsByTagName("category")
    for category_node in category_nodes:
        if len(category_node.childNodes) > 0:
            category = category_node.childNodes[0].data
            if not category in categories:
                categories.append(category)

    # check categories
    print("We found events in these categories:", categories)
    all = input("Should we add them all? (Y/n)")
    if all == "N" or all == "n":
        for category in categories:
            this_one = input("Add category '" + category + "'? (Y/n)")
            if this_one != "N" and this_one != "n":
                chosen_categories.append(category)
    else:
        chosen_categories = categories

    print("These categories will be included:", chosen_categories)


def handle_event(event, event_type):
    global year_map
    label = get_data(event, "label")
    category = get_data(event, "category")
    if not category in chosen_categories:
        return
    if event_type == "birthday":
        day = int(get_data(event, "day"))
        month = int(get_data(event, "month"))
        entry_year = get_data(event, "year")
        if entry_year:
            label = label + " (" + str(year - int(entry_year)) + ")"
        year_map[month][day].append(label)


def parse_xml():
    # parse xml
    for file in glob.glob("input/*.xml"):
        print("importing", file)
        xmldoc = minidom.parse(file)
        events = xmldoc.getElementsByTagName("calendar_entries")[0]
        get_all_categories(events)
        for event_type in EVENT_TYPES:
            events_of_type = events.getElementsByTagName(event_type)
            for event in events_of_type:
                handle_event(event, event_type)

class LatexCalendar(calendar.Calendar):

    """
    This calendar returns complete latex formatted pages that can be turned to
    PDF. It also allows to include data.
    """

    START_CALENDAR = """\\documentclass[8pt, a4paper]{article}
                        \\usepackage[utf8]{inputenc}
                        \\parindent 0mm
                        \\hoffset -3.3cm
                        \\textwidth 20cm
                        \\pagestyle{empty}

                        \\begin{document}"""
    END_CALENDAR = "end{document}"
    YEAR = "\\textbf{{\\huge{{Calendar for the Year %d}}}}\\\\\\\\";

    MONTH_TITLE = "\\textbf{{\\large{{%s}}}}\\\\\\\\";

    MONTH_START = """\\begin{tabular*}{20cm}{|l|l|l|p{5cm}|l| }
                     \\hline
                     \\textbf{} & \\textbf{} & \\textbf{} & \\textbf{...}\\\\
                     \\hline
                     \\hline\n"""

    MONTH_END = """\\end{tabular*}
                   \\newpage\n"""

    ROW = "%d & %s & \\textbf{{%d}} & \\tiny{{%s}} & \\\\ \\hline\n"
    WEEK_END = "\\hline\n"

    def format_year(self, the_year):
        c = self.yeardayscalendar(the_year, 1)
        out = self.START_CALENDAR
        out += self.YEAR % the_year
        for month_index, month in enumerate(c):
            print(month_index)
            print(month)
            out += self.MONTH_TITLE % calendar.month_name[month_index + 1]
            out += self.MONTH_START
            for week_index, week in enumerate(month[0]):
                for weekday, day in enumerate(week):
                    if day == 0:
                        continue
                    entries = ", ".join(year_map[month_index + 1][day])
                    weekday_str = calendar.day_abbr[weekday]
                    week_number = date(the_year, month_index + 1, day).isocalendar()[1]
                    out += self.ROW % (week_number, weekday_str, day, entries)
                    if weekday == 6:
                        out += self.WEEK_END
            out += self.MONTH_END
        out += self.END_CALENDAR

        return out





def main():
    global year

    print("creating a new calendar")

    if len(sys.argv) != 2:
        print("usage: ./run.py [year]\n  e.g. ./run.py 2042")
        sys.exit(0)

    year = int(sys.argv[1])

    init_year_map()
    parse_xml()
    print(year_map)

    # create latex output
    c = LatexCalendar()
    base_file_name = "calendar_" + str(year)
    latex_file = open("output/" + base_file_name + ".tex", "w")
    latex_file.write(c.format_year(year))
    latex_file.close()
    os.system("cd output && latex -interaction=nonstopmode " + base_file_name + ".tex")
    os.system("cd output && dvipdf " + base_file_name + ".dvi")
    os.system("cd output && evince " + base_file_name + ".pdf")



if __name__ == '__main__':
    main()
