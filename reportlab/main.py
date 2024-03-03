from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px

fig = px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])
fig.show()
fig.write_image("random.pdf")


def create_report(introduction, metrics_data, table_data, graphs_data):
    # Create a PDF document
    doc = SimpleDocTemplate("algo_trading_report.pdf", pagesize=letter)

    # Content elements
    elements = []

    # Introduction section
    intro_style = getSampleStyleSheet()["Heading1"]
    elements.append(Paragraph("Introduction", intro_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(introduction, getSampleStyleSheet()["BodyText"]))

    # Metrics section
    metrics_style = getSampleStyleSheet()["Heading1"]
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Key Metrics", metrics_style))
    elements.append(Spacer(1, 6))

    # Convert metrics data to a table
    metrics_table_data = [["Metric", "Value"]]
    metrics_table_data.extend(metrics_data.items())

    metrics_table = Table(metrics_table_data, colWidths=[2 * inch, 1 * inch])
    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige)])
    metrics_table.setStyle(style)

    elements.append(metrics_table)

    # Additional space for tables
    elements.append(Spacer(1, 12))

    # Additional table section
    table_style = getSampleStyleSheet()["Heading1"]
    elements.append(Paragraph("Additional Table", table_style))
    elements.append(Spacer(1, 6))

    # Convert table data to a table
    additional_table_data = [["Column1", "Column2", "Column3"]]
    additional_table_data.extend(table_data)

    additional_table = Table(additional_table_data, colWidths=[1 * inch, 1 * inch, 1 * inch])
    additional_table.setStyle(style)

    elements.append(additional_table)

    # Graphs section
    graph_style = getSampleStyleSheet()["Heading1"]
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Graphs", graph_style))
    elements.append(Spacer(1, 6))

    for graph_data in graphs_data:
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(f"Graph: {graph_data['title']}", getSampleStyleSheet()["BodyText"]))
        elements.append(Spacer(1, 6))

        fig = make_subplots(rows=1, cols=1, subplot_titles=[graph_data['title']])
        fig.add_trace(go.Scatter(x=graph_data['x'], y=graph_data['y'], mode='lines', name='Sample Line'))

        pdf_file = f"{graph_data['title']}_graph.pdf"
        pio.write_image(fig, pdf_file, format='pdf')

        # load from pdf
        graph_image = Image(pdf_file, width=400, height=300)
        elements.append(graph_image)

    # Build the PDF document
    doc.build(elements)


def main():
    introduction_text = """
    This is a sample introduction to the algo trading strategy report.
    Provide an overview of the strategy, its objectives, and any relevant background information.
    """

    # Example metrics, table, and graphs data
    metrics_data = {"Total Returns": 15.2, "Sharpe Ratio": 1.8, "Max Drawdown": -5.2}
    table_data = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
    graphs_data = [{'title': 'Sample Graph', 'x': [1, 2, 3], 'y': [4, 5, 6]}]

    # Generate the PDF report
    create_report(introduction_text, metrics_data, table_data, graphs_data)


# Example usage
if __name__ == "__main__":
    main()
