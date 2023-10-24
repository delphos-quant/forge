import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


def to_pdf(data, round_cols, n_rows=10):
    preview = data.sample(n_rows)

    # Reformat round values to be in format 1e3, 1e6 etc with no digits after decimal point
    # Using .loc or .iloc
    preview.loc[:, round_cols] = preview.loc[:, round_cols].applymap(lambda x: f"{x:.0e}")

    # Remove columns 'round_D' to 'round_F'
    preview = preview.drop(columns=[f"round_{chr(ord('D') + i)}" for i in range(3)])

    # Crop 'category_list' column to max 1 category (separated by | char)
    preview['category_list'] = preview['category_list'].str.split('|').str[1]
    latex = preview.to_latex(index=False, escape=False)

    # Create a PDF document
    pdf_filename = 'investments_VC.pdf'
    document = SimpleDocTemplate(pdf_filename, pagesize=letter)

    # Create a list of elements to add to the document
    elements = []

    # Convert the DataFrame to a list of lists
    table_data = [preview.columns]  # Include column headers
    table_data += preview.values.tolist()

    # Create a table from the data
    table = Table(table_data)

    # Style the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])

    table.setStyle(style)

    # Add the table to the list of elements
    elements.append(table)

    # Build the PDF document
    document.build(elements)


def main():
    data = pd.read_csv("investments_VC.csv", encoding="ISO-8859-1")
    print(data)
    print(data.columns)
    # rounds = ["round_A", ..., "round_H"]
    vc_rounds = ["round_" + chr(ord('A') + i) for i in range(8)]
    data = data[['name', 'category_list', 'founded_year', ' funding_total_usd ', *vc_rounds]]

    # Select only data with more or equal to two investment rounds (not null and also not 0)
    data = data[data[vc_rounds].notnull().sum(axis=1) >= 2]
    data = data[data[vc_rounds].sum(axis=1) > 0]

    to_pdf(data, round_cols=vc_rounds)


if __name__ == "__main__":
    main()
