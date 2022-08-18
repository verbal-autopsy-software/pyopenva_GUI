# -*- coding: utf-8 -*-

"""
pyopenva.data
~~~~~~~~~~~~~~
This module creates data used by the app.
"""

# Country list for SmartVA
COUNTRIES = [
    "Unknown",
    "Afghanistan (AFG)",
    "Albania (ALB)",
    "Algeria (DZA)",
    "Andorra (AND)",
    "Angola (AGO)",
    "Antigua and Barbuda (ATG)",
    "Argentina (ARG)",
    "Armenia (ARM)",
    "Australia (AUS)",
    "Austria (AUT)",
    "Azerbaijan (AZE)",
    "Bahrain (BHR)",
    "Bangladesh (BGD)",
    "Barbados (BRB)",
    "Belarus (BLR)",
    "Belgium (BEL)",
    "Belize (BLZ)",
    "Benin (BEN)",
    "Bhutan (BTN)",
    "Bolivia (BOL)",
    "Bosnia and Herzegovina (BIH)",
    "Botswana (BWA)",
    "Brazil (BRA)",
    "Brunei (BRN)",
    "Bulgaria (BGR)",
    "Burkina Faso (BFA)",
    "Burundi (BDI)",
    "Cambodia (KHM)",
    "Cameroon (CMR)",
    "Canada (CAN)",
    "Cape Verde (CPV)",
    "Central African Republic (CAF)",
    "Chad (TCD)",
    "Chile (CHL)",
    "China (CHN)",
    "Colombia (COL)",
    "Comoros (COM)",
    "Congo (COG)",
    "Costa Rica (CRI)",
    "Cote d\"Ivoire (CIV)",
    "Croatia (HRV)",
    "Cuba (CUB)",
    "Cyprus (CYP)",
    "Czech Republic (CZE)",
    "Democratic Republic of the Congo (COD)",
    "Denmark (DNK)",
    "Djibouti (DJI)",
    "Dominica (DMA)",
    "Dominican Republic (DOM)",
    "Ecuador (ECU)",
    "Egypt (EGY)",
    "El Salvador (SLV)",
    "Equatorial Guinea (GNQ)",
    "Eritrea (ERI)",
    "Estonia (EST)",
    "Ethiopia (ETH)",
    "Federated States of Micronesia (FSM)",
    "Fiji (FJI)",
    "Finland (FIN)",
    "France (FRA)",
    "Gabon (GAB)",
    "Georgia (GEO)",
    "Germany (DEU)",
    "Ghana (GHA)",
    "Greece (GRC)",
    "Grenada (GRD)",
    "Guatemala (GTM)",
    "Guinea (GIN)",
    "Guinea-Bissau (GNB)",
    "Guyana (GUY)",
    "Haiti (HTI)",
    "Honduras (HND)",
    "Hungary (HUN)",
    "Iceland (ISL)",
    "India (IND)",
    "Indonesia (IDN)",
    "Iran (IRN)",
    "Iraq (IRQ)",
    "Ireland (IRL)",
    "Israel (ISR)",
    "Italy (ITA)",
    "Jamaica (JAM)",
    "Japan (JPN)",
    "Jordan (JOR)",
    "Kazakhstan (KAZ)",
    "Kenya (KEN)",
    "Kiribati (KIR)",
    "Kuwait (KWT)",
    "Kyrgyzstan (KGZ)",
    "Laos (LAO)",
    "Latvia (LVA)",
    "Lebanon (LBN)",
    "Lesotho (LSO)",
    "Liberia (LBR)",
    "Libya (LBY)",
    "Lithuania (LTU)",
    "Luxembourg (LUX)",
    "Macedonia (MKD)",
    "Madagascar (MDG)",
    "Malawi (MWI)",
    "Malaysia (MYS)",
    "Maldives (MDV)",
    "Mali (MLI)",
    "Malta (MLT)",
    "Marshall Islands (MHL)",
    "Mauritania (MRT)",
    "Mauritius (MUS)",
    "Mexico (MEX)",
    "Moldova (MDA)",
    "Mongolia (MNG)",
    "Montenegro (MNE)",
    "Morocco (MAR)",
    "Mozambique (MOZ)",
    "Myanmar (MMR)",
    "Namibia (NAM)",
    "Nepal (NPL)",
    "Netherlands (NLD)",
    "New Zealand (NZL)",
    "Nicaragua (NIC)",
    "Niger (NER)",
    "Nigeria (NGA)",
    "North Korea (PRK)",
    "Norway (NOR)",
    "Oman (OMN)",
    "Pakistan (PAK)",
    "Palestine (PSE)",
    "Panama (PAN)",
    "Papua New Guinea (PNG)",
    "Paraguay (PRY)",
    "Peru (PER)",
    "Philippines (PHL)",
    "Poland (POL)",
    "Portugal (PRT)",
    "Qatar (QAT)",
    "Romania (ROU)",
    "Russia (RUS)",
    "Rwanda (RWA)",
    "Saint Lucia (LCA)",
    "Saint Vincent and the Grenadines (VCT)",
    "Samoa (WSM)",
    "Sao Tome and Principe (STP)",
    "Saudi Arabia (SAU)",
    "Senegal (SEN)",
    "Serbia (SRB)",
    "Seychelles (SYC)",
    "Sierra Leone (SLE)",
    "Singapore (SGP)",
    "Slovakia (SVK)",
    "Slovenia (SVN)",
    "Solomon Islands (SLB)",
    "Somalia (SOM)",
    "South Africa (ZAF)",
    "South Korea (KOR)",
    "Spain (ESP)",
    "Sri Lanka (LKA)",
    "Sudan (SDN)",
    "Suriname (SUR)",
    "Swaziland (SWZ)",
    "Sweden (SWE)",
    "Switzerland (CHE)",
    "Syria (SYR)",
    "Taiwan (TWN)",
    "Tajikistan (TJK)",
    "Tanzania (TZA)",
    "Thailand (THA)",
    "The Bahamas (BHS)",
    "The Gambia (GMB)",
    "Timor-Leste (TLS)",
    "Togo (TGO)",
    "Tonga (TON)",
    "Trinidad and Tobago (TTO)",
    "Tunisia (TUN)",
    "Turkey (TUR)",
    "Turkmenistan (TKM)",
    "Uganda (UGA)",
    "Ukraine (UKR)",
    "United Arab Emirates (ARE)",
    "United Kingdom (GBR)",
    "United States (USA)",
    "Uruguay (URY)",
    "Uzbekistan (UZB)",
    "Vanuatu (VUT)",
    "Venezuela (VEN)",
    "Vietnam (VNM)",
    "Yemen (YEM)",
    "Zambia (ZMB)",
    "Zimbabwe (ZWE)",
]

