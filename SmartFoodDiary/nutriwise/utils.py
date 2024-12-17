from collections import defaultdict
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import csv

# Function to generate chart data based on user's entries and selected metrics
def generate_chart_data(entries, metrics, chart_type):
    data = defaultdict(list)
    labels = []
    metric_values = {metric: [] for metric in metrics}

    # Process user entries to populate data for each metric
    for entry in entries:
        labels.append(entry.timestamp.strftime('%Y-%m-%d %H:%M:%S'))
        for metric in metrics:
            metric_values[metric].append(getattr(entry, metric, 0))  # Dynamically fetch metric value

    # Prepare the final dataset for the chart
    datasets = []
    for metric, values in metric_values.items():
        datasets.append({
            'label': metric.capitalize(),
            'data': values
        })

    return {
        'type': chart_type,
        'data': {
            'labels': labels,
            'datasets': datasets
        }
    }

def generate_pdf(report_data, response):
    c = canvas.Canvas(response, pagesize=letter)
    c.drawString(100, 750, "Custom Report")
    c.drawString(100, 730, f"Data: {json.dumps(report_data)}")  # Add the report data
    c.save()

# Function to generate CSV
def generate_csv(report_data, response):
    writer = csv.writer(response)
    writer.writerow(['Metric', 'Value'])
    for metric, value in report_data.items():
        writer.writerow([metric, value])