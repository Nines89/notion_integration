from accomodation_integration import main_fil_choice

with open('link.txt', 'r') as f:
    link = f.read()

if link:
    main_fil_choice(link)
