import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from matplotlib.figure import Figure
from random import randint
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import daiquiri
import base64
import io


class LogReader(object):

    def __init__(self):
        self.junk=0

    def fake_data(self,start_date="1-Aug-2018",
                          end_date="1-Nov-2018",
                          data_frequency="15min"):
        """
        Fake some data !!
        :param start_date: The Start Date for the Fake Data
        :param end_date:  The End Date for the Fake Data
        :param frequency: Frequency of the Fake Data in the Dataset (15Min,30s,1D) etc
        :param summed_freq: Data frequency summation period (1D, 2D, 1W,2M) etc
        :return: A pandas DataFrame with ALl the Data Points in it
        """

        # Some exchanges
        EX_MAX=10
        FD_MAX=10

        exc = ["Ex{}".format(n) for n in range(EX_MAX)]
        # A Feed
        feed = ['F{}'.format(n) for n in range(FD_MAX)]


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
            Attempt to make Date-Time easier to read.

            Does not seem to work as intended !!


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
        df_good.When = pd.date_range(start=start_date, end=end_date, freq=data_frequency)

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


    def Process(self,df_good,resample_freq="w"):
        """
        Do the Data Frame Filtering - producing a pivot table which then can
        be rendered



        :param df_good: Pandas Dataframe with ALL (good and Bad value in it)
        :param resample_freq: Time period i.e. (w,2w,1d,12d,2m)
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

        df_grouped = df_summary.groupby(['Ex_Feed', 'Status']).resample(resample_freq)['size'].sum()
        #
        # Now remove the index ...i.e. flatten the Output
        df_grouped = df_grouped.reset_index()
        #
        # Only Process Failed Links
        #
        df_fail = (df_grouped[df_grouped.Status == 'Fail']).drop(columns=['Status'])
        #
        #
        #df_fail.When=df_fail.When.apply(lambda x: Simplify_date(pd.to_datetime(x)))
        #df_fail = df_fail.pivot("When", "Ex_Feed","size")

        df_fail_pvt = df_fail.pivot(index="Ex_Feed", columns="When", values="size")

        # df_fail.reset_index(inplace=True)
        # MUST get rid of nan values - else nasty crash will occur.
        df_fail_pvt.fillna(0, inplace=True)
        return df_fail_pvt

    def Img(self,orig_data, df_pivoted_data):
        """

        :param orig_data: A Pandas Data Frame
        :param df_pivoted_data: A Pandas Data Frame which has been pivoted
        :return: A Matplotlib Image
        """

        """ Note this will need to be base64 encoded before it can be passed to a web page"""

        #max_val_in_df = max(list(df_pivoted_data.max()))

        #
        # Reformat X Axis using  using the DataFrom prior to the pivot
        #

        rv = sns.heatmap(df_pivoted_data, annot=True,
                    cmap='gist_rainbow_r')
        print("Type of rv is {}".format(type(rv)))
        f=rv.figure
        f.savefig("output.png")

        return rv

    def Img_new(self,orig_data,df_pivoted_data):
        from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
        from matplotlib.figure import Figure
        from matplotlib.dates import DateFormatter

        fig = Figure()
        ax = fig.add_subplot(111)

        rv = sns.heatmap(df_pivoted_data, annot=True,
                         cmap='gist_rainbow_r')

        fig.autofmt_xdate()
        canvas = FigureCanvas(fig)
        return canvas

    def plot_to_b64png(self,heat_canvas):
        '''

        :param df_plot: the output of df.plot()
        :return: base64 version of img
        '''

        fig = heat_canvas.figure
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        buffer = b''.join(buf)

        b64_plot=base64.encodebytes(buffer).decode('utf-8').replace('\n', '')

        return b64_plot