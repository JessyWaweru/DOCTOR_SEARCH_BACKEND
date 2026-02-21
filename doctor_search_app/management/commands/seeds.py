import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from doctor_search_app.models import Doctor, Review
from django.utils.text import slugify

User = get_user_model()

class Command(BaseCommand):
    help = 'Load doctor data with images and conditional reviews'

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
        doctor_data = [
            # --- OLD DOCTORS (Default Image, Generate Reviews) ---
            {
                "name": "Koome Muratha", "specialty": "Cardiologist", "hospital": "Nairobi Cardiac Rehab Centre", 
                "location": "Nairobi", "cell": "2721580", "image": None, "generate_reviews": True
            },
            {
                "name": "Charles Kariuki", "specialty": "Cardiologist", "hospital": "Nairobi Hospital", 
                "location": "Nairobi", "cell": "2721609", "image": None, "generate_reviews": True
            },
            {
                "name": "Dr Philip Kisyoka", "specialty": "Cardiologist", "hospital": "Nairobi Hospital", 
                "location": "Nairobi", "cell": "0722964288", "image": None, "generate_reviews": True
            },
            {
                "name": "Dr Murithi Nyamu", "specialty": "Cardiologist", "hospital": "Nelson Awori", 
                "location": "Nairobi", "cell": "0722 433 130", "image": None, "generate_reviews": True
            },
            {
                "name": "William I Okumu", "specialty": "Cardiologist", "hospital": "Consolidated Bank Hse", 
                "location": "Nairobi", "cell": "0722 320146", "image": None, "generate_reviews": True
            },
            {
                "name": "J.M Chakava", "specialty": "Physician", "hospital": "The Mater Hospital", 
                "location": "Nairobi", "cell": "020-2252815", "image": None, "generate_reviews": True
            },
            {
                "name": "Paul Ngugi", "specialty": "Diabetologist", "hospital": "Hazina Towers", 
                "location": "Nairobi", "cell": "0722-726600", "image": None, "generate_reviews": True
            },
            {
                "name": "Kassim Goke", "specialty": "Physician", "hospital": "Upper Hill Medical Centre", 
                "location": "Nairobi", "cell": "020-3424832", "image": None, "generate_reviews": True
            },
            {
                "name": "R.M. Muraguri", "specialty": "Gastroenterologist", "hospital": "The Nairobi Hospital", 
                "location": "Nairobi", "cell": "020-2722302", "image": None, "generate_reviews": True
            },
            {
                "name": "S.M. Kairu", "specialty": "Gastroenterologist", "hospital": "Menelik Medical Centre", 
                "location": "Nairobi", "cell": "020-3877028", "image": None, "generate_reviews": True
            },
            {
                "name": "Prof Erastus O. Amayo", "specialty": "Neurologist", "hospital": "General Accident Hse", 
                "location": "Nairobi", "cell": "020-2722405", "image": None, "generate_reviews": True
            },
            {
                "name": "Dr Lucy Mutara", "specialty": "Dentist", "hospital": "Mpaka Plaza Westlands", 
                "location": "Nairobi", "cell": "0721502512", "image": None, "generate_reviews": True
            },
            {
                "name": "Dr Sanjna K.", "specialty": "Dentist", "hospital": "Nairobi CBD", 
                "location": "Nairobi", "cell": "0722252549", "image": None, "generate_reviews": True
            },
            {
                "name": "Dr Kasi Marani", "specialty": "Dentist", "hospital": "Hurlingham Medicare Plaza", 
                "location": "Nairobi", "cell": "2715239", "image": None, "generate_reviews": True
            },
            {
                "name": "Dr William Obwaka", "specialty": "Obs/Gyn", "hospital": "NSSF Building", 
                "location": "Nairobi", "cell": "0716473326", "image": None, "generate_reviews": True
            },
            {
                "name": "Dr James Kamau", "specialty": "Obs/Gyn", "hospital": "Exchange Building", 
                "location": "Nairobi", "cell": "020-310800", "image": None, "generate_reviews": True
            },
            {
                "name": "Eunice J Cheserem", "specialty": "Obs/Gyn", "hospital": "Nairobi Hospital Drs Plaza", 
                "location": "Nairobi", "cell": "020-2846434", "image": None, "generate_reviews": True
            },
            {
                "name": "Dr D M Kinuthia", "specialty": "Paediatrician", "hospital": "Aga Khan University Hospital", 
                "location": "Nairobi", "cell": "3740000", "image": None, "generate_reviews": True
            },
            {
                "name": "C.A Okello (Mrs)", "specialty": "Paediatrician", "hospital": "Hurlingham Medical Centre", 
                "location": "Nairobi", "cell": "020-2712852", "image": None, "generate_reviews": True
            },
            {
                "name": "Dr Anne Maina", "specialty": "ENT Surgeon", "hospital": "Optimum Medical Centre", 
                "location": "Nairobi", "cell": "0722 566 039", "image": None, "generate_reviews": True
            },
            {
                "name": "Dr Walter Otieno", "specialty": "Paediatrician", "hospital": "Drs. Plaza-Kisumu", 
                "location": "Kisumu", "cell": "0722144814", "image": None, "generate_reviews": True
            },
            {
                "name": "Dr Janet Oyieko", "specialty": "Paediatrician", "hospital": "Oasis Medical Centre", 
                "location": "Kisumu", "cell": "0721 99 69 88", "image": None, "generate_reviews": True
            },
            {
                "name": "Dr Leah Okin", "specialty": "Obs/Gyn", "hospital": "Oasis Medical Centre", 
                "location": "Kisumu", "cell": "0727 79 19 05", "image": None, "generate_reviews": True
            },
            {
                "name": "Satish Mangal Vaghela", "specialty": "Dentist", "hospital": "Nyali Dental Care", 
                "location": "Mombasa", "cell": "041-314953", "image": None, "generate_reviews": True
            },
            {
                "name": "Dr Salaah A.O", "specialty": "Dentist", "hospital": "TSS Towers", 
                "location": "Mombasa", "cell": "0733 39 39 39", "image": None, "generate_reviews": True
            },
            {
                "name": "Dr C.E Muyodi", "specialty": "Physician", "hospital": "Pandya Memorial Hospital", 
                "location": "Mombasa", "cell": "2230674", "image": None, "generate_reviews": True
            },
            {
                "name": "Dr F. Gikandi", "specialty": "Paediatrician", "hospital": "Aga Khan Hospital Mombasa", 
                "location": "Mombasa", "cell": "0722 684 176", "image": None, "generate_reviews": True
            },

            # --- NEW DOCTORS (Explicit Image, NO Reviews) ---
            {
                "name": "Dr. Dan K. Gikonyo", "specialty": "Adult Cardiologist", "hospital": "The Karen Hospital", 
                "location": "Nairobi", "cell": "0709 382 000", 
                "image": "https://karenhospital.org/wp-content/uploads/2020/09/Dr-Dan-Gikonyo.jpg", 
                "generate_reviews": False
            },
            {
                "name": "Dr. Francis Mbugua", "specialty": "Orthopaedic Surgeon", "hospital": "Private Practice", 
                "location": "Nairobi", "cell": "0791 399 103", 
                "image": "https://static.wixstatic.com/media/a9ff10_8b1116ea77d94f27b9cde5629c118ed3~mv2.jpg", 
                "generate_reviews": False
            },
            {
                "name": "Prof. Zahida Qureshi", "specialty": "Obstetrician & Gynaecologist", "hospital": "Upper Hill Medical Centre", 
                "location": "Nairobi", "cell": "0724 255 295", 
                "image": "https://randomuser.me/api/portraits/women/44.jpg", 
                "generate_reviews": False
            },
            {
                "name": "Dr. Hosea W. Waweru", "specialty": "Dermatologist", "hospital": "Upper Hill Medical Centre", 
                "location": "Nairobi", "cell": "0737 343 146", 
                "image": "https://randomuser.me/api/portraits/men/32.jpg", 
                "generate_reviews": False
            },
            {
                "name": "Dr. J.M. Chakaya", "specialty": "Chest Physician", "hospital": "Fortis Suites", 
                "location": "Nairobi", "cell": "0725 522 915", 
                "image": "https://randomuser.me/api/portraits/men/45.jpg", 
                "generate_reviews": False
            },
            {
                "name": "Dr. Sangeeta Chauhan", "specialty": "Endocrinologist", "hospital": "Aga Khan Doctors Plaza", 
                "location": "Nairobi", "cell": "0711 092 720", 
                "image": "https://randomuser.me/api/portraits/women/68.jpg", 
                "generate_reviews": False
            },
            {
                "name": "Dr. Smita Devani", "specialty": "Gastroenterologist", "hospital": "Aga Khan Doctors Plaza", 
                "location": "Nairobi", "cell": "0733 943 802", 
                "image": "https://randomuser.me/api/portraits/women/65.jpg", 
                "generate_reviews": False
            },
            {
                "name": "Dr. Bernard Samia", "specialty": "Consultant Physician and Cardiologist", "hospital": "MP Shah Hospital", 
                "location": "Nairobi", "cell": "020 429 1000", 
                "image": "https://randomuser.me/api/portraits/men/22.jpg", 
                "generate_reviews": False
            },
            {
                "name": "Dr. Shamsa Hussein Ahmed", "specialty": "Infectious Diseases Physician", "hospital": "MP Shah Hospital", 
                "location": "Nairobi", "cell": "020 429 1000", 
                "image": "https://mpshahhosp.org/wp-content/uploads/2025/01/dr-shamsa-ahmed.jpg", 
                "email": "info@mpshahhospital.org",
                "generate_reviews": False
            },
            {
                "name": "Dr. Charles Kabetu", "specialty": "Anaesthetist", "hospital": "Upper Hill Medical Centre", 
                "location": "Nairobi", "cell": "020 262 7156", 
                "image": None, 
                "generate_reviews": False
            }
        ]

        # 4. LOOP & CREATE
        # ---------------------------------------------------------
        # Standard grey silhouette placeholder (like WhatsApp)
        DEFAULT_AVATAR = "https://upload.wikimedia.org/wikipedia/commons/7/7c/Profile_avatar_placeholder_large.png"
        
        count = 0
        for doc in doctor_data:
            
            # 1. Determine Image
            final_image_url = doc.get("image")
            if not final_image_url:
                final_image_url = DEFAULT_AVATAR

            # 2. Create or Update Doctor
            doctor, created = Doctor.objects.get_or_create(
                name=doc["name"],
                defaults={
                    'specialty': doc["specialty"],
                    'hospital': doc["hospital"],
                    'location': doc["location"],
                    'cell': doc["cell"],
                    'email': doc.get('email', '-'),
                    'image': final_image_url
                }
            )
            
            # If doctor already existed, ensure the image is up to date
            if not created:
                doctor.image = final_image_url
                doctor.email = doc.get('email', '-')
                doctor.save()

            # 3. Handle Reviews
            if doc.get("generate_reviews", False):
                # Delete existing reviews to prevent duplicates piling up if run multiple times
                Review.objects.filter(doctor=doctor).delete()

                review_count = random.randint(4, 7)
                random.shuffle(users)
                
                for i in range(review_count):
                    user = users[i]
                    
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
            else:
                # Ensure the new doctors are swept clean of any accidental past reviews
                Review.objects.filter(doctor=doctor).delete()

            count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {count} doctors.'))