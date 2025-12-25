#!/usr/bin/env python3
"""
Graph Maker - Generate JPG graphs from InfluxDB data for e-paper display
"""

import os
import yaml
from datetime import datetime
import pytz
from influxdb_client import InfluxDBClient
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path


class GraphMaker:
    def __init__(self, config_path='config.yaml'):
        """Initialize GraphMaker with configuration file"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Timezone used for plotting (defaults to Finland)
        self.tz = pytz.timezone(self.config.get('timezone', 'Europe/Helsinki'))
        
        # Initialize InfluxDB client
        self.client = InfluxDBClient(
            url=self.config['influxdb']['url'],
            token=self.config['influxdb']['token'],
            org=self.config['influxdb']['org']
        )
        self.query_api = self.client.query_api()
        
        # Create output directory if it doesn't exist
        output_dir = Path(self.config['output']['directory'])
        output_dir.mkdir(parents=True, exist_ok=True)
    
    def query_data(self, query):
        """Query data from InfluxDB"""
        try:
            tables = self.query_api.query(query)
            
            timestamps = []
            values = []
            
            for table in tables:
                for record in table.records:
                    # Convert UTC timestamp to Finland timezone
                    utc_time = record.get_time()
                    if utc_time.tzinfo is None:
                        utc_time = pytz.utc.localize(utc_time)
                    local_time = utc_time.astimezone(self.tz)
                    timestamps.append(local_time)
                    values.append(record.get_value())
            
            return timestamps, values
        except Exception as e:
            print(f"Error querying data: {e}")
            return [], []
    
    def create_graph(self, graph_config):
        """Create a graph based on configuration"""
        print(f"Creating graph: {graph_config['name']}")
        
        # Query data
        timestamps, values = self.query_data(graph_config['query'])
        
        if not timestamps or not values:
            print(f"No data found for {graph_config['name']}")
            return
        
        # Set up the figure with specified size
        width = graph_config['size']['width'] / self.config['output']['dpi']
        height = graph_config['size']['height'] / self.config['output']['dpi']
        
        fig, ax = plt.subplots(figsize=(width, height))
        
        # Get font sizes (with defaults)
        font_size = graph_config.get('font_size', {})
        title_size = font_size.get('title', 14)
        axis_label_size = font_size.get('axis_label', 10)
        tick_label_size = font_size.get('tick_label', 9)
        
        # Get graph type (default to line)
        graph_type = graph_config.get('graph_type', 'line')

        # For bar charts, try to infer the interval from the data so bars span
        # the full interval starting at the timestamp (e.g., 00:00->00:15).
        bar_width_days = (15 * 60) / 86400  # default: 15 minutes
        if graph_type == 'bar' and len(timestamps) > 1:
            deltas = []
            for t1, t2 in zip(timestamps, timestamps[1:]):
                dt = (t2 - t1).total_seconds()
                if dt > 0:
                    deltas.append(dt)
            if deltas:
                deltas.sort()
                median_dt = deltas[len(deltas) // 2]
                bar_width_days = median_dt / 86400
        
        # Plot the data based on graph type
        if graph_type == 'bar':
            # Align bars to the interval start time (left edge at timestamp)
            ax.bar(timestamps, values, width=bar_width_days, align='edge')
        else:  # default to line
            ax.plot(timestamps, values, linewidth=2)
        
        # Set labels and title with configurable font sizes
        ax.set_title(graph_config['title'], fontsize=title_size, fontweight='bold')
        
        # Set xlabel only if provided
        if 'xlabel' in graph_config and graph_config['xlabel']:
            ax.set_xlabel(graph_config['xlabel'], fontsize=axis_label_size)
        
        # Set ylabel only if provided
        if 'ylabel' in graph_config and graph_config['ylabel']:
            ax.set_ylabel(graph_config['ylabel'], fontsize=axis_label_size)
        
        # Format x-axis for dates (explicit timezone to avoid UTC offset)
        try:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=self.tz))
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=4, tz=self.tz))
        except TypeError:
            # Fallback for older matplotlib: plot naive local times
            timestamps = [ts.replace(tzinfo=None) for ts in timestamps]
            ax.clear()
            if graph_type == 'bar':
                ax.bar(timestamps, values, width=bar_width_days, align='edge')
            else:
                ax.plot(timestamps, values, linewidth=2)
            ax.set_title(graph_config['title'], fontsize=title_size, fontweight='bold')
            if 'xlabel' in graph_config and graph_config['xlabel']:
                ax.set_xlabel(graph_config['xlabel'], fontsize=axis_label_size)
            if 'ylabel' in graph_config and graph_config['ylabel']:
                ax.set_ylabel(graph_config['ylabel'], fontsize=axis_label_size)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))
        plt.xticks(rotation=45, fontsize=tick_label_size)
        plt.yticks(fontsize=tick_label_size)
        
        # Grid for better readability
        ax.grid(True, alpha=0.3, color='red')
        
        # Tight layout to prevent label cutoff
        plt.tight_layout()
        
        # Save the graph
        output_path = os.path.join(
            self.config['output']['directory'],
            graph_config['filename']
        )
        
        plt.savefig(
            output_path,
            format=self.config['output']['format'],
            dpi=self.config['output']['dpi'],
            bbox_inches='tight'
        )
        plt.close()
        
        print(f"Graph saved to: {output_path}")
    
    def generate_all_graphs(self):
        """Generate all graphs defined in config"""
        print(f"Generating {len(self.config['graphs'])} graphs...")
        
        for graph_config in self.config['graphs']:
            try:
                self.create_graph(graph_config)
            except Exception as e:
                print(f"Error creating graph {graph_config['name']}: {e}")
        
        print("All graphs generated!")
    
    def close(self):
        """Close InfluxDB client connection"""
        self.client.close()


def main():
    """Main entry point"""
    graph_maker = GraphMaker()
    
    try:
        graph_maker.generate_all_graphs()
    finally:
        graph_maker.close()


if __name__ == '__main__':
    main()
