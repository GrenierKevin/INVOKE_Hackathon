from pydantic import BaseModel
from openai import OpenAI
import pandas as pd
import os
import json

# Insert OpenAI API key below before running
os.environ["OPENAI_API_KEY"] = ''


class Ticket(BaseModel):
    Category: str
    SubCategory: str


# Read the input Excel file
input_excel_path = 'Python\HackathonTickets\TicketClassifierDataShort.xlsx'
df = pd.read_excel(input_excel_path)


client = OpenAI()

# Initialize an empty list to store the responses
json_responses = []
confidences = []


# Loop through each description and get the JSON response
for index, row in df.iterrows():
    # Extract the descriptions
    body = row['Record_Notes']
    classification = row['Classification']
    counter = 0.0
    curr = ""

    #For each description, obtain the openai response 10 times to determine a confidence level
    for i in range(0, 10):
        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """You are a refrigeration engineer that needs to classify support tickets into categories and subcategories. You will be provided with the email body of a support ticket, and you will then need to categorize the ticket into one of the following categories and subcategories and return a JSON response. Categories and associated subcategories are provided as shown.

    1. Non-Mechanical Door Repairs
    1.1 Gaskets.
    1.2 Frame and threshold heaters.
    1.3 Torque rods and door closers.
    1.4 Hold open bars and handles.
    1.5 Door adjustments and hardware.
    1.6 Strip curtain repair/replacement.
    1.7 Replacement doors and glass.
    1.8 Replacement/repair of trim and panels.
    1.9 Resealing cases.

    2. Nuisance Calls
    2.1 System in defrost at time of call. 
    2.2 Door open.
    2.3 Switch turned off.
    2.4 Calls that appear to be refrigeration related but are not.
    2.5 No problem found.

    3. Damage by Customer
    3.1 Damage by Customer.

    4. Case Cleaning/Deicing
    4.1 The cleaning of honeycombs, baffles, back walls, drain pans, and coils.
    4.2 Dirty drain pan.
    4.3 Plumbing backups or plugged drains.

    5. Compressors/Motors
    5.1 Refrigerated compressors on racks and semi-hermetic compressors.
    5.2 Evaporative condenser pumps seals due to scale up.
    5.3 Motors that are over 15 HP.

    6. Capital Replacement
    6.1 Replacement items due to components beyond shelf life and/or related to years of corrosion.
    6.2 Replacement of furnaces, swamp coolers, evaporators, and package units.
    6.3 Corroded headers, sub-coolers, coils, condensers, Heat Reclaim tanks.

    7. Misc. Billable Repairs and Service Calls
    7.1 Ice machines and ice makers that do not belong to Safeway Companies.
    7.2 Self-contained case repairs.
    7.3 Refrigerated cases and coolers that do not belong to Safeway Companies.
    7.4 Inaccessible refrigerant and plumbing lines located underground, inside walls and above ceilings.
    7.5 Strip curtains.
    7.6 Drinking fountains.
    7.7 Carbonated drink dispensers and water filters.
    7.8 Ductwork and duct work insulation.
    7.9 Supply and return air grilles.
    7.10 Electrical components between the power supply panel and termination point on refrigeration/HVAC equipment.
    7.11 Fixture paint, Glass, Porcelain, trim, panels and shelves.
    7.12 Produce hoses and watering equipment.
    7.13 Misting and fogger systems and related equipment.
    7.14 Water treatment equipment, chemical pumps and water treatment chemicals.
    7.15 Non-refrigerated equipment.
    7.16 Lamps and lens cover for walk inbox lighting.
    7.17 Lamps, lens covers and ballast in refrigerated cases.
    7.18 Ice machine sanitary cleaning.
    7.19 Power and water outages – scheduled and/or reactive.
    7.20 Equipment that are the result of interruption in electrical and/or water supply that was not caused by service provider.

    8.0 nan
    8.1 Motors that are under 15 HP
                 
    Do not include numbers in the categories.
                 
    Here is an example of an email received: 

    '''7/15/23
    Travel:10:45-11:15
    Onsite:11:15-12:00
    Checked in with manager Diana upon arrival. 
    Found glass on freezer door cracked. 
    Cover door with cardboard and got info needed for new door. 
    Will submit quote for new door. 

    1 tech 6 hours
    1 door
    1 torque rod
    1 torque master
    1 hinge pin.'''

    Here is an example of the expected JSON response:
            
            {
                        "Category":"Non-Mechanical Door Repairs",
                        "Subcategory":"Replacement doors and glass", 
            }


                    """},
                {"role": "user",
                "content": "The email body is the following: " + body},
            ],
            response_format=Ticket,
        )
        event = completion.choices[0].message.content
        data = json.loads(event)
        #print(data['Category'])
        #print(classification)
        #print(event)
        #Increment counter if expected classification was obtained by openai
        if data['Category'] == classification:
            counter = counter + 1.0
            curr = event
        #print(counter)
    #Append openai response and confidence to appropriate lists    
    if not curr:
        json_responses.append(event)
    else:
        json_responses.append(curr)
    confidences.append(counter/10.0)
    
# Add the JSON response and confidence to new columns (F) in the dataframe
df['JSON Response'] = json_responses
df['Confidence'] = confidences

# Save the updated dataframe back to an Excel file
output_excel_path = 'Python\HackathonTickets\Output.xlsx'
df.to_excel(output_excel_path, index=False)