CAUSETEXTV5 = {
    "a_nrp": {"cause": "Not pregnant or recently delivered",
              "code": "Not pregnant or recently delivered"},
    "a_pend_6w": {"cause": "Pregnancy ended within 6 weeks of death",
                  "code": "Pregnancy ended within 6 weeks of death"},
    "a_preg": {"cause": "Pregnant at death",
               "code": "Pregnant at death"},
    "b_0101": {"cause": "Sepsis (non-obstetric)", 
               "code": 1.01},
    "b_0102": {"cause": "Acute resp infect incl pneumonia",
               "code": 1.02},
    "b_0103": {"cause": "HIV/AIDS related death",
               "code": 1.03},
    "b_0104": {"cause": "Diarrhoeal diseases",
               "code": 01.04},
    "b_0105": {"cause": "Malaria",
               "code": 1.05},
    "b_0106": {"cause": "Measles",
               "code": 1.06},
    "b_0107": {"cause": "Meningitis and encephalitis",
               "code": 1.07},
    "b_0108": {"cause": "Tetanus",
               "code": 1.08},
    "b_0109": {"cause": "Pulmonary tuberculosis",
               "code": 1.09},
    "b_0110": {"cause": "Pertussis",
               "code": 01.10},
    "b_0111": {"cause": "Haemorrhagic fever (non-dengue)",
               "code": 01.11},
    "b_0112": {"cause": "Dengue fever",
               "code": 01.12},
    "b_0199": {"cause": "Other and unspecified infect dis",
               "code": 01.99},
    "b_0201": {"cause": "Oral neoplasms",
               "code": 02.01},
    "b_0202": {"cause": "Digestive neoplasms",
               "code": 02.02},
    "b_0203": {"cause": "Respiratory neoplasms",
               "code": 02.03},
    "b_0204": {"cause": "Breast neoplasms",
               "code": 02.04},
    "b_0205": {"cause": "Reproductive neoplasms MF",
               "code": 02.05},
    "b_0299": {"cause": "Other and unspecified neoplasms",
               "code": 02.99},
    "b_0301": {"cause": "Severe anaemia",
               "code": 03.01},
    "b_0302": {"cause": "Severe malnutrition",
               "code": 03.02},
    "b_0303": {"cause": "Diabetes mellitus",
               "code": 03.03},
    "b_0401": {"cause": "Acute cardiac disease",
               "code": 04.01},
    "b_0402": {"cause": "Stroke",
               "code": 04.02},
    "b_0403": {"cause": "Sickle cell with crisis",
               "code": 04.03},
    "b_0499": {"cause": "Other and unspecified cardiac dis",
               "code": 04.99},
    "b_0501": {"cause": "Chronic obstructive pulmonary dis",
               "code": 05.01},
    "b_0502": {"cause": "Asthma",
               "code": 05.02},
    "b_0601": {"cause": "Acute abdomen",
               "code": 06.01},
    "b_0602": {"cause": "Liver cirrhosis",
               "code": 06.02},
    "b_0701": {"cause": "Renal failure",
               "code": 07.01},
    "b_0801": {"cause": "Epilepsy",
               "code": 08.01},
    "b_0901": {"cause": "Ectopic pregnancy",
               "code": 09.01},
    "b_0902": {"cause": "Abortion-related death",
               "code": 09.02},
    "b_0903": {"cause": "Pregnancy-induced hypertension",
               "code": 09.03},
    "b_0904": {"cause": "Obstetric haemorrhage",
               "code": 09.04},
    "b_0905": {"cause": "Obstructed labour",
               "code": 09.05},
    "b_0906": {"cause": "Pregnancy-related sepsis",
               "code": 09.06},
    "b_0907": {"cause": "Anaemia of pregnancy",
               "code": 09.07},
    "b_0908": {"cause": "Ruptured uterus",
               "code": 09.08},
    "b_0999": {"cause": "Other and unspecified maternal CoD",
               "code": 09.99},
    "b_1001": {"cause": "Prematurity",
               "code": 10.01},
    "b_1002": {"cause": "Birth asphyxia",
               "code": 10.02},
    "b_1003": {"cause": "Neonatal pneumonia",
               "code": 10.03},
    "b_1004": {"cause": "Neonatal sepsis",
               "code": 10.04},
    "b_1006": {"cause": "Congenital malformation",
               "code": 10.06},
    "b_1099": {"cause": "Other and unspecified neonatal CoD",
               "code": 10.99},
    "b_1101": {"cause": "Fresh stillbirth",
               "code": 11.01},
    "b_1102": {"cause": "Macerated stillbirth",
               "code": 11.02},
    "b_1201": {"cause": "Road traffic accident",
               "code": 12.01},
    "b_1202": {"cause": "Other transport accident",
               "code": 12.02},
    "b_1203": {"cause": "Accid fall",
               "code": 12.03},
    "b_1204": {"cause": "Accid drowning and submersion",
               "code": 12.04},
    "b_1205": {"cause": "Accid expos to smoke fire & flame",
               "code": 12.05},
    "b_1206": {"cause": "Contact with venomous plant/animal",
               "code": 12.06},
    "b_1207": {"cause": "Accid poisoning & noxious subs",
               "code": 12.07},
    "b_1208": {"cause": "Intentional self-harm",
               "code": 12.08},
    "b_1209": {"cause": "Assault",
               "code": 12.09},
    "b_1210": {"cause": "Exposure to force of nature",
               "code": 12.10},
    "b_1299": {"cause": "Other and unspecified external CoD",
               "code": 12.99},
    "b_9800": {"cause": "Other and unspecified NCD",
               "code": 98.00},
    "c_cult": {"cause": "Culture",
               "code": "Culture"},
    "c_emer": {"cause": "Emergency",
               "code": "Emergency"},
    "c_hsys": {"cause": "Health systems",
               "code": "Health"},
    "c_inev": {"cause": "Inevitable",
               "code": "Inevitable"},
    "c_know": {"cause": "Knowledge",
               "code": "Knowledge"},
    "c_resr": {"cause": "Resources",
               "code": "Resources"}}
