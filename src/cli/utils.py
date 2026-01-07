from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pandas import DataFrame

if TYPE_CHECKING:
    from pandas.core.series import Series


def format_content(row: Any) -> str:
    """Format database row for html content."""
    return str(row).replace("<", "&lt;").replace(">", "&gt;")


def get_html_template() -> str:
    """Return HTML template string."""
    return """<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Jobs Table</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                background-color: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            th {{
                background-color: paleturquoise;
                padding: 12px;
                text-align: left;
                font-weight: bold;
                border-bottom: 2px solid #ddd;
            }}
            td {{
                background-color: lavender;
                padding: 12px;
                border-bottom: 1px solid #ddd;
            }}
            tr:hover td {{
                background-color: #e6d5f5;
            }}
            .view-btn {{
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 6px 12px;
                cursor: pointer;
                border-radius: 4px;
                font-size: 14px;
            }}
            .view-btn:hover {{
                background-color: #45a049;
            }}
            
            .modal {{
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.5);
            }}
            .modal-content {{
                background-color: white;
                margin: 5% auto;
                padding: 20px;
                border-radius: 8px;
                width: 80%;
                max-width: 800px;
                max-height: 80vh;
                overflow-y: auto;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            }}
            .close {{
                color: #aaa;
                float: right;
                font-size: 28px;
                font-weight: bold;
                cursor: pointer;
                line-height: 20px;
            }}
            .close:hover {{
                color: #000;
            }}
            .modal-header {{
                border-bottom: 2px solid #4CAF50;
                padding-bottom: 10px;
                margin-bottom: 15px;
            }}
            .modal-body {{
                line-height: 1.6;
                white-space: pre-wrap;
            }}
        </style>
    </head>
    <body>
        <h1>Search Query: {3}</h1>
        <p><strong>Total Leads: {0}</strong></p>
        <table id="jobsTable">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Title</th>
                    <th>Company</th>
                    <th>Location</th>
                    <th>Date Posted</th>
                    <th>Email</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
                {1}
            </tbody>
        </table>

        <div id="modal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeModal()">&times;</span>
                <div class="modal-header">
                    <h2 id="modalTitle"></h2>
                </div>
                <div class="modal-body" id="modalBody"></div>
            </div>
        </div>

        <script>
            const descriptions = {{{2}}};
            
            function showModal(id) {{
                const modal = document.getElementById('modal');
                const modalTitle = document.getElementById('modalTitle');
                const modalBody = document.getElementById('modalBody');
                
                modalTitle.textContent = descriptions[id].title;
                modalBody.textContent = descriptions[id].desc;
                modal.style.display = 'block';
            }}

            function closeModal() {{
                document.getElementById('modal').style.display = 'none';
            }}

            window.onclick = function(event) {{
                const modal = document.getElementById('modal');
                if (event.target == modal) {{
                    modal.style.display = 'none';
                }}
            }}

            document.addEventListener('keydown', function(event) {{
                if (event.key === 'Escape') {{
                    closeModal();
                }}
            }});
        </script>
    </body>
    </html>
"""


def format_data(idx: int, row: Series) -> str:
    """Format data."""
    company_url = str(row["company_url"])
    if company_url in ["nan", "-"]:
        company_html = "-"
    else:
        company_html = f'<a href="{company_url}" target="_blank" rel="noopener noreferrer">{format_content(row["company"])}</a>'

    return f"""
            <tr>
                <td>{idx + 1}</td>
                <td>{format_content(row["title"])}</td>
                <td>{company_html}</td>
                <td>{format_content(row["location"])}</td>
                <td>{format_content(row["date_posted"])}</td>
                <td>{format_content(row["emails"])}</td>
                <td><button class="view-btn" onclick="showModal({idx})">View Description</button></td>
            </tr>
    """


def generate_descriptions(idx: int, row: Series) -> str:
    """Generate description from a data row."""
    desc = str(row['description']).replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
    title = str(row['title']).replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
    return f"{idx}: {{title: `{title}`, desc: `{desc}`}},\n"


def generate_html_content(df: DataFrame, title: str) -> str:
    """Generate html content."""
    rows = ""
    descriptions = ""

    for i, row in enumerate(df.iterrows()):
        rows += format_data(i, row[1])
        descriptions += generate_descriptions(i, row[1])

    html_template = get_html_template()
    return html_template.format(str(len(df)), rows, descriptions, title)
    