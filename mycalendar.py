import calendar
import glob
import itertools
import yaml
from calendar import monthrange
from datetime import date


class LatexCalendarData:
    EVENT_TYPES = [
            "birthdays",
            "fixed_day_events",
            "nth_weekday_in_month_events",
            "last_week_in_month_events"
            ]
    chosen_categories = []
    year_map = {}

    def get_data(self, node, key):
        return node.get(key, "")

    def init_year_map(self, year):
       for month in range(1, 12 + 1):
           month_map = {}
           mr = monthrange(year, month)
           for day in range(1, mr[1] + 1):
               month_map[day] = []
           self.year_map[month] = month_map

    def get_all_categories(self, events):
        # flatten to get the categories
        all_events = list(itertools.chain.from_iterable(list(events.values())))
        return list(set([e["category"] for e in all_events]))

    def handle_event(self, year, event, event_type):
        label = self.get_data(event, "label")
        category = self.get_data(event, "category")
        month = int(self.get_data(event, "month"))
        if not category in self.chosen_categories:
            return
        if event_type == "birthdays":
            day = int(self.get_data(event, "day"))
            entry_year = self.get_data(event, "year")
            if entry_year:
                label = label + " (" + str(year - int(entry_year)) + ")"
        elif event_type == "fixed_day_events":
            day = int(self.get_data(event, "day"))
        elif event_type == "nth_weekday_in_month_events":
            n = int(self.get_data(event, "n"))
            weekday = int(self.get_data(event, "weekday"))
            day = calendar.Calendar(weekday).monthdayscalendar(year, month)[n][0]
        elif event_type == "last_week_in_month_events":
            weekday = int(self.get_data(event, "weekday"))
            day = calendar.Calendar(weekday).monthdayscalendar(year, month)[-1][0]
        self.year_map[month][day].append(label)


    def parse_yaml(self, folder, year):
        categories = []
        all_data = []
        for file in glob.glob(folder + "/*.yml"):
            print("importing", file)
            data = []
            with open(file, 'r') as stream:
                try:
                    data = yaml.load(stream)
                except yaml.YAMLError as exc:
                    print(exc)
            events = data["calendar_entries"]
            categories += self.get_all_categories(events)
            all_data += [events]

        # check categories
        print("We found events in these categories:", categories)
        all = input("Should we add them all? (Y/n)")
        if all == "N" or all == "n":
            for category in categories:
                this_one = input("Add category '" + category + "'? (Y/n)")
                if this_one != "N" and this_one != "n":
                    self.chosen_categories.append(category)
        else:
            self.chosen_categories = categories

        print("These categories will be included:", self.chosen_categories)

        for event_type in self.EVENT_TYPES:
            for events in all_data:
                events_of_type = events[event_type]
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
        self.input_data.parse_yaml(folder, year)

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

