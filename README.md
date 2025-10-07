# Sari-Sari: Agricultural Market

Sari-Sari is a web-based marketplace designed to connect small-scale agricultural vendors directly with consumers in Cebu City. The platform promotes transparent pricing, seasonal tracking, and direct communication, empowering local farmers and providing consumers with fresh, trusted produce.

---

### Tech Stack Used

*   **Backend:** Python with the Django Framework
*   **Database:** PostgreSQL (hosted on Supabase)
*   **Frontend:** HTML5, CSS3
*   **Version Control:** Git & GitHub

---

### Setup & Run Instructions


**1. Clone the Repository**
```bash
git clone https://github.com/morel-porel/CSIT327-G1-Sari-SariAgriculturalMarket.git
cd Sari-Sari-Agricultural-Market
```

**2. Create and Activate a Virtual Environment**
```bash
# For Windows
python -m venv env
env\Scripts\activate

# For macOS/Linux
python3 -m venv env
source env/bin/activate
```

**3. Install Dependencies**
This command installs all the necessary Python packages.
```bash
pip install -r requirements.txt
```

**4. Apply Database Migrations**
This command will set up the database schema. The project is configured to use the .env file provided by the team.
```bash
python manage.py migrate
```

**5. Create a Superuser (for Admin Access)**
This step is required to access the Django admin panel at /admin/.
```bash
python manage.py createsuperuser
```

**6. Run the Development Server**
```bash
python manage.py runserver
```

The application will be running at http://122.0.0.1:8000/.

---

Team Members
Name	Role	CIT-U Email
Ramirez, Ruther Gerald L. | Lead Developer | ruthergerard.ramirez@cit.edu
Pacio, Muriel D. | Developer | muriel.pacio@cit.edu
Orat, Crisorlann Jon S. | Developer | crisorlannjon.orat@cit.edu	
Pescante, Merven Loui A. | Product Owner | mervenloui.pescante@cit.edu
Poliquit Keint Warren J. | Business Analyst | keintwarren.poliquit@cit.edu
Pancho, Allan Krsna B. | Scrum Master | allankrsna.pancho@cit.edu			
							
							
							
							
							
							
							
