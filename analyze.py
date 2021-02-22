from apachelogs import LogParser
from attr import __description__
from tabulate import tabulate
from pandas import DataFrame
import pandas as pd
import argparse
import matplotlib.pyplot as plt


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_rows', None)


def Top_10_requests(df, report_type):
    """ 
    Function to identify top 10 requested URL with request count
    Params:
        df: Dataframe with valid log entries
        report_type: Report type option bar graph or tabular report
    """
    df.drop(columns=['host', 'status'], inplace=True)
    df["count"] = ""
    data = df.groupby("url", as_index=False).count().nlargest(10, "count")
    if report_type == 1:
        data.plot.bar(x="url", y="count", rot=90)
        plt.subplots_adjust(bottom=0.6)
        plt.show()
    if report_type == 2:
        print("Below is the tabular report:")
        tb = data.reset_index()[['url', 'count']]
        del(data)
        tb.index += 1
        tabularized_report = tabulate(tb, headers=[
                                      "Sl.No", "URL", "Number of times requested"])
        print(tabularized_report)


def Percent_success(df):
    """ 
    Function to identify percentage of successfull request
    Params:
        df: Dataframe with valid log entries
    """
    dt = df.sort_values("status")["status"]
    filter1 = dt >= 200
    filter2 = dt < 400
    success_percent = (dt.where(filter1 & filter2).count()/dt.count())*100
    print("Total success percent is: {0}%".format(
        format(success_percent, '.2f')))


def Percent_failed(df):
    """ 
    Function to identify percentage of unsuccessful request
    Params:
        df: Dataframe with valid log entries
    """
    dt = df.sort_values("status")["status"]
    filter1 = dt < 200
    filter2 = dt >= 400
    fail_percent = (dt.where(filter1 | filter2).count()/dt.count())*100
    print("Total fail percent is: {0}%".format(format(fail_percent, '.2f')))


def Top_10_failed(df_in, report_type):
    """ 
    Function to identify top 10 failed requests
    Params:
        df_in: Dataframe with valid log entries
        report_type: Report type option bar graph or tabular report
    """
    df_in.drop(columns=['host'], inplace=True)
    df_in["count"] = ""
    df = df_in.groupby(["url", "status"], as_index=False).count()
    del(df_in)
    df.set_index('url', inplace=True)
    filter1 = df["status"] < 200
    filter2 = df["status"] >= 400
    dt = df.where(filter1 | filter2).dropna()
    del(df)
    dt.drop(columns=["status"], inplace=True)
    de = dt.sort_values(["count"], ascending=False).nlargest(10, "count")
    if report_type == 1:
        tb = de.reset_index()[['url', 'count']]
        del(de)
        tb.plot.bar(x="url", y="count", rot=90)
        plt.subplots_adjust(bottom=0.6)
        plt.xlabel("failed url")
        plt.ylabel("failed count")
        plt.show()
    if report_type == 2:
        print("Below is the tabular report:")
        tb = de.reset_index()[['url', 'count']]
        del(de)
        tb.index += 1
        tabularized_report = tabulate(tb, headers=[
                                      "Sl.No", "URL", "Number of times request failed"])
        print(tabularized_report)


def Top_10_host(df, report_type):
    """ 
    Function to identify top 10 host making maximum request
    Params:
        df_in: Dataframe with valid log entries
        report_type: Report type option bar graph or tabular report
    """
    df.drop(columns=['url', 'status'], inplace=True)
    df["count"] = ""
    data = df.groupby("host").count().nlargest(10, "count")
    if report_type == 1:
        tb = data.reset_index()[['host', 'count']]
        del(data)
        tb.plot.bar(x="host", y="count", rot=90)
        plt.subplots_adjust(bottom=0.6)
        plt.xlabel("host")
        plt.ylabel("count")
        plt.show()
    if report_type == 2:
        print("Below is the tabular report:")
        tb = data.reset_index()[['host', 'count']]
        del(data)
        tb.index += 1
        tabularized_report = tabulate(tb, headers=[
                                      "Sl.No", "HOST", "Number of times requested"])
        print(tabularized_report)

def Top_10_host_top_5_url(df,report_type):
    data = df.groupby("host", as_index=False).head(5)
    tabularized_report = tabulate(data)
    print(tabularized_report)

def Analyze_it(filepath, option, report_type):
    """ 
    Function to import log file and perform further tasks
    Params:
        filepath: Path to the log file
        option: Which type of analysis needs to be done
    """
    parser = LogParser(
        "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\" \"-\"")
    requests = []
    count = 0
    with open(filepath, 'r') as f:
        lines = f.readlines()
        for line in lines:
            try:
                entry = parser.parse(line)
                request = {
                    "url": entry.request_line,
                    "status": entry.final_status,
                    "host": entry.remote_host
                }
                requests.append(request)
                count += 1
                if count > 500:
                    break
            except Exception as e:
                continue
    df = DataFrame(requests, columns=['url', 'status', 'host'])
    if option == 1:
        Top_10_requests(df, report_type)
    if option == 2:
        Percent_success(df)
    if option == 3:
        Percent_failed(df)
    if option == 4:
        Top_10_failed(df, report_type)
    if option == 5:
        Top_10_host(df, report_type)
    if option == 6:
        Top_10_host_top_5_url(df, report_type)    


if __name__ == "__main__":
    # """ 
    # Entry point
    # """
    # try:
    #     parser = argparse.ArgumentParser(
    #         description="Collect Details for log analytics program")
    #     parser.add_argument("-f", "--filepath", required=True,
    #                         help="Path to the log file")
    #     args = parser.parse_args()
    #     filepath = args.filepath

    #     print(f"""{bcolors.OKGREEN} 
    #             This program is to analyze the log files generated by apache server.  
    #             Please choose:
    #             1 - for Top 10 requested pages and the number of requests made for each.
    #             2 - for Percentage of successful requests (anything in the 200s and 300s range).
    #             3 - for Percentage of unsuccessful requests (anything that is not in the 200s or 300s range).
    #             4 - for Top 10 unsuccessful page requests.
    #             5 - for Top 10 hosts making the most requests, displaying the IP address and number of requests made.
    #             {bcolors.ENDC}""")

    #     option = int(
    #         input(f"{bcolors.OKGREEN}Enter your option:{bcolors.ENDC}"))
    #     report_type = None
    #     if option not in (2, 3):
    #         report_type = int(
    #             input(f"{bcolors.OKGREEN}Enter 1 for bargraph or 2 for tabular report:{bcolors.ENDC}"))
    #     print(
    #         f"{bcolors.WARNING} Analyzing and sharing the report please wait{bcolors.ENDC}")
        Analyze_it(filepath="access.log.txt", option=6, report_type=6)
    # except Exception as e:
    #     print(e)
