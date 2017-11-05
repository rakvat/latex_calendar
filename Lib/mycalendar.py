import calendar
import glob
from calendar import monthrange
from datetime import date
from xml.dom import minidom

class LatexCalendarData:
    EVENT_TYPES = [
            "birthday",
            "fixed_day_event",
            "nth_weekday_in_month_event",
            "last_week_in_month_event"
            ]
    chosen_categories = []
    year_map = {}

    def get_data(self, node, key):
        sub_node = node.getElementsByTagName(key)
        if len(sub_node) > 0 and len(sub_node[0].childNodes) > 0:
            return sub_node[0].childNodes[0].data
        else:
            return ""

    def init_year_map(self, year):
       for month in range(1, 12 + 1):
           month_map = {}
           mr = monthrange(year, month)
           for day in range(1, mr[1] + 1):
               month_map[day] = []
           self.year_map[month] = month_map

    def get_all_categories(self, events):
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


    def handle_event(self, year, event, event_type):
        label = self.get_data(event, "label")
        category = self.get_data(event, "category")
        month = int(self.get_data(event, "month"))
        if not category in chosen_categories:
            return
        if event_type == "birthday":
            day = int(self.get_data(event, "day"))
            entry_year = self.get_data(event, "year")
            if entry_year:
                label = label + " (" + str(year - int(entry_year)) + ")"
        elif event_type == "fixed_day_event":
            day = int(self.get_data(event, "day"))
        elif event_type == "nth_weekday_in_month_event":
            n = int(self.get_data(event, "n"))
            weekday = int(self.get_data(event, "weekday"))
            day = calendar.Calendar(weekday).monthdayscalendar(year, month)[n][0]
        elif event_type == "last_week_in_month_event":
            weekday = int(self.get_data(event, "weekday"))
            day = calendar.Calendar(weekday).monthdayscalendar(year, month)[-1][0]
        self.year_map[month][day].append(label)


    def parse_xml(self, folder, year):
        for file in glob.glob(folder + "/*.xml"):
            print("importing", file)
            xmldoc = minidom.parse(file)
            events = xmldoc.getElementsByTagName("calendar_entries")[0]
            self.get_all_categories(events)
            for event_type in self.EVENT_TYPES:
                events_of_type = events.getElementsByTagName(event_type)
                for event in events_of_type:
                    self.handle_event(year, event, event_type)

class LatexCalendar(calendar.Calendar):
    """
    This calendar returns complete latex formatted pages that can be turned to
    PDF. It also allows to include data.
    """

    input_data = None

    START_CALENDAR = """\\documentclass[8pt, a4paper]{article}
                        \\usepackage[utf8]{inputenc}
                        \\parindent 0mm
                        \\hoffset -3.3cm
                        \\textwidth 20cm
                        \\pagestyle{empty}

                        \\begin{document}"""
    END_CALENDAR = "\\end{document}"
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

    def process_input_data(self, folder, year):
        self.input_data = LatexCalendarData()
        self.input_data.init_year_map(year)
        self.input_data.parse_xml(folder, year)

    def format_year(self, year):
        our_calendar = self.yeardayscalendar(year, 1)
        out = self.START_CALENDAR
        out += self.YEAR % year
        for month_index, month in enumerate(our_calendar):
            out += self.MONTH_TITLE % calendar.month_name[month_index + 1]
            out += self.MONTH_START
            for week_index, week in enumerate(month[0]):
                for weekday, day in enumerate(week):
                    if day == 0:
                        continue
                    if self.input_data:
                        entries = ", ".join(self.input_data.year_map[month_index + 1][day])
                    else:
                        entries = ""
                    weekday_str = calendar.day_abbr[weekday]
                    week_number = date(year, month_index + 1, day).isocalendar()[1]
                    out += self.ROW % (week_number, weekday_str, day, entries)
                    if weekday == 6:
                        out += self.WEEK_END
            out += self.MONTH_END
        out += self.END_CALENDAR

        return out

