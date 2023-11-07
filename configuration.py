# All of the phrases to flag for in violations. This is case insensitive.
# For example, if you want to flag for "certified food employee" and "certified food manager certificate",
# you would add "certified food employee" and "certified food manager certificate" to this list.
phrasesToFlagForInViolations = [
    "certified food employee",
    "certified food manager certificate",
    "certified food manager",
    "certification is not posted",
    "food employee certification",
    "food facility has lost its certified food employee",
    "food facility does not employ a certified food employee",
    "food facility does not have an employee with Chester County Certified Food Manager certification",
    "food facility does not yet employ a certified",
    "food facility does not yet have an employee with Chester County Certified Food Manager certification",
    "food facility lost its certified employee",
    "food facility lost its certified food employee",
    "food facility lost its certified food manager",
    "food facility has an employee who held a Certified Food Manager certificate",
    "food facility has an employee that has taken food safety training program",
    "food facility has an employee who held a Certified Food Manager certificate",
    "food facility does not yet employ a certified food employee",
    "no certified employee",
    "no certified employee, no certificate",
    "certified supervisory employee",
    "supervisory employee certification",
    "get this certification"
]

# All of the counties you want to search violations for. This is case insensitive.
# Note: Each county name must have a comma after it except for the last county name.
#       It must also be surrounded by quotes.
countiesToSearchFor = [
    'Adams',
    'Allegheny',
    'Armstrong',
    'Beaver',
    'Bedford',
    'Berks',
    'Blair',
    'Bradford',
    'Bucks',
    'Butler',
    'Cambria',
    'Cameron',
    'Carbon',
    'Centre',
    'Chester',
    'Clarion',
    'Clearfield',
    'Clinton',
    'Columbia',
    'Crawford',
    'Cumberland',
    'Dauphin',
    'Delaware',
    'Elk',
    'Erie',
    'Fayette',
    'Forest',
    'Franklin',
    'Fulton',
    'Greene',
    'Huntingdon',
    'Indiana',
    'Jefferson',
    'Juniata',
    'Lackawanna',
    'Lancaster',
    'Lawrence',
    'Lebanon',
    'Lehigh',
    'Luzerne',
    'Lycoming',
    'McKean',
    'Mercer',
    'Mifflin',
    'Monroe',
    'Montgomery',
    'Montour',
    'Northampton',
    'Northumberland',
    'Perry',
    'Philadelphia',
    'Pike',
    'Potter',
    'Schuylkill',
    'Snyder',
    'Somerset',
    'Sullivan',
    'Susquehanna',
    'Tioga',
    'Union',
    'Venango',
    'Warren',
    'Washington',
    'Wayne',
    'Westmoreland',
    'Wyoming',
    'York'
]

# Start and end date fields to search for.
# Keep blank to use yesterday's date as the start date and today's date as the end date.
# Date Format: MM/DD/YYYY
startDate = '09/25/2023'
endDate = '11/7/2023'

# Set this to 'True' if you find your computer is slow and skipping over violations.
# Note: This will make the program take longer to run but have more consistent results in laggy situations.
isGlitching = False

# Enable this if bought Excel to unlock formatting and other features.
haveExcelProductKey = False

# Set this to 'True' if you want to run the program in the background rather than opening up an instance of
# Chrome. This is useful if you want to run the program in the background while you do other things.
runInBackground = False

# Set this to 'True' if you want to keep the browser open after the program is finished.
keepBrowserOpenAfterFinished = True
