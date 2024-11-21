import json
import os
import sys

def create_constituency_folders(json_data, base_path):
    """
    Create folders for regions and their constituencies
    
    Args:
        json_data (dict): Dictionary containing regions and constituencies
        base_path (str): Base directory where folders will be created
    """
    try:
        # Convert to absolute path
        absolute_path = os.path.abspath(base_path)
        
        print(f"\nPreparing to create folders in: {absolute_path}")
        confirm = input("Do you want to proceed? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("Operation cancelled by user.")
            return

        # Create base directory if it doesn't exist
        if not os.path.exists(absolute_path):
            os.makedirs(absolute_path)
            print(f"Created base directory: {absolute_path}")

        # Iterate through regions
        for region, constituencies in json_data.items():
            # Create region folder
            region_path = os.path.join(absolute_path, region)
            if not os.path.exists(region_path):
                os.makedirs(region_path)
                print(f"Created region folder: {region}")
            
            # Create constituency folders
            for constituency in constituencies:
                # Clean constituency name to be safe for folder names
                safe_constituency = "".join(c for c in constituency if c.isalnum() or c in (' ', '-', '_'))
                constituency_path = os.path.join(region_path, safe_constituency)
                
                if not os.path.exists(constituency_path):
                    os.makedirs(constituency_path)
                    print(f"Created constituency folder: {constituency}")

        print("\nFolder creation completed successfully!")
        print(f"All folders have been created in: {absolute_path}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Option 1: Current directory (will create in same folder as script)
    base_directory = "Ghana_Constituencies"
    
    # Option 2: Specify full path (uncomment and modify as needed)
    # base_directory = r"C:\Users\YourUsername\Desktop\Ghana_Constituencies"
    
    # Option 3: Ask user for location
    print("\nWhere would you like to create the folders?")
    print("1. Current directory:", os.path.abspath(os.getcwd()))
    print("2. Desktop")
    print("3. Custom location")
    
    choice = input("Enter your choice (1/2/3): ")
    
    if choice == "1":
        base_directory = "Ghana_Constituencies"
    elif choice == "2":
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        base_directory = os.path.join(desktop, "Ghana_Constituencies")
    elif choice == "3":
        base_directory = input("Enter the full path where you want to create the folders: ")
    else:
        print("Invalid choice. Using current directory.")
        base_directory = "Ghana_Constituencies"

    # Your JSON data goes here
    constituencies_data = {
  "AHAFO_REGION": [
    "Asunafo North",
    "Asunafo South",
    "Asutifi North",
    "Asutifi South",
    "Tano North",
    "Tano South"
  ],
  "ASHANTI_REGION": [
    "Adansi Asokwa",
    "Adansi North",
    "Afigya Kwabre North",
    "Afigya Kwabre South",
    "Afigya Sekyere East",
    "Ahafo Ano North",
    "Ahafo Ano South East",
    "Ahafo Ano South West",
    "Akrofuom",
    "Asante Akim Central",
    "Asante Akim North",
    "Asante Akim South",
    "Asokwa",
    "Atwima Kwanwoma",
    "Atwima Mponua",
    "Atwima Nwabiagya North",
    "Atwima Nwabiagya South",
    "Bantama",
    "Bekwai",
    "Bosome Freho",
    "Bosomtwe",
    "Ejisu",
    "Ejura Sekyedumase",
    "Fomena",
    "Juaben",
    "Manhyia North",
    "Manhyia South",
    "Manso Adubia",
    "Manso Nkwanta",
    "Manyia",
    "New Edubiase",
    "Nhyiaeso",
    "Obuasi East",
    "Obuasi West",
    "Odotobri",
    "Offinso North",
    "Offinso South",
    "Old Tafo",
    "Oforikrom",
    "Kwadaso",
    "Kwabre East",
    "Kumawu",
    "Sekyere Afram Plains",
    "Sekyere East",
    "Suame",
    "Subin",
    "Effiduase-Asokore"
  ],
  "BONO_REGION": [
    "Banda",
    "Berekum East",
    "Berekum West",
    "Dormaa Central",
    "Dormaa East",
    "Dormaa West",
    "Jaman North",
    "Jaman South",
    "Sunyani East",
    "Sunyani West",
    "Tain",
    "Wenchi"
  ],
  "BONO_EAST_REGION": [
    "Atebubu-Amantin",
    "Kintampo North",
    "Kintampo South",
    "Nkoranza North",
    "Nkoranza South",
    "Pru East",
    "Pru West",
    "Sene East",
    "Sene West",
    "Techiman North",
    "Techiman South"
  ],
  "EASTERN_REGION": [
    "Abetifi",
    "Abirem",
    "Abuakwa North",
    "Abuakwa South",
    "Afram Plains North",
    "Afram Plains South",
    "Akropong",
    "Akwatia",
    "Asuogyaman",
    "Atiwa East",
    "Atiwa West",
    "Ayensuano",
    "Fanteakwa North",
    "Fanteakwa South",
    "Kade",
    "Kwaebibirem",
    "Lower Manya",
    "Lower West Akim",
    "New Juaben North",
    "New Juaben South",
    "Nkawkaw",
    "Nsawam-Adoagyiri",
    "Ofoase-Ayirebi",
    "Okere",
    "Suhum",
    "Upper Manya",
    "Upper West Akim",
    "Yilo Krobo",
    "Akim Oda",
    "Akim Swedru",
    "Akwapim South",
    "Akyem Abuakwa North",
    "Mpraeso"
  ],
  "GREATER_ACCRA_REGION": [
    "Ablekuma Central",
    "Ablekuma North",
    "Ablekuma South",
    "Ablekuma West",
    "Adentan",
    "Ashaiman",
    "Ayi Mensah",
    "Bortianor-Ngleshie Amanfro",
    "Dade Kotopon",
    "Dome-Kwabenya",
    "Domeabra-Obom",
    "Korle Klottey",
    "Krowor",
    "La Dadekotopon",
    "Ledzokuku",
    "Madina",
    "Ningo Prampram",
    "Odododiodoo",
    "Okaikwei Central",
    "Okaikwei North",
    "Okaikwei South",
    "Shai Osudoku",
    "Tema Central",
    "Tema East",
    "Tema West",
    "Trobu",
    "Weija-Gbawe",
    "Ayawaso Central",
    "Ayawaso East",
    "Ayawaso North",
    "Ayawaso West Wuogon",
    "Kpone Katamanso",
    "Sege",
    "Ada"
  ],
  "NORTH_EAST_REGION": [
    "Walewale",
    "Yagaba-Kubori",
    "Yunyoo",
    "Chereponi",
    "Nalerigu",
    "Bunkpurugu"
  ],
  "NORTHERN_REGION": [
    "Bimbilla",
    "Gushegu",
    "Karaga",
    "Kpandai",
    "Mion",
    "Nanton",
    "Saboba",
    "Savelugu",
    "Tamale Central",
    "Tamale North",
    "Tamale South",
    "Tatale-Sanguli",
    "Tolon",
    "Wulensi",
    "Yendi",
    "Zabzugu",
    "Sagnarigu",
    "Nalerigu-Gambaga"
  ],
  "OTI_REGION": [
    "Biakoye",
    "Buem",
    "Krachi East",
    "Krachi Nchumuru",
    "Krachi West",
    "Nkwanta North",
    "Nkwanta South",
    "Akan"
  ],
  "SAVANNAH_REGION": [
    "Bole-Bamboi",
    "Damongo",
    "Daboya-Mankarigu",
    "Salaga North",
    "Salaga South",
    "Sawla-Tuna-Kalba",
    "Yapei-Kusawgu"
  ],
  "UPPER_EAST_REGION": [
    "Binduri",
    "Bawku Central",
    "Bawku West",
    "Bolgatanga Central",
    "Bolgatanga East",
    "Builsa North",
    "Builsa South",
    "Chiana-Paga",
    "Garu",
    "Navrongo Central",
    "Pusiga",
    "Tempane",
    "Zebilla",
    "Talensi",
    "Nabdam"
  ],
  "UPPER_WEST_REGION": [
    "Daffiama-Bussie-Issa",
    "Jirapa",
    "Lambussie",
    "Lawra",
    "Nadowli-Kaleo",
    "Nandom",
    "Sissala East",
    "Sissala West",
    "Wa Central",
    "Wa East",
    "Wa West"
  ],
  "VOLTA_REGION": [
    "Adaklu",
    "Afadjato South",
    "Agotime-Ziope",
    "Anlo",
    "Avenor-Ave",
    "Central Tongu",
    "Ho Central",
    "Ho West",
    "Hohoe",
    "Keta",
    "Ketu North",
    "Ketu South",
    "North Dayi",
    "North Tongu",
    "South Dayi",
    "South Tongu",
    "Akatsi North",
    "Akatsi South"
  ],
  "WESTERN_NORTH_REGION": [
    "Bibiani-Anhwiaso-Bekwai",
    "Bia East",
    "Bia West",
    "Bodi",
    "Juaboso",
    "Sefwi Akontombra",
    "Sefwi Wiawso",
    "Suaman",
    "Aowin"
  ],
  "WESTERN_REGION": [
    "Ahanta West",
    "Amenfi Central",
    "Amenfi East",
    "Amenfi West",
    "Evalue-Ajomoro-Gwira",
    "Jomoro",
    "Kwesimintsim",
    "Mpohor",
    "Prestea Huni-Valley",
    "Sefwi-Wiawso",
    "Sekondi",
    "Shama",
    "Takoradi",
    "Tarkwa-Nsuaem",
    "Effia",
    "Ellembelle",
    "Essikado-Ketan"
  ],
  "CENTRAL_REGION": [
    "Abura-Asebu-Kwamankese",
    "Agona East",
    "Agona West",
    "Ajumako-Enyan-Essiam",
    "Asikuma-Odoben-Brakwa",
    "Assin Central",
    "Assin North",
    "Assin South",
    "Awutu Senya East",
    "Awutu Senya West",
    "Cape Coast North",
    "Cape Coast South",
    "Effutu",
    "Ekumfi",
    "Gomoa Central",
    "Gomoa East",
    "Gomoa West",
    "Hemang Lower Denkyira",
    "Komenda-Edina-Eguafo-Abirem",
    "Mfantseman",
    "Twifo Atti Morkwa",
    "Twifo Hemang Lower Denkyira",
    "Upper Denkyira East",
    "Upper Denkyira West"
  ]
}



create_constituency_folders(constituencies_data, base_directory)