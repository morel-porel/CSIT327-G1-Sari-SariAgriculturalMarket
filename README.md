## Sari-Sari Agricultural Market Project 
Follow these steps to get your development environment set up and running.

**1. Clone the Repository**
```bash
git clone https://github.com/morel-porel/Sari-Sari-Agricultural-Market.git
cd sari-sari-agricultural-market
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
This command reads the `requirements.txt` file and installs all the necessary Python packages.
```bash
pip install -r requirements.txt
```

**4. Configure Environment Variables**
The project requires a `.env` file for secret keys and database credentials.
- ask devs for the file

**5. Apply Database Migrations**
This command will set up your database schema based on the project's models.
```bash
python manage.py migrate
```

**6. Create a Superuser (for Admin Access)**
This step is required to access the Django admin panel.
```bash
python manage.py createsuperuser
```
Follow the prompts. Note that the password will not be visible as you type.

**7. Run the Development Server**
```bash
python manage.py runserver
```
The application will be running at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

---

## How to Demo the User Authentication Feature

1.  Make sure the server is running.
2.  Open your browser and navigate to the **Sign Up page**: [http://127.0.0.1:8000/auth/signup/](http://127.0.0.1:8000/auth/signup/)
3.  Navigate to the **Login page**: [http://127.0.0.1:8000/auth/login/](http://127.0.0.1:8000/auth/login/)
4.  Navigate to the **Admin panel**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) and log in with your superuser credentials.
