import os
import sys

# Change to project directory
os.chdir(r"C:\Users\User\Documents\IM2 Sari-Sari\CSIT327-G1-Sari-SariAgriculturalMarket")

# Run makemigrations
print("=" * 60)
print("Creating migrations...")
print("=" * 60)
os.system("python manage.py makemigrations")

print("\n" + "=" * 60)
print("Applying migrations to database...")
print("=" * 60)
os.system("python manage.py migrate")

print("\n" + "=" * 60)
print("MIGRATION COMPLETE!")
print("=" * 60)
print("\nThe suspension system is now active:")
print("- 1st Suspension: 2 days")
print("- 2nd Suspension: 1 week (+ penalties)")
print("- 3rd Suspension: Permanent ban")
print("\nYou can now restart your Django server.")
print("=" * 60)

input("\nPress Enter to close...")
