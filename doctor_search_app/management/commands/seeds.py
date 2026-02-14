import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from doctor_search_app.models import Doctor, Review
from django.utils.text import slugify

User = get_user_model()

class Command(BaseCommand):
    help = 'Load doctor data with images and reviews'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting database seeding...")

        # 1. CREATE DUMMY USERS (To write the reviews)
        # ---------------------------------------------------------
        dummy_names = [
            "Wanjiku", "Otieno", "Kamau", "Achieng", "Odhiambo", "Nyambura", "Ochieng", 
            "Njoroge", "Mwangi", "Chebet", "Kipkorir", "Adhiambo", "Wambui", "Maina", 
            "Kariuki", "Mutua", "Omondi", "Anyango", "Juma", "Njeri"
        ]
        
        users = []
        for name in dummy_names:
            username = f"{name.lower()}{random.randint(1, 99)}"
            email = f"{username}@example.com"
            user, created = User.objects.get_or_create(username=username, email=email)
            if created:
                user.set_password("password123")
                user.save()
            users.append(user)
        
        self.stdout.write(f"Created/Loaded {len(users)} dummy users.")


        # 2. REVIEW COMMENTS BANK
        # ---------------------------------------------------------
        good_reviews = [
            "Excellent service, very professional.",
            "Saved my life! Best doctor in the region.",
            "Very kind and took time to explain everything.",
            "Great facility and friendly staff.",
            "Highly recommended for anyone with similar issues.",
            "The treatment worked wonders. Thank you daktari.",
            "Very knowledgeable and precise.",
            "Wait time was short and the service was top notch."
        ]
        
        avg_reviews = [
            "Good doctor but the queue was too long.",
            "Service was okay, but the receptionist was rude.",
            "Decent experience, but a bit expensive.",
            "Treatment was effective but follow-up was slow.",
            "Average experience. Nothing special."
        ]
        
        bad_reviews = [
            "Kept me waiting for 3 hours!",
            "Did not listen to my concerns at all.",
            "Very expensive for the level of service provided.",
            "Rushed through the consultation.",
            "I would not recommend this clinic.",
            "Very unprofessional staff."
        ]

        # 3. DOCTOR DATA
        # ---------------------------------------------------------
        # (Name, Specialty, Hospital, Location, Contact, GenderGuess)
        # Gender 'm' or 'f' helps us pick the right photo folder
        doctor_data = [
            ("Koome Muratha", "Cardiologist", "Nairobi Cardiac Rehab Centre", "Nairobi", "2721580", "m"),
            ("Charles Kariuki", "Cardiologist", "Nairobi Hospital", "Nairobi", "2721609", "m"),
            ("Dr Philip Kisyoka", "Cardiologist", "Nairobi Hospital", "Nairobi", "0722964288", "m"),
            ("Dr Murithi Nyamu", "Cardiologist", "Nelson Awori", "Nairobi", "0722 433 130", "m"),
            ("William I Okumu", "Cardiologist", "Consolidated Bank Hse", "Nairobi", "0722 320146", "m"),
            
            ("J.M Chakava", "Physician", "The Mater Hospital", "Nairobi", "020-2252815", "m"),
            ("Paul Ngugi", "Diabetologist", "Hazina Towers", "Nairobi", "0722-726600", "m"),
            ("Kassim Goke", "Physician", "Upper Hill Medical Centre", "Nairobi", "020-3424832", "m"),
            ("R.M. Muraguri", "Gastroenterologist", "The Nairobi Hospital", "Nairobi", "020-2722302", "m"),
            ("S.M. Kairu", "Gastroenterologist", "Menelik Medical Centre", "Nairobi", "020-3877028", "m"),
            ("Prof Erastus O. Amayo", "Neurologist", "General Accident Hse", "Nairobi", "020-2722405", "m"),
            
            ("Dr Lucy Mutara", "Dentist", "Mpaka Plaza Westlands", "Nairobi", "0721502512", "f"),
            ("Dr Sanjna K.", "Dentist", "Nairobi CBD", "Nairobi", "0722252549", "f"),
            ("Dr Kasi Marani", "Dentist", "Hurlingham Medicare Plaza", "Nairobi", "2715239", "f"),
            ("Dr William Obwaka", "Obs/Gyn", "NSSF Building", "Nairobi", "0716473326", "m"),
            ("Dr James Kamau", "Obs/Gyn", "Exchange Building", "Nairobi", "020-310800", "m"),
            ("Eunice J Cheserem", "Obs/Gyn", "Nairobi Hospital Drs Plaza", "Nairobi", "020-2846434", "f"),

            ("Dr D M Kinuthia", "Paediatrician", "Aga Khan University Hospital", "Nairobi", "3740000", "m"),
            ("C.A Okello (Mrs)", "Paediatrician", "Hurlingham Medical Centre", "Nairobi", "020-2712852", "f"),
            ("Dr Anne Maina", "ENT Surgeon", "Optimum Medical Centre", "Nairobi", "0722 566 039", "f"),
            
            ("Dr Walter Otieno", "Paediatrician", "Drs. Plaza-Kisumu", "Kisumu", "0722144814", "m"),
            ("Dr Janet Oyieko", "Paediatrician", "Oasis Medical Centre", "Kisumu", "0721 99 69 88", "f"),
            ("Dr Leah Okin", "Obs/Gyn", "Oasis Medical Centre", "Kisumu", "0727 79 19 05", "f"),
            
            ("Satish Mangal Vaghela", "Dentist", "Nyali Dental Care", "Mombasa", "041-314953", "m"),
            ("Dr Salaah A.O", "Dentist", "TSS Towers", "Mombasa", "0733 39 39 39", "m"),
            ("Dr C.E Muyodi", "Physician", "Pandya Memorial Hospital", "Mombasa", "2230674", "m"),
            ("Dr F. Gikandi", "Paediatrician", "Aga Khan Hospital Mombasa", "Mombasa", "0722 684 176", "f"),
        ]

        # 4. LOOP & CREATE
        # ---------------------------------------------------------
        count = 0
        for name, specialty, hospital, location, cell, gender in doctor_data:
            
            # Generate Image URL
            # We use randomuser.me IDs. 
            # Men IDs: 1-99, Women IDs: 1-99.
            # We use the name length as a seed to keep the image consistent for the same name every time we run seeds.
            img_id = (len(name) * 3) % 99 
            if img_id == 0: img_id = 1
            
            gender_path = "men" if gender == "m" else "women"
            image_url = f"https://randomuser.me/api/portraits/{gender_path}/{img_id}.jpg"

            # Create Doctor
            doctor, created = Doctor.objects.get_or_create(
                name=name,
                defaults={
                    'specialty': specialty,
                    'hospital': hospital,
                    'location': location,
                    'cell': cell,
                    'email': f"{slugify(name)}@example.com",
                    'image': image_url
                }
            )
            
            # If doctor already existed, update the image just in case
            if not created:
                doctor.image = image_url
                doctor.save()

            # Create 4 to 7 Reviews
            review_count = random.randint(4, 7)
            # Shuffle users to get random reviewers
            random.shuffle(users)
            
            # Delete existing reviews to prevent duplicates piling up if we run seeds twice
            Review.objects.filter(doctor=doctor).delete()

            for i in range(review_count):
                user = users[i]
                
                # Weighted Randomness: Doctors mostly get good reviews, some bad
                # 70% Good, 20% Avg, 10% Bad
                rand_val = random.random()
                if rand_val < 0.7:
                    rating = random.randint(8, 10)
                    comment = random.choice(good_reviews)
                elif rand_val < 0.9:
                    rating = random.randint(5, 7)
                    comment = random.choice(avg_reviews)
                else:
                    rating = random.randint(1, 4)
                    comment = random.choice(bad_reviews)
                
                Review.objects.create(
                    doctor=doctor,
                    user=user,
                    rating=rating,
                    comment=comment
                )

            count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {count} doctors with images and reviews.'))