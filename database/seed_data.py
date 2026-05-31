import sqlite3
import os
from schema import create_database, DB_PATH

def seed_all():
    create_database()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ─── CONTRACTORS ────────────────────────────────────────────────────────
    contractors = [
        ("Ashoka Buildcon Ltd",      "ABL/MCA/2001/NH",  "Maharashtra", 23, 847,  156, 89,  12, 34, 4,  5.4, "Poor"),
        ("L&T Construction",         "LTC/MCA/1999/NH",  "Tamil Nadu",  41, 2340, 89,  82,  3,  6,  1,  8.2, "Good"),
        ("IRB Infrastructure",       "IRB/MCA/2004/NH",  "Maharashtra", 18, 1120, 104, 78,  6,  12, 2,  7.1, "Good"),
        ("GR Infraprojects",         "GRI/MCA/2006/RJ",  "Rajasthan",   29, 1560, 132, 98,  7,  18, 3,  6.8, "Average"),
        ("HG Infra Engineering",     "HGI/MCA/2008/RJ",  "Rajasthan",   22, 980,  78,  68,  4,  9,  1,  7.5, "Good"),
        ("PNC Infratech",            "PNC/MCA/2003/UP",  "Uttar Pradesh",31, 1890, 145, 101, 9,  22, 5,  6.2, "Average"),
        ("Dilip Buildcon Ltd",       "DBL/MCA/2005/MP",  "Madhya Pradesh",27,1340, 167, 112, 11, 28, 6,  5.8, "Average"),
        ("KCC Buildtech",            "KCC/MCA/2010/DL",  "Delhi",       12, 340,  198, 89,  18, 41, 9,  4.1, "Poor"),
        ("APCO Infratech",           "APC/MCA/2007/AP",  "Andhra Pradesh",19,890, 91,  72,  5,  11, 2,  6.5, "Average"),
        ("J Kumar Infraprojects",    "JKI/MCA/2002/MH",  "Maharashtra", 24, 1120, 87,  72,  4,  10, 2,  7.0, "Good"),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO contractors
        (name,registration_number,headquarters_state,total_roads_count,total_length_km,
         complaints_received,complaints_resolved,dlp_violations,repeat_failures,
         budget_overruns,accountability_score,grade)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, contractors)
    print("✅ Contractors seeded")

    # ─── AUTHORITIES ────────────────────────────────────────────────────────
    authorities = [
        # NH → NHAI
        ("NH","NHAI Regional Office Bhopal",    "NHAI","Madhya Pradesh","Bhopal",    "Rajesh Kumar Sharma","Executive Engineer","ee-bhopal@nhai.org",    "0755-2661234","NHAI RO, Arera Colony, Bhopal - 462016",       14),
        ("NH","NHAI Regional Office Mumbai",    "NHAI","Maharashtra",   "Mumbai",    "Priya Desai",        "Executive Engineer","ee-mumbai@nhai.org",    "022-26591234","NHAI RO, BKC, Mumbai - 400051",                14),
        ("NH","NHAI Regional Office Delhi",     "NHAI","Delhi",         "New Delhi", "Amit Singh",         "Executive Engineer","ee-delhi@nhai.org",     "011-25074100","NHAI HQ, Dwarka, New Delhi - 110075",          14),
        ("NH","NHAI Regional Office Chennai",   "NHAI","Tamil Nadu",    "Chennai",   "S. Venkataraman",    "Executive Engineer","ee-chennai@nhai.org",   "044-28271234","NHAI RO, Anna Salai, Chennai - 600002",        14),
        ("NH","NHAI Regional Office Jaipur",    "NHAI","Rajasthan",     "Jaipur",    "Deepak Meena",       "Executive Engineer","ee-jaipur@nhai.org",    "0141-2741234","NHAI RO, JLN Marg, Jaipur - 302017",          14),
        # SH → State PWD
        ("SH","MP State PWD Bhopal",            "State PWD","Madhya Pradesh","Bhopal","Suresh Patel",      "Executive Engineer","ee-pwd-mp@mp.gov.in",   "0755-2441234","PWD Office, Arera Hills, Bhopal - 462011",    21),
        ("SH","Maharashtra PWD Mumbai",         "State PWD","Maharashtra",   "Mumbai","Anjali Patil",      "Executive Engineer","ee-pwd-mh@maharashtra.gov.in","022-22024000","PWD Mantralaya, Mumbai - 400032",      21),
        ("SH","UP PWD Lucknow",                 "State PWD","Uttar Pradesh", "Lucknow","Ram Prasad Yadav", "Executive Engineer","ee-pwd-up@up.gov.in",   "0522-2237100","PWD Office, Hazratganj, Lucknow - 226001",    21),
        ("SH","Rajasthan PWD Jaipur",           "State PWD","Rajasthan",     "Jaipur", "Kavita Sharma",    "Executive Engineer","ee-pwd-rj@rajasthan.gov.in","0141-2227481","PWD Office, Jacob Road, Jaipur - 302006", 21),
        ("SH","Tamil Nadu PWD Chennai",         "State PWD","Tamil Nadu",    "Chennai","P. Murugesan",     "Executive Engineer","ee-pwd-tn@tn.gov.in",   "044-28521234","PWD Office, Chepauk, Chennai - 600005",       21),
        # MDR/Village → PMGSY PIU
        ("MDR","PMGSY PIU Sehore MP",           "PMGSY PIU","Madhya Pradesh","Sehore","Mohan Tiwari",      "Programme Officer","po-pmgsy-sehore@mp.gov.in","07562-224100","PMGSY PIU, Collector Office, Sehore - 466001",30),
        ("Village","PMGSY PIU Pune District",   "PMGSY PIU","Maharashtra",  "Pune",   "Sneha Kulkarni",    "Programme Officer","po-pmgsy-pune@maharashtra.gov.in","020-26123000","PMGSY PIU, ZP Office, Pune - 411001",  30),
        ("Village","PMGSY PIU Ajmer Rajasthan", "PMGSY PIU","Rajasthan",    "Ajmer",  "Vikram Singh",      "Programme Officer","po-pmgsy-ajmer@rajasthan.gov.in","0145-2627100","PMGSY PIU, Collectorate, Ajmer - 305001",30),
        # Urban → Municipal Corporation
        ("Urban","Bhopal Municipal Corporation","Municipal Corporation","Madhya Pradesh","Bhopal","Ravi Verma","City Engineer","roads@bmcbhopal.in","0755-2700100","BMC Head Office, TT Nagar, Bhopal - 462003",  15),
        ("Urban","Pune Municipal Corporation",  "Municipal Corporation","Maharashtra",  "Pune", "Neha Joshi","City Engineer","roads@punecorporation.org","020-25501000","PMC Main Building, Shivajinagar, Pune - 411005",15),
        ("Urban","Jaipur Municipal Corporation","Municipal Corporation","Rajasthan",    "Jaipur","Arun Gupta","City Engineer","roads@jmcjaipur.in","0141-2740200","JMC Office, Lal Kothi, Jaipur - 302015",       15),
        # International
        ("NH","National Highways Authority UK", "International","United Kingdom","London","Operations Team","Highways England","info@nationalhighways.co.uk","+44-300-123-5000","National Highways, Bridge House, Guildford",14),
        ("NH","Federal Highway Administration US","International","United States","Washington DC","Operations Team","FHWA","fhwa.info@dot.gov","+1-202-366-0660","FHWA, 1200 New Jersey Ave SE, Washington DC",  30),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO authorities
        (road_type,authority_name,authority_type,state,district,engineer_name,
         designation,email,phone,office_address,complaint_sla_days)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, authorities)
    print("✅ Authorities seeded")

    # ─── ROADS ──────────────────────────────────────────────────────────────
    roads = [
        # National Highways
        ("NH-44 Delhi-Chennai (MP Stretch)",       "NH","Madhya Pradesh","Bhopal",
         23.2599, 77.4126, 22.7196, 75.8577, 312.0,
         1,"2019-03-15","2023-08-20","2024-03-15",
         485.50, 481.20, 99.1,
         "Central Road Fund","CAG Report 2024, Pg 112",
         6, 47, 1),

        ("NH-46 Bhopal-Vidisha",                   "NH","Madhya Pradesh","Vidisha",
         23.2599, 77.4126, 23.5251, 77.8082, 62.0,
         1,"2018-06-10","2023-03-12","2023-06-10",
         42.30, 41.80, 98.8,
         "Central Road Fund","CAG Report 2025, Pg 47",
         5, 23, 1),

        ("NH-48 Delhi-Mumbai (Pune Stretch)",       "NH","Maharashtra","Pune",
         18.5204, 73.8567, 17.6868, 73.7770, 180.0,
         2,"2020-11-01","2024-01-15","2025-11-01",
         320.00, 298.50, 93.3,
         "NHAI Toll","NHAI Project Report NH48-2020",
         8, 12, 2),

        ("NH-19 Agra-Lucknow Expressway",          "NH","Uttar Pradesh","Agra",
         27.1767, 78.0081, 26.8467, 80.9462, 302.0,
         6,"2021-04-20","2024-06-10","2026-04-20",
         1240.00,1198.00, 96.6,
         "NHAI Toll","NHAI Project Report NH19-2021",
         7, 8,  3),

        ("NH-52 Jaipur-Bikaner",                   "NH","Rajasthan","Jaipur",
         26.9124, 75.7873, 28.0229, 73.3119, 330.0,
         4,"2019-09-05","2022-11-30","2024-09-05",
         290.00, 289.10, 99.7,
         "Central Road Fund","CAG Report 2023, Pg 78",
         5, 31, 5),

        # State Highways
        ("SH-18 Bhopal-Hoshangabad",               "SH","Madhya Pradesh","Hoshangabad",
         23.2599, 77.4126, 22.7568, 77.7337, 78.0,
         7,"2017-07-22","2022-05-14","2020-07-22",
         38.40, 38.10, 99.2,
         "State Budget","MP PWD Annual Report 2022",
         4, 18, 6),

        ("SH-4 Pune-Nashik",                       "SH","Maharashtra","Nashik",
         18.5204, 73.8567, 19.9975, 73.7898, 212.0,
         3,"2018-12-01","2023-09-20","2021-12-01",
         124.00, 121.50, 98.0,
         "State Budget","Maharashtra PWD Report 2023",
         6, 14, 7),

        ("SH-25 Jaipur-Ajmer",                     "SH","Rajasthan","Ajmer",
         26.9124, 75.7873, 26.4499, 74.6399, 132.0,
         4,"2019-03-10","2023-07-05","2022-03-10",
         67.80, 66.90, 98.7,
         "NABARD","NABARD Rural Infra Fund Report 2023",
         5, 21, 9),

        ("SH-39 Lucknow-Kanpur",                   "SH","Uttar Pradesh","Kanpur",
         26.8467, 80.9462, 26.4499, 80.3319, 87.0,
         6,"2020-08-15","2024-02-28","2023-08-15",
         54.20, 53.80, 99.3,
         "State Budget","UP PWD Report 2024",
         6, 9,  8),

        ("SH-49 Chennai-Vellore",                  "SH","Tamil Nadu","Vellore",
         13.0827, 80.2707, 12.9165, 79.1325, 145.0,
         2,"2021-01-20","2024-04-10","2024-01-20",
         89.50, 84.20, 94.1,
         "State Budget","TN PWD Annual Report 2024",
         7, 7,  10),

        # PMGSY Rural Roads
        ("PMGSY Sehore-Nasrullaganj Rural Link",   "Village","Madhya Pradesh","Sehore",
         23.2019, 77.0857, 23.1234, 76.9876, 14.2,
         7,"2020-02-14","2022-08-20","2023-02-14",
         1.84,  1.82,  98.9,
         "PMGSY","PMGSY OMMAS ID: MP-SEH-2020-4821",
         3, 4,  11),

        ("PMGSY Pune District Village Road",       "Village","Maharashtra","Pune",
         18.4088, 73.8543, 18.3912, 73.8211, 8.6,
         3,"2021-06-01","2023-11-15","2024-06-01",
         0.98,  0.95,  96.9,
         "PMGSY","PMGSY OMMAS ID: MH-PUN-2021-3312",
         4, 2,  12),

        ("PMGSY Ajmer District Gram Sadak",        "Village","Rajasthan","Ajmer",
         26.3915, 74.5623, 26.3712, 74.5401, 6.4,
         4,"2019-11-20","2022-03-10","2022-11-20",
         0.72,  0.71,  98.6,
         "PMGSY","PMGSY OMMAS ID: RJ-AJM-2019-1987",
         3, 3,  13),

        # Urban Roads
        ("TT Nagar Road Bhopal",                   "Urban","Madhya Pradesh","Bhopal",
         23.2320, 77.4020, 23.2280, 77.4090, 2.4,
         7,"2021-03-10","2023-12-05","2024-03-10",
         3.20,  3.18,  99.4,
         "Municipal Fund","BMC Budget Report 2023-24",
         4, 6,  14),

        ("FC Road Pune",                           "Urban","Maharashtra","Pune",
         18.5195, 73.8468, 18.5080, 73.8350, 3.1,
         3,"2022-01-15","2024-03-20","2025-01-15",
         4.80,  4.65,  96.9,
         "Municipal Fund","PMC Budget Report 2023-24",
         7, 3,  15),

        ("MI Road Jaipur",                         "Urban","Rajasthan","Jaipur",
         26.9195, 75.8006, 26.9080, 75.7876, 4.2,
         4,"2020-09-12","2023-10-18","2023-09-12",
         6.40,  6.38,  99.7,
         "Municipal Fund","JMC Budget Report 2023-24",
         5, 8,  16),

        # Global Roads
        ("A1 London-Edinburgh",                    "NH","United Kingdom","London",
         51.5074, -0.1278, 55.9533, -3.1883, 650.0,
         None,"2015-04-01","2023-06-15",None,
         0.0, 0.0, 0.0,
         "UK Government","Highways England Annual Report 2023",
         8, 0,  17),

        ("I-95 East Coast USA",                    "NH","United States","New York",
         40.7128, -74.0060, 25.7617, -80.1918, 2940.0,
         None,"2010-01-01","2022-09-10",None,
         0.0, 0.0, 0.0,
         "Federal Highway Fund","FHWA Annual Report 2022",
         7, 0,  18),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO roads
        (name,road_type,state,district,start_lat,start_lon,end_lat,end_lon,
         length_km,contractor_id,construction_date,last_repair_date,dlp_expiry_date,
         budget_sanctioned_cr,budget_spent_cr,budget_utilization_pct,
         funding_source,source_document,condition_score,accident_count_last3yr,authority_id)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, roads)
    print("✅ Roads seeded")

    # ─── GLOBAL ROADS ───────────────────────────────────────────────────────
    global_roads = [
        ("United Kingdom","A1 Great North Road","Motorway","National Highways England",
         "+44-300-123-5000","https://www.nationalhighways.co.uk/contact-us/",
         "National Highways Annual Report 2023"),
        ("United States","I-95 Interstate","Interstate Highway","Federal Highway Administration",
         "+1-202-366-0660","https://www.fhwa.dot.gov/contact/",
         "FHWA Annual Report 2022"),
        ("Germany","A9 Berlin-Munich","Autobahn","Autobahn GmbH",
         "+49-30-18425-0","https://www.autobahn.de/en/contact",
         "Autobahn GmbH Report 2023"),
        ("Australia","M1 Pacific Motorway","Motorway","Transport for NSW",
         "+61-2-8202-2200","https://www.transport.nsw.gov.au/contact-us",
         "Transport NSW Annual Report 2023"),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO global_roads
        (country,road_name,road_type,authority_name,authority_contact,
         complaint_portal_url,data_source)
        VALUES (?,?,?,?,?,?,?)
    """, global_roads)
    print("✅ Global roads seeded")

    # ─── SAMPLE COMPLAINTS ──────────────────────────────────────────────────
    complaints = [
        ("SW-2024-BPL-0001", 2, "Pothole",          "High",
         "Large pothole 2ft wide near km 34",
         23.3812, 77.5890, None, "2024-11-10 09:23:00", None,
         "Resolved", 1, "2024-11-28 14:00:00", "Patched by contractor"),

        ("SW-2025-BPL-0021", 2, "Pothole",          "Critical",
         "Multiple potholes causing accidents",
         23.3901, 77.6012, None, "2025-02-14 11:45:00", None,
         "In Progress", 1, None, None),

        ("SW-2025-PUN-0008", 3, "Waterlogging",     "Medium",
         "Road floods during rain near flyover",
         18.5321, 73.8712, None, "2025-01-20 08:10:00", None,
         "Acknowledged", 2, None, None),

        ("SW-2025-JPR-0015", 5, "Missing Signage",  "High",
         "Speed limit board missing for 3km stretch",
         26.9544, 75.8193, None, "2025-03-05 16:30:00", None,
         "Submitted", 5, None, None),

        ("SW-2025-LKO-0003", 9, "Broken Divider",   "Critical",
         "Central divider broken — head-on collision risk",
         26.8823, 80.9721, None, "2025-04-12 07:20:00", None,
         "In Progress", 8, None, None),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO complaints
        (complaint_id,road_id,complaint_type,severity,description,
         reported_lat,reported_lon,photo_path,timestamp,reporter_contact,
         status,authority_assigned,resolution_date,resolution_notes)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, complaints)
    print("✅ Sample complaints seeded")

    conn.commit()
    conn.close()
    print("\n🎉 All data seeded successfully! Database ready at:", DB_PATH)

if __name__ == "__main__":
    seed_all()