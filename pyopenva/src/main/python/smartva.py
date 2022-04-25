# -*- coding: utf-8 -*-

"""
pyopenva.smartva
~~~~~~~~~~~~~~
This module creates a dialog for setting SmartVA options.
"""

from PyQt5.QtWidgets import (QComboBox, QDialog, QDialogButtonBox,
                             QLabel, QVBoxLayout)

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


class SmartVADialog(QDialog):

    def __init__(self, parent=None, country="Unknown", hiv="False",
                 malaria="False", hce="False", freetext="False"):
        super(SmartVADialog, self).__init__(parent=parent)
        self.setWindowTitle("SmartVA Options")
        self.smartva_country = country
        self.smartva_hiv = hiv
        self.smartva_malaria = malaria
        self.smartva_hce = hce
        self.smartva_freetext = freetext

        country_option_set = COUNTRIES
        self.combo_country_label = QLabel("Data are from an HIV region")
        self.combo_country = QComboBox()
        self.combo_country.addItems(country_option_set)
        self.combo_country.setCurrentIndex(
            country_option_set.index(self.smartva_country))
        self.combo_country.currentTextChanged.connect(self.set_country)
        option_set = ["True", "False"]
        self.combo_hiv_label = QLabel("Data are from an HIV region")
        self.combo_hiv = QComboBox()
        self.combo_hiv.addItems(option_set)
        self.combo_hiv.setCurrentIndex(option_set.index(self.smartva_hiv))
        self.combo_hiv.currentTextChanged.connect(self.set_hiv)

        self.combo_malaria_label = QLabel("Data are from a Malaria region")
        self.combo_malaria = QComboBox()
        self.combo_malaria.addItems(option_set)
        self.combo_malaria.setCurrentIndex(
            option_set.index(self.smartva_malaria))
        self.combo_malaria.currentTextChanged.connect(self.set_malaria)

        self.combo_hce_label = \
            QLabel("Use Health Care Experience (HCE) variables")
        self.combo_hce = QComboBox()
        self.combo_hce.addItems(option_set)
        self.combo_hce.setCurrentIndex(
            option_set.index(self.smartva_hce))
        self.combo_hce.currentTextChanged.connect(self.set_hce)

        self.combo_freetext_label = QLabel("Use 'free text' variables")
        self.combo_freetext = QComboBox()
        self.combo_freetext.addItems(option_set)
        self.combo_freetext.setCurrentIndex(
            option_set.index(self.smartva_freetext))
        self.combo_freetext.currentTextChanged.connect(self.set_freetext)

        self.btn_box = QDialogButtonBox(QDialogButtonBox.Cancel |
                                        QDialogButtonBox.Ok)
        self.btn_box.accepted.connect(self.accept)
        self.btn_box.accepted.connect(
            lambda:
            self.parent().update_smartva_country(self.smartva_country))
        self.btn_box.rejected.connect(self.reject)
        self.btn_box.accepted.connect(
            lambda:
            self.parent().update_smartva_hiv(self.smartva_hiv))
        self.btn_box.accepted.connect(
            lambda:
            self.parent().update_smartva_malaria(self.smartva_malaria))
        self.btn_box.rejected.connect(self.reject)
        self.btn_box.accepted.connect(
            lambda:
            self.parent().update_smartva_hce(self.smartva_hce))
        self.btn_box.rejected.connect(self.reject)
        self.btn_box.accepted.connect(
            lambda:
            self.parent().update_smartva_freetext(self.smartva_freetext))
        self.btn_box.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.combo_country_label)
        self.layout.addWidget(self.combo_country)
        self.layout.addWidget(self.combo_hiv_label)
        self.layout.addWidget(self.combo_hiv)
        self.layout.addWidget(self.combo_malaria_label)
        self.layout.addWidget(self.combo_malaria)
        self.layout.addWidget(self.combo_hce_label)
        self.layout.addWidget(self.combo_hce)
        self.layout.addWidget(self.combo_freetext_label)
        self.layout.addWidget(self.combo_freetext)
        self.layout.addWidget(self.btn_box)
        self.setLayout(self.layout)

    def set_country(self, updated_country):
        self.smartva_country = updated_country

    def set_hiv(self, updated_hiv):
        self.smartva_hiv = updated_hiv

    def set_malaria(self, updated_malaria):
        self.smartva_malaria = updated_malaria

    def set_hce(self, updated_hce):
        self.smartva_hce = updated_hce

    def set_freetext(self, updated_freetext):
        self.smartva_freetext = updated_freetext
