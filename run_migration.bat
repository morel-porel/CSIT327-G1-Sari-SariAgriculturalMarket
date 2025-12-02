@echo off
cd /d "c:\Users\User\Documents\IM2 Sari-Sari\CSIT327-G1-Sari-SariAgriculturalMarket"
echo Running migrations for suspension system...
python manage.py makemigrations
python manage.py migrate
echo.
echo Migration complete!
echo.
echo The following suspension system has been implemented:
echo - 1st Suspension: 2 days
echo - 2nd Suspension: 1 week (+ role-specific penalties)
echo - 3rd Suspension: Permanent ban
echo.
pause

