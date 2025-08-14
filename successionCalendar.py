import sys
import json
import csv
import re
import datetime

def main():
    print('Welcome to the Python Garden Planner!')
    with open('./data/user_profile.json', 'r') as file:
        user_profile = json.load(file)
        user_profile = json.loads(user_profile)
    try:
        while(True):
            path = input('What would you like to do?\n1 - Generate Calendar\n2 - Edit Crops\n3 - Set Frost Dates\n4 - View Crop Data\n(1 / 2 / 3 / 4)\n')
            if path == '1':
                # Generate the calendar
                for item in generate_calendar():
                    print(item)
                break
            elif path == '2':
                # Modify crops
                modify_crops()
                break
            elif path == '3':
                # Modify / set the frost dates
                frost_dates(user_profile)
            elif path == '4':
                data = print_crop_data()
                if len(data) != 0:
                    for item in data:
                        print(item)
                else:
                    print('You currently have no crops loaded!\n')
    except EOFError:
        sys.exit('Operation aborted')
    except:
        pass

def generate_calendar():
    important_dates = {}
    with open('./data/user_profile.json', 'r') as frost_file:
        temp = json.load(frost_file)
        temp = json.loads(temp)
        important_dates.update({'Spring frost': temp['spring_frost'], 'Winter frost': temp['winter_frost']})
    crop_data = []
    with open('./data/crops.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            crop_data.append(row)
    # row[0] == crop_name
    # row[1] == Days to harvest
    # row[2] == planting frequency
    # for each crop, generate planting and harvest dates.  Add those dates to the dictionary important_dates
    for row in crop_data:
        n = 0
        planting_frequency = datetime.timedelta(days = int(row[2]))
        harvest_time = datetime.timedelta(days = int(row[1]))
        spring_frost = datetime.date.fromisoformat(important_dates['Spring frost'])
        winter_frost = datetime.date.fromisoformat(important_dates['Winter frost'])
        while True:
            harvest_date = spring_frost + planting_frequency * n + harvest_time
            if harvest_date < winter_frost:
                important_dates.update({f'{row[0]} Planting {n + 1}': f'{spring_frost + planting_frequency * n}'})
                important_dates.update({f'{row[0]} Harvest {n + 1}': f'{harvest_date}'})
                n = n + 1
            else:
                break
    # Translate important_dates to dates_list from a dictionary to a list of tuples
    dates_list = list(important_dates.items())
    # Convert datetime.date(x,y,z) to proper format and store in new_list
    formatted_dates_list =[]
    for row in dates_list:
        formatted_dates_list.append([row[0], row[1]])
    for row in formatted_dates_list:
        if type(row[1]) == type('str'):
            row[1] = datetime.date.fromisoformat(row[1])
    # Define a sorting fuction to order by date, and sort formatted_dates_list in date order
    def sorting_function(list):
        return list[1]
    formatted_dates_list.sort(key=sorting_function)
    # print action and dates for gardener
    final_list = []
    for row in formatted_dates_list:
        final_list.append(f'{row[0]}: {row[1]}')
    return final_list

def modify_crops():
    try:
        while True:
            path = input('What action would you like to perform on your crops?\n1 - Add new crop\n2 - Modify an existing crop\n3 - Remove a crop\n4 - Reset all crops\n5 - Cancel\n')
            if path == '1':
                append_crop(add_crop())
            elif path == '2':
                edit_existing_crop()
            elif path == '3':
                remove_crop()
            elif path == '4':
                reset_confirm = False
                reset_confirm = input('Are you sure you want to reset you whole crop list? (y / n)\n')
                if reset_confirm == 'y':
                    print('Crop list has been reset')
                    reset_crops()
                else:
                    print('Invalid input, operation has been aborted.\n')
            elif path == '5':
                print('Operation aborted\n')
                sys.exit()
    except EOFError:
        sys.exit('Operation aborted')

def add_crop(check_bypass = False):
    while True:
        crop_name = input('What would you like your crop to be called?\n')
        # Bypass exist_checker function for crops that have been previously selected
        if check_bypass == True:
            is_checked = True
            break
        is_checked = False
        with open('./data/crops.csv', 'r') as file:
            reader = csv.reader(file)
            exist_checker = False
            for row in reader:
                if crop_name in row:
                    exist_checker = True
            if exist_checker == True:
                while True:
                    choice = input('This crop already exists!\nWould you like to edit the crop? (y/n)\n')
                    if choice == 'y' or choice == 'n':
                        break
                    else:
                        print('Invalid input. Please enter either "y" or "n".')
                if choice == 'y':
                    print('. . . Redirecting . . . ')
                    edit_existing_crop(crop_name)
                    break
                elif choice == 'n':
                    break
            else:
                is_checked=True
        if is_checked == True:
            break
    if is_checked == True:
        # Gather and validate crop information
        while True:
            try:
                crop_time = int(input('How many days from sowing to harvest?\n'))
                if crop_time > 0:
                    break
            except EOFError:
                sys.exit('Operation aborted')
            except:
                print('Please enter a valid integer greater than 0.')
        while True:
            try:
                crop_frequency = int(input('How frequently in number of days would you like to harvest?\n'))
                if crop_frequency > 0:
                    break
            except EOFError:
                sys.exit('operation aborted')
            except:
                print('Please enter a valid integer greater than 0')
        new_line = [crop_name, crop_time, crop_frequency]
        return new_line

def append_crop(new_line):
    with open('./data/crops.csv', 'a', newline = '') as file:
        writer = csv.writer(file)
        writer.writerow(new_line)

def check_crop_exists(crop):
    try:
        with open("./data/crops.csv", 'r') as file:
            exist_checker = False
            reader = csv.reader(file)
            for row in reader:
                if crop in row:
                    exist_checker = True
            if exist_checker == True:
                return exist_checker
            else:
                print('No such crop found.\n')
                return exist_checker
    except EOFError:
        sys.exit()

def edit_existing_crop(crop = None):
    # Check if argv[1] exists, if so use it, otherwise ask for input
    if crop != None:
        print(f"You are editing {crop}.\n")
    else:
        crop = input('What crop would you like to edit?\n')
    # verify that crop exists in crops.csv
    exist_check = check_crop_exists(crop)
    if exist_check == True:
        # Import crops.csv and convert into a list
        new_file = []
        with open('./data/crops.csv', 'r') as file_read:
            reader = csv.reader(file_read)
            for row in reader:
                new_file.append(row)
        count = 0
        # Find Crop, modify it in new_file using add_crop()
        for row in new_file:
            if row[0] == crop:
                new_data = add_crop(True)
                new_file[count] = new_data
            count = count + 1
        # Clear crops.csv to prep for rewrite with modified crop
        reset_crops()
        # Rewrite crops.csv with new data
        with open('./data/crops.csv', 'a') as file_write:
            writer = csv.writer(file_write)
            for item in new_file:
                writer.writerow(item)

def remove_crop():
    crop = input('What crop would you like to remove?\n')
    exist_check = check_crop_exists(crop)
    if exist_check == True:
        # Write a list of all items in crops.csv without the selected crop
        update_list =[]
        with open('./data/crops.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] != crop:
                    update_list.append(row)
                else:
                    pass
        reset_crops()
        with open('./data/crops.csv', 'a', newline = '') as file:
            writer = csv.writer(file)
            for item in update_list:
                writer.writerow(item)
    else:
        print('Specified crop does not exist.\n')

def reset_crops():
    with open('./data/crops.csv', 'w') as file:
        file.truncate()

def frost_dates(user_profile):
    while(True):
        try:
            frost_bool = input('Does your area experience a winter frost? (y/n)\n')
            frost_bool == frost_bool.lower()
            if frost_bool == 'y' or frost_bool == 'yes':
                get_frost_dates(user_profile)
                break
            elif frost_bool == 'n' or frost_bool == 'no':
                print('The calendar will generate')
                current_year = datetime.date.today().year
                user_profile['spring_frost'] = f'{current_year}-01-01'
                user_profile['winter_frost'] = f'{current_year}-12-31'
                user_profile['start_date'] = f'{current_year}-01-01'
                user_profile = json.dumps(user_profile)
                with open('./data/user_profile.json', 'w') as f:
                    json.dump(user_profile, f)
                print('\nFrost dates successfully updated\n')
                break
            else:
                pass
        except EOFError:
            sys.exit()
        except:
            pass

def get_frost_dates(user_profile):
    while(True):
        try:
            spring_frost = input('What is your last spring frost date? (mm-dd)\n')
            check_one_var = spring_frost.split('-')
            check_one_var[0] = int(check_one_var[0])
            check_one_var[1] = int(check_one_var[1])
            if check_one_var[0] < 1 or check_one_var[0] > 12 or check_one_var[1] < 1 or check_one_var[1] > 31:
                raise ValueError('Invalid Date Entry')
            validate = r"^[0-1][0-9]-[0-3]\d$"
            if re.fullmatch(validate, spring_frost):
                user_profile['spring_frost'] = f"{datetime.date.today().year}-{spring_frost}"
            if int(spring_frost[0] + spring_frost[1]) >= 7:
                year = datetime.date.today().year + 1
            else:
                year = datetime.date.today().year
            user_profile['start_date'] = user_profile['spring_frost']
            winter_frost = input('What is your first winter frost date? (mm-dd)\n')
            if re.fullmatch(validate, winter_frost):
                user_profile['winter_frost'] = f"{year}-{winter_frost}"
            x = json.dumps(user_profile)
            with open("./data/user_profile.json", 'w') as f:
                json.dump(x, f)
            break
        except EOFError:
            sys.exit()
        except:
            print('Error - Invalid Entry')
        break

def print_crop_data():
    # This function returns the current contents of crops.csv in a user friendly readable format.
    with open('./data/crops.csv', 'r') as file:
        reader = csv.reader(file)
        data = []
        for row in reader:
            data.append(f'{row[0]} | Days to harvest: {row[1]}; Planting frequency: {row[2]}')
        return data

if __name__ == "__main__":
    main()
