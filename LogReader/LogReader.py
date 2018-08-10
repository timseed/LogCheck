import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from random import randint
import seaborn as sns
import matplotlib
import daiquiri


class LogReader(object):

    def __init__(self):
        self.junk=0

    def fake_data(self,start_date="1-Aug-2018",
                          end_date="1-Nov-2018",
                          frequency="15min",
                          summed_freq="1W"):
        """
        Fake some data !!
        :param start_date: The Start Date for the Fake Data
        :param end_date:  The End Date for the Fake Data
        :param frequency: Frequency of the Fake Data in the Dataset (15Min,30s,1D) etc
        :param summed_freq: Data frequency summation period (1D, 2D, 1W,2M) etc
        :return: A pandas DataFrame with ALl the Data Points in it
        """

        # Some exchanges
        exc = ["Ex{}".format(n) for n in range(130)]
        # A Feed
        feed = ['F{}'.format(n) for n in range(38)]


        def good_bad_etc():

            status = ['Ok', 'Warning', 'Fail']
            v = randint(0, 100)
            if v < 80:
                return status[0]
            elif v < 94:
                return status[1]
            else:
                return status[2]


        def Simplify_date(date_time_obj):
            """
            Attempt to make Date-Time easier to read. Does not seem to work as intended
            :param date_time_obj:
            :return:
            """
            return date_time_obj.strftime("%Y-%M-%D")


        # Data Frame with GOOD Data Only in it
        df_good = pd.DataFrame(columns=['Id', 'When', 'Exchange', 'Feed', 'Status'])

        #
        # Fake Some Data
        #
        # Set the ID
        df_good.Id = [a for a in range(0, len(df_good))]
        # Generate a Date/Time Value
        df_good.When = pd.date_range(start="1-Aug-2018", end="1-Nov-2018", freq='15min')

        id = [a for a in range(0, len(df_good))]
        ex = [exc[randint(0, len(exc) - 1)] for a in range(0, len(df_good))]
        fd = [feed[randint(0, len(feed) - 1)] for a in range(0, len(df_good))]
        df_good.Id = id
        df_good.Exchange = ex
        df_good.Feed = fd
        # Use a simple Function to skew the Dist of the Good-Bad etc
        df_good.Status = df_good.Status.apply(lambda x: good_bad_etc())

        df_good['Ex_Feed'] = df_good.Exchange + " " + df_good.Feed

        return df_good


    def Process(self,df_good):
        """
        Do the Data Frame Filtering - producing a pivot table which then can
        be rendered


        :param df_good: Pandas Dataframe with ALL (good and Bad value in it)
        :return: df_fail: Pandas DataFrame which has been pivoted  - this contains all the Bad Data Records
        """

        #
        #  Remove all the OK's !!
        #
        df_good = df_good[df_good.Status != 'Ok']

        df_summary = df_good.groupby(by=['When', 'Ex_Feed', 'Status']).size().to_frame('size').reset_index().sort_values(
            ['size'], ascending=[False])
        df_summary.index = pd.DatetimeIndex(df_summary.When)
        # Remove the Col as we are using it as an index
        df_summary.drop(columns=['When'], inplace=True)

        df_grouped = df_summary.groupby(['Ex_Feed', 'Status']).resample('w')['size'].sum()
        #
        # Now remove the index ...i.e. flatten the Output
        df_grouped = df_grouped.reset_index()
        #
        # Only Process Failed Links
        #
        df_fail = (df_grouped[df_grouped.Status == 'Fail']).drop(columns=['Status'])
        #
        #
        # df_fail.When=df_fail.When.apply(lambda x: Simplify_date(pd.to_datetime(x)))
        df_fail = df_fail.pivot("When", "Ex_Feed", "size")
        # df_fail.reset_index(inplace=True)
        # MUST get rid of nan values - else nasty crash will occur.
        df_fail.fillna(0, inplace=True)

        return df_fail

    def Img(self,df_pivoted_data):
        """

        :param df_pivoted_data: A Pandas Data Frame which has been pivoted
        :return: A Matplotlib Image
        """

        """ Note this will need to be base64 encoded before it can be passed to a web page"""
        return sns.heatmap(df_pivoted_data, annot=True)