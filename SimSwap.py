#!/usr/bin/env python

"""SimSwap.py: Creates a network graph to compare familiar and unfamiliar subscriber transactions, post-SIM swap.
Running SimSwap.py will save the file TZ_SimSwap_Network.html. The HTML file displays an interactive network
graph with hover functionality, revealing subscriber names and MSISDNs.
"""

__author__ = 'Alex Friedmann'
__email__ = 'alex.mark.friedmann@gmail.com'

# Imports
import pandas as pd
import networkx as nx
from bokeh.io import save, output_file
from bokeh.transform import linear_cmap
from bokeh.models import (Plot, Range1d, MultiLine, Circle, HoverTool, TapTool, PanTool, WheelZoomTool)
from bokeh.models.graphs import from_networkx, EdgesAndLinkedNodes


class SimSwap:

    def __init__(self, file_name):
        self.file_name = file_name

    def read_csv(self):
        """Creates Pandas dataframe from CSV file.
        Returns: data - Pandas DataFrame object
        """
        try:
            data = pd.read_csv(self.file_name, sep=';', usecols=[4, 5, 6, 7, 9, 10, 11, 12, 13], parse_dates=[0, 2])

            # Create 'TIME' column recording whether transactions before(0) or after(1) SIM reset
            data['TIME'] = [0 if data.iat[i, 0] < data.iat[i, 2] else 1 for i in range(len(data.index))]

            return data

        except FileNotFoundError:
            print('CSV file not found.')
            raise

    def build_nx(self):
        """
        Creates Networkx graph from Pandas dataframe.
        Returns: nx_graph - Networkx graph object
        """
        try:
            data = self.read_csv()
            nx_graph = nx.from_pandas_edgelist(data, source='PIN RESET MSISDN', target='CREDIT PARTY',
                                               edge_attr=('PIN RESET MSISDN', 'DEBIT PARTY', 'CREDIT PARTY',
                                                          'CREDIT PARTY SHORTCODE/MSISDN', 'TIME',
                                                          'TRANSACTION TIME', 'TRANSACTION ID',
                                                          'TRANSACTION AMOUNT', 'TIME'))
            return nx_graph
        except KeyError:
            print('Incorrect CSV file heading.')
            raise

    def build_bokeh(self):
        """
        Creates Bokeh graph from Networkx graph.
        Returns: show(plot): A Bokeh layout object
        """

        nx_graph = self.build_nx()

        # Format data for use in Bokeh's ColumnDataSource
        atts = [d for u, v, d in nx_graph.edges(data=True)]
        r_msisdn = []
        r_name = []
        cr_msisdn = []
        cr_name = []
        ba_time = []
        node_color_list = []
        for i in atts:
            r_msisdn.append(i.get('PIN RESET MSISDN'))
            r_name.append(i.get('DEBIT PARTY'))
            cr_msisdn.append(i.get('CREDIT PARTY'))
            cr_name.append(i.get('CREDIT PARTY SHORTCODE/MSISDN'))
            ba_time.append(i.get('TIME'))

        # Create edge colour list
        for i in list(nx_graph.nodes()):
            if len(str(i)) < 12:
                node_color_list.append(0)
            elif i in r_msisdn:
                node_color_list.append(1)
            else:
                node_color_list.append(2)

        # Create Bokeh canvas and title
        plot = Plot(plot_width=800, plot_height=800,
                    x_range=Range1d(-1.1, 1.1), y_range=Range1d(-1.1, 1.1))

        plot.title.text = "Tanzania SIM Swaps & PIN Resets 21-28 August 2018"

        # Create Bokeh hover tools
        hover = [('Reset No.', '@rmsisdn'),
                 ('Reset Name', '@rname'),
                 ('Credit No.', '@crmsisdn'),
                 ('Creditor Name', '@crname')]
        plot.add_tools(HoverTool(tooltips=hover), TapTool(), PanTool(), WheelZoomTool())

        # Initialise Bokeh renderer from Networkx graph
        graph_renderer = from_networkx(nx_graph, nx.spring_layout, scale=1, center=(0, 0))

        # Initialise node ColumnDataSource data
        graph_renderer.node_renderer.data_source.data['node_colors'] = node_color_list

        # Initialise edge ColumnDataSource data
        graph_renderer.edge_renderer.data_source.data['rmsisdn'] = r_msisdn
        graph_renderer.edge_renderer.data_source.data['rname'] = r_name
        graph_renderer.edge_renderer.data_source.data['crmsisdn'] = cr_msisdn
        graph_renderer.edge_renderer.data_source.data['crname'] = cr_name
        graph_renderer.edge_renderer.data_source.data['batime'] = ba_time

        # Define node colors and palette
        node_target_palette = ['#808080', '#B22222', '#FFA07A']
        node_colors = linear_cmap(field_name='node_colors', palette=node_target_palette,
                                  low=0, high=2)

        # Define edge colors and palette
        target_palette = ['mediumseagreen', 'firebrick']
        edge_colors = linear_cmap(field_name='batime', palette=target_palette,
                                  low=1, high=0)

        # Render nodes
        graph_renderer.node_renderer.glyph = Circle(size=7, fill_color=node_colors, fill_alpha=1,
                                                    line_color=node_colors)
        graph_renderer.node_renderer.selection_glyph = Circle(size=10, fill_color=node_colors, fill_alpha=1)
        graph_renderer.node_renderer.hover_glyph = Circle(size=15, fill_color=node_colors, fill_alpha=1)

        # Render edges
        graph_renderer.edge_renderer.glyph = MultiLine(line_color=edge_colors, line_alpha=0.5, line_width=3)
        graph_renderer.edge_renderer.selection_glyph = MultiLine(line_color=edge_colors, line_width=5)
        graph_renderer.edge_renderer.hover_glyph = MultiLine(line_color=edge_colors, line_width=5)

        # Set hover and selection policy
        graph_renderer.selection_policy = EdgesAndLinkedNodes()
        graph_renderer.inspection_policy = EdgesAndLinkedNodes()

        # Attach renderers to canvas
        plot.renderers.append(graph_renderer)

        # Save plot as HTML
        output_file('TZ_SimSwap_Network.html')
        save(plot)


try:
    s = SimSwap('/Users/alex/PycharmProjects/NodeNetworks/csv_files/TZ_28_Aug.csv')
    s.build_bokeh()
except TypeError as type_error:
    print('SimSwap() must take csv file path as a string')
    raise
except FileNotFoundError as file_error:
    print('{0}'.format(file_error))
except KeyError as key_error:
    print('Key: {0}'.format(key_error))
