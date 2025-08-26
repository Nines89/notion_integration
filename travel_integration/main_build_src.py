
from travel_integration import main_build_info

with open('link.txt', 'r') as f:
    link = f.read()

if link:
    main_build_info(link)