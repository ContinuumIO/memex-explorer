import csv
import sys
from blaze import *
import pandas as pd
from bokeh.plotting import *
import numpy as np
import datetime as dt
from bokeh.embed import components
from bokeh.resources import CDN



class Termite(object):

    # Draw a termite plot to visualize topics and words from an LDA.
    def __init__(self, input_data='data_monitor/summary.txt'):
        self.input_data = input_data
        self.data, self.source = self.update_source()
        #self.plot = self.create_plot()

    def generate_data(self):
        """
        Generates the csv files from the summary.txt output of the LDA.
        """
        # Transform the summary.txt file into a csv file with the purpose of inputing the file into Blaze-Bokeh for visualization.
        fmt ='%Y-%m-%d-%H-%M-%S-%f' 
        current_time = dt.datetime.now().strftime(fmt)
        #topics_file = '%s_topics_data.csv' % current_time
        topics_file = 'topics_data.csv'
        with open(topics_file, 'wb') as outfile:
            writer = csv.writer(outfile, delimiter=',')
            with open(self.input_data, 'rb') as f:
                reader = csv.reader(f, delimiter='\t')
                try:
                    for row in reader:
                        if any(row):
                            if row[0].startswith("Topic"):
                                topic = row[0]
                                writer.writerow(row)
                            else:
                                pass
                except csv.Error as e:
                    sys.exit('file %s, line %d: %s' % (self.input_data, reader.line_num, e))

        # Transform the summary.txt file into a csv file with the purpose of inputing the file into Blaze-Bokeh for visualization.
        #termite_file = '%s_termite_data.csv' % current_time
        termite_file = 'termite_data.csv'
        with open(termite_file, 'wb') as outfile:
            writer = csv.writer(outfile, delimiter=',')
            with open(self.input_data, 'rb') as f:
                reader = csv.reader(f, delimiter='\t')
                try:
                    for row in reader:
                        if any(row):
                            if row[0].startswith("Topic"):
                                topic = row[0]
                                # Uncomment if you want the topic aggregation result as a row
                                #writer.writerow(row)
                            else:
                                row[0] = topic
                                writer.writerow(row)
                except csv.Error as e:
                    sys.exit('file %s, line %d: %s' % (self.input_data, reader.line_num, e))

        return topics_file, termite_file

    def update_source(self):
        topics_file, termite_file = self.generate_data()
        
        t = Table(CSV(termite_file, columns=['topic', 'word', 'result']))
        df = into(DataFrame, t)

        top = Table(CSV(topics_file, columns=['topic', 'word', 'result']))
        topics_df = into(DataFrame, top)

        topics_df = topics_df[["topic", "result"]]
        topics_df.sort('result', ascending=False)

        gby_df = df.groupby('topic')

        gby_df.describe()

        t_by = by(t.topic, max=t.result.max(), min=t.result.min())

        # size proportional to result in Karan's example 0-10 range.
        MAX = compute(t.result.max())
        MIN = compute(t.result.min())

        # Create a size variable to define the size of the the circle for the plot.
        t = transform(t, size=sqrt((t.result - MIN)/(MAX - MIN))*50)

        data = t

        source = into(ColumnDataSource, data)

        return data, source

    def create_plot(self, output_html='termite.html'):

        WORDS = self.data['word'].distinct()
        WORDS = into(list, WORDS)

        TOPICS = self.data['topic'].distinct()
        TOPICS = into(list, TOPICS)

        figure(x_range=TOPICS, y_range=WORDS, 
               plot_width=400, plot_height=400,
               title="Termite Plot", tools='save')

        circle(x="topic", y="word", size="size", fill_alpha=0.6, source=self.source)
        xaxis().major_label_orientation = np.pi/3
        #show()

        plot = curplot()
        termite = components(plot, CDN)

        return termite
