from django.core.management.base import BaseCommand
from doctor_search_app.models import Doctor
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Load doctor data from transcribed image data'

    def handle(self, *args, **kwargs):
        # Data structure: (Name, Specialty, Hospital/Address, Location, Contact)
        # Note: 'Location' is derived from the section headers in your images (Nairobi, Kisumu, etc.)
        
        doctor_data = [
            # --- NAIROBI (Start) ---
            # Cardiologists / Physicians
            ("Koome Muratha", "Cardiologist", "Nairobi Cardiac Rehab Centre, Landmark Plaza", "Nairobi", "2721580 / 2721543"),
            ("Charles Kariuki", "Cardiologist", "Nairobi Hospital", "Nairobi", "2721609 / 2721543"),
            ("Dr Philip Kisyoka", "Cardiologist", "Nairobi Hospital", "Nairobi", "27271337 / 0722964288"),
            ("Dr Murithi Nyamu", "Cardiologist", "Nelson Awori", "Nairobi", "0722 433 130"),
            ("William I Okumu", "Cardiologist", "Consolidated Bank Hse", "Nairobi", "0722 320146"),
            
            # Physicians / Chest / Gastro / etc
            ("J.M Chakava", "Physician", "The Mater Hospital", "Nairobi", "020-2252815"),
            ("Paul Ngugi", "Diabetologist", "Hazina Towers, 1st Floor", "Nairobi", "020-316571, 0722-726600"),
            ("Kassim Goke", "Physician", "Upper Hill Medical Centre", "Nairobi", "020-3424832"),
            ("R.M. Muraguri", "Gastroenterologist", "The Nairobi Hospital", "Nairobi", "020-2722302"),
            ("S.M. Kairu", "Gastroenterologist", "Menelik Medical Centre", "Nairobi", "020-3877028"),
            ("Prof Erastus O. Amayo", "Neurologist", "General Accident Hse", "Nairobi", "020-2722405"),
            
            # Dentists (Nairobi)
            ("Dr Lucy Mutara", "Dentist", "Mpaka Plaza 1st Floor, Westlands", "Nairobi", "0721502512"),
            ("Dr Sanjna K.", "Dentist", "Nairobi", "Nairobi", "0722252549"),
            ("Dr Kasi Marani", "Dentist", "Hurlingham Medicare Plaza", "Nairobi", "2715239"),
            ("MotherSmile Dental Care", "Dentist", "Junction of Ngong & Kinchwa Roads", "Nairobi", "0734741866"),
            
            # OBS/GYN (Nairobi)
            ("Dr William Obwaka", "Obs/Gyn", "NSSF Building Floor B1", "Nairobi", "0716473326"),
            ("Dr James Kamau", "Obs/Gyn", "Exchange Building 5th Floor", "Nairobi", "020-310800"),
            ("Dr Gichuhi", "Obs/Gyn", "KMA Centre", "Nairobi", "0722 861 914"),
            ("Dr Kavoo Linge", "Obs/Gyn", "Tumaini Hse Nrb", "Nairobi", "0722 522 085"),
            ("Eunice J Cheserem", "Obs/Gyn", "Nairobi Hospital Drs Plaza", "Nairobi", "020-2846434"),

            # Paediatricians (Nairobi)
            ("Dr D M Kinuthia", "Paediatrician", "Aga Khan University Hospital", "Nairobi", "3740000 ext 2221"),
            ("C.A Okello (Mrs)", "Paediatrician", "Hurlingham Medical Centre", "Nairobi", "020-2712852"),
            ("Dr Njuki", "Paediatrician", "Acacia Medical Centre", "Nairobi", "020-2722714"),
            
            # --- DOCTOR 2 IMAGE (ENT / Surgeons / Etc) ---
            # ENT (Nairobi)
            ("Peter M", "ENT Surgeon", "Hazina Towers 1st Floor", "Nairobi", "020-2434745"),
            ("Billy Mungai", "ENT Surgeon", "Consolidated Building 5th Flr", "Nairobi", "242831/242673"),
            ("Dr Anne Maina", "ENT Surgeon", "Optimum Medical Centre", "Nairobi", "0722 566 039"),
            ("Dr Maurice Podho", "ENT Surgeon", "Nakuru ENT Medical Centre", "Nakuru", "051-2215953"), # Note: Nakuru address in Nrb list? I will label based on location if explicit.
            
            # Surgeons (Nairobi)
            ("Dr Joab Bodo", "Orthopaedic Surgeon", "Aga Khan University Hospital", "Nairobi", "375 1087"),
            ("Dr Choutkin", "Orthopaedic Surgeon", "5th Avenue Suites, 7th Floor", "Nairobi", "2713838"),
            ("M.R Khan", "Surgeon", "Nairobi Hospital", "Nairobi", "2713935"),
            ("Dr John K N", "General Surgeon", "Nairobi Hospital", "Nairobi", "202-2720726"),
            ("Edwin K Rono", "Craniofacial Surgeon", "M.P Shah Hospital", "Nairobi", "0720-456773"),

            # Ophthalmologists
            ("Prof Saida", "Ophthalmologist", "Yaya Centre", "Nairobi", "562525"),
            ("Ravji H.", "Ophthalmologist", "Utalii Hse 1st Floor", "Nairobi", "020-218585"),
            
            # Rheumatologist
            ("Dr Omondi Oyoo", "Rheumatologist", "Fortis Granite House", "Nairobi", "2724044"),
            ("Dr Bernard Owing", "Rheumatologist", "Aga Khan University Hospital", "Nairobi", "0728 820 209"),

            # Psychiatrists
            ("Marx M.O Okonji", "Psychiatrist", "Nairobi Hospital", "Nairobi", "3743012"),
            ("Margaret Mak", "Psychiatrist", "Fort Granite Suite B4", "Nairobi", "0722829599"),
            
            # --- KISUMU (Start) ---
            ("Dr Walter Otieno", "Paediatrician", "Drs. Plaza-Kisumu", "Kisumu", "0722144814"),
            ("Dr Dedan Ongong'a", "Paediatrician", "Oasis Medical Centre", "Kisumu", "0721418415"),
            ("Dr Janet Oyieko", "Paediatrician", "Oasis Medical Centre", "Kisumu", "0721 99 69 88"),
            
            # --- DOCTOR 3 IMAGE (Kisumu / Mombasa / Others) ---
            # Kisumu Continued
            ("Dr James Wagude", "Paediatrician", "Oasis Medical Centre", "Kisumu", "0733 78 00 16"),
            ("Dr Willis Ovieko", "Urologist", "Oasis Medical Centre", "Kisumu", "0720299505"),
            ("Dr Charles Nyakinda", "Surgeon", "Oasis Medical Centre", "Kisumu", "0722 53 79 14"),
            ("Dr F.A Otieno", "Surgeon", "Drs Plaza-Kisumu", "Kisumu", "0722 30 12 12"),
            ("Dr Leah Okin", "Obs/Gyn", "Oasis Medical Centre", "Kisumu", "0727 79 19 05"),
            ("Dr Michael Owili", "Physician", "Kisumu", "Kisumu", "0722 47 69 83"),
            ("Dr David Odeny", "ENT", "Intermedicons Kisumu", "Kisumu", "057-2021202"),
            
            # Mombasa
            ("Satish Mangal Vaghela", "Dentist", "Nyali Dental Care", "Mombasa", "041-314953"),
            ("Dr Salaah A.O", "Dentist", "TSS Towers 1st Flr", "Mombasa", "0733 39 39 39"),
            ("Dr Karume", "Obs/Gyn", "Mombasa", "Mombasa", "0733 516 321"),
            ("N.D Mnjalla", "Ophthalmologist", "Aga Khan Hospital Mombasa", "Mombasa", "041-2228067"),
            ("Dr C.E Muyodi", "Physician", "Pandya Memorial Hospital", "Mombasa", "2230674"),
            ("Dr F. Gikandi", "Paediatrician", "Aga Khan Hospital Mombasa", "Mombasa", "0722 684 176"),
            ("Dr J.M Muthuri", "Surgeon", "Mombasa Hospital Clinics", "Mombasa", "041-2224105"),
            
            # Kakamega
            ("Hezron W Odongo", "Paediatrician", "Canon Awori St", "Kakamega", "056 30547"),
            ("N.M. Wambugu", "Dentist", "Boflo Building 1st Floor", "Kakamega", "0733 606 327"),
            
            # Nakuru
            ("Dr Norman K Njogu", "Obs/Gyn", "Prime Care Medical Centre", "Nakuru", "N/A"),
            ("Dr Naresh Sarna", "Dentist", "Arcade House", "Nakuru", "0733 711 032"),
            
            # Thika
            ("J.K Mwangi", "Dentist", "Thika Dental Care", "Thika", "067-22276"),
            ("Dr J.K Thuo", "Physician", "Jogoo Building", "Thika", "067-22440"),
        ]

        self.stdout.write("Starting data seeding...")

        count = 0
        for name, specialty, hospital, location, cell in doctor_data:
            # Create a dummy email based on name
            dummy_email = f"{slugify(name)}@example.com"
            
            # Check if doctor exists to avoid duplicates
            if not Doctor.objects.filter(name=name, hospital=hospital).exists():
                Doctor.objects.create(
                    name=name,
                    specialty=specialty,
                    hospital=hospital,
                    location=location,
                    cell=cell,
                    email=dummy_email
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully added {count} doctors to the database.'))