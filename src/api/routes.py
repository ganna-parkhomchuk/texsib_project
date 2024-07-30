from flask import request, render_template
from datetime import datetime
from src.database.database import get_db


def init_routes(app):
    """This function initialize routes for the web service"""

    @app.route('/', methods=["GET", "POST"])
    def index():
        """Index page"""
        # Connection with DB
        db = get_db()
        # Creating a cursor for SQL-requests
        cursor = db.cursor()

        # Getting list of all departments from DB
        cursor.execute("SELECT ID, Abteilungsname FROM Abteilungen")
        departments = cursor.fetchall()

        sort_by = request.args.get('sort_by', 'ID')  # Default sort by 'ID'
        valid_sort_columns = ['ID', 'Abteilungsname', 'Ziel_Aussage', 'Bewertung', 'Bewertungskriterien', 'Aktueller_Kommentar', 'Datum', 'Aenderungsbenutzer']

        if sort_by not in valid_sort_columns:
            sort_by = 'ID'  # Fallback to default if the sort column is invalid

        if request.method == "GET":
            # Get data from database with table join (left) and sorting
            cursor.execute(f"""
                SELECT z.ID, a.Abteilungsname, z.Ziel_Aussage, z.Bewertung, z.Bewertungskriterien, 
                       z.Aktueller_Kommentar, z.Datum, z.Aenderungsbenutzer
                FROM Ziele z
                LEFT JOIN Abteilungen a ON z.Abteilung_ID = a.ID
                ORDER BY {sort_by}
            """)
            results = cursor.fetchall()
            cursor.close()
            return render_template('index.html.j2', results=results, departments=departments, sort_by=sort_by)

        elif request.method == "POST":
            # Extract data from form (user input)
            ziel_aussage = request.form.get('ziel_aussage')
            bewertung = request.form.get('bewertung')
            bewertungskriterien = request.form.get('bewertungskriterien')
            aktueller_kommentar = request.form.get('aktueller_kommentar')
            abteilungsname = request.form.get('abteilungsname')

            # Get Abteilung_ID by Abteilungsname
            cursor.execute('SELECT ID FROM Abteilungen WHERE Abteilungsname = %s', (abteilungsname,))
            result = cursor.fetchone()

            if result is None:
                cursor.close()
                return render_template('index.html.j2', results=[], departments=departments, message='Abteilungsname not found!', sort_by=sort_by)

            abteilung_id = result[0]  # Use index 0 to get the ID value

            # Add new records to the database
            current_date = datetime.now().strftime('%Y-%m-%d')
            user = "admin"  # should be setting for many users with creating a new table in DB "Users"

            try:
                cursor.execute('INSERT INTO Ziele (Abteilung_ID, Ziel_Aussage, Bewertung, Bewertungskriterien, Aktueller_Kommentar, Datum, Aenderungsbenutzer) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                               (abteilung_id, ziel_aussage, bewertung, bewertungskriterien, aktueller_kommentar, current_date, user))
                db.commit()
                message = 'New entry added successfully.'
            except Exception as e:
                db.rollback()
                print(f"Error: {e}")
                message = 'Failed to add new entry.'

            # Reload data and display
            cursor.execute(f"""
                SELECT z.ID, a.Abteilungsname, z.Ziel_Aussage, z.Bewertung, z.Bewertungskriterien, 
                       z.Aktueller_Kommentar, z.Datum, z.Aenderungsbenutzer
                FROM Ziele z
                LEFT JOIN Abteilungen a ON z.Abteilung_ID = a.ID
                ORDER BY {sort_by}
            """)
            results = cursor.fetchall()
            cursor.close()

            # Render the main page with message
            return render_template('index.html.j2', results=results, departments=departments, message=message, sort_by=sort_by)
