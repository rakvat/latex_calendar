#!/usr/bin/python3

import sys
import glob
import calendar
from calendar import monthrange
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
                        \\usepackage[german,ngerman]{babel}
                        \\parindent 0mm
                        \\hoffset -3.3cm
                        \\textwidth 20cm
                        \\pagestyle{empty}

                        \\begin{document}"""
    END_CALENDAR = "end{document}"
    YEAR = "\\textbf{{\\huge{{Calendar for the Year {0}}}}}\\\\\\\\";

    MONTH_TITLE = "\\textbf{{\\large{{{0}}}}}\\\\\\\\";

    MONTH_START = """\\begin{tabular*}{20cm}{|l|l|l|p{5cm}|l| }
                     \\hline
                     \\textbf{} & \\textbf{} & \\textbf{} & \\textbf{...}\\\\
                     \\hline
                     \\hline"""

    MONTH_END = """\\end{tabular*}
                   \\newpage"""

    ROW = "{0} & {1} & \\textbf{{{2}}} & \\tiny{{{3}}} & \\\\ \\hline"
    WEEKEND = "\\hline"

    def format_year(self, the_year):
        print(self.yeardayscalendar(the_year))
        out = self.START_CALENDAR
        for month in range(1, 12 + 1):
            out += self.MONTH_TITLE
            out += self.MONTH_START
            out += self.MONTH_END
        out += self.END_CALENDAR

        print(out)





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
    c.format_year(year)



if __name__ == '__main__':
    main()
