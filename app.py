
from flask import Flask, render_template, request
import csv
import os
from urllib.parse import quote_plus

app = Flask(__name__)

# Read hospital data from CSV file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "hospitals.csv")


def load_hospitals():
    hospitals = []

    with open(CSV_FILE, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            hospitals.append(row)

    return hospitals


# Demo emergency classification
def classify_emergency(breathing, unconscious, bleeding):

    if breathing or unconscious or bleeding:
        return "Critical"

    return "Non-Critical (Demo Only)"


# Find required medical speciality using keywords
def find_specialty(symptoms):

    symptoms = symptoms.lower()

    if any(word in symptoms for word in
           ["heart", "chest pain", "cardiac"]):
        return "Cardiology"

    elif any(word in symptoms for word in
             ["accident", "injury", "trauma", "fracture"]):
        return "Trauma"

    else:
        return "General Medicine"


# Calculate a simple demo recommendation score
def calculate_score(hospital, specialty):

    score = 0

    if hospital["specialty"].lower() == specialty.lower():
        score += 50

    beds = int(hospital["beds"])
    icu = int(hospital["icu"])

    score += min(beds, 10) * 2
    score += min(icu, 5) * 2

    if hospital["ambulance"].lower() == "yes":
        score += 10

    return score


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/find-hospital", methods=["POST"])
def find_hospital():

    # Get information from HTML form
    name = request.form.get("name", "")
    location = request.form.get("location", "")
    age = request.form.get("age", "")
    symptoms = request.form.get("symptoms", "")

    breathing = request.form.get("breathing") == "yes"
    unconscious = request.form.get("unconscious") == "yes"
    bleeding = request.form.get("bleeding") == "yes"

    # Classify demo emergency priority
    severity = classify_emergency(
        breathing, unconscious, bleeding
    )

    # Find required speciality
    specialty = find_specialty(symptoms)

    # Load hospital records
    all_hospitals = load_hospitals()

    # Select hospitals with sample beds and emergency service
    available_hospitals = []

    for hospital in all_hospitals:

        if (hospital["emergency"].lower() == "yes"
                and int(hospital["beds"]) > 0):

            hospital["score"] = calculate_score(
                hospital, specialty
            )

            # Create Google Maps directions link
            destination = quote_plus(hospital["name"] + ", " +
                                     hospital["address"])
            origin = quote_plus(location)

            hospital["map_link"] = (
                "https://www.google.com/maps/dir/?api=1"
                + "&origin=" + origin
                + "&destination=" + destination
            )

            available_hospitals.append(hospital)

    # Show highest scoring hospitals first
    available_hospitals.sort(
        key=lambda hospital: hospital["score"],
        reverse=True
    )

    return render_template(
        "result.html",
        name=name,
        location=location,
        age=age,
        symptoms=symptoms,
        severity=severity,
        specialty=specialty,
        hospitals=available_hospitals
    )


if __name__ == "__main__":
    app.run(debug=True)
