#   Wwise Generate Gamesyncs Data Table.py
#
#   Created by: Jon Evans
#   Created on: Mar 29, 2020
"""
This script has been written to work as part of a workflow optimization for
working in the Unreal Engine with Wwise Gamesyncs. This script will parse
the 'SoundbanksInfo.xml' file into the different switch, state and game
parameter data, then sort that data into a .csv which can be read by UE4 as
a data table. That data table can then be used to provide constant referencable
trings from a single location, instead of copy/pasting them into Wwise nodes.
"""
# Import the module for parsing the .xml into a Python object
import untangle

# Set usable values
SOUNDBANK_PATH = 'SoundbanksInfo.xml'  # The path to the Wwise soundbank
INIT_BANK = 'Init.bnk'  # The file name of the soundbank not needed
DEFAULT_SURFACE_TYPE = '"SurfaceType_Default"'  # Default Surface Type as displayed in .csv
CSV_TOP_ROW = '---,State/Switch_Group,State/Switch,PhysicalSurfaces\n'  # Datatable column info
STATE_NONE = 'None'  # State to ignore
NAME_STR = 'Name'  # XML paramater
SUCCESS_MESSAGE = 'File(s) generated in current folder'  # Notify the user that datatables were generated

output_file = 'DT_Wwise'  # The file name of the desired .csv


def get_game_parameters_list(obj: untangle.Element) -> list:
    """
    Get a nested list of RTPC names
    :param obj: the untangle Element representing the XML element
    :return: A list of all the RTPC names
    """
    print(type(obj))
    name_list = []
    for i in range(len(obj.GameParameters)):
        name_list.append(obj.GameParameters.GameParameter[i][NAME_STR])

    for i in range(len(name_list)):
        name_list[i] = [str(f'{name_list[i]},"{name_list[i]}","{name_list[i]}",{DEFAULT_SURFACE_TYPE}')]

    return name_list


def get_states(obj: untangle.Element) -> list:
    """
    Get a nested list of State names
    :param obj: the untangle Element representing the XML element
    :return: A list of all the State names
    """
    name_list = []
    group_count = len(obj.StateGroups)
    for i in range(group_count):
        # If there are more that one State Groups, then get the first index
        current_group = obj.StateGroups.StateGroup[i] if (group_count > 1) else obj.StateGroups.StateGroup

        group_name = current_group[NAME_STR]
        # For each state, add to the name_list
        for k in range(len(current_group.States)):
            state_name = current_group.States.State[k][NAME_STR]
            if state_name != STATE_NONE:
                name_list.append([str(f'{state_name},"{group_name}","{state_name}",{DEFAULT_SURFACE_TYPE}')])

    return name_list


def get_switches(obj: untangle.Element) -> list:
    """
    Get a nested list of switch names
    :param obj: the untangle Element representing the XML element
    :return: A list of all the Switch names
    """
    name_list = []
    group_count = len(obj.SwitchGroups)
    # For each Switch Group, get the switch name
    for i in range(group_count):
        # If there are more that one Switch Groups, then get the first index
        current_group = obj.SwitchGroups.SwitchGroup[i] if (group_count > 1) else obj.SwitchGroups.SwitchGroup

        group_name = current_group[NAME_STR]

        # For each switch, add to the name_list
        for k in range(len(current_group.Switches)):
            switch_name = current_group.Switches.Switch[k][NAME_STR]
            if switch_name != STATE_NONE:
                name_list.append([str(f'{switch_name},"{group_name}","{switch_name}",{DEFAULT_SURFACE_TYPE}')])

    return name_list


def create_csv(csv_data: str, index: int, output_file: str) -> None:
    """
    Creates a .csv file in the current folder.
    :param csv_data: The data as a string, formatted for the .csv
    :param index: The current number iteration if included as part of a loop. Used for naming the .csv file.
    :param output_file: The file name.
    """
    if index != 0:
        output_file += "_" + str(index + 1)

    output_file = f'{output_file}.csv'
    file = open(output_file, 'w')

    try:
        file.write(csv_data)
        file.close()
    except:
        file.close()
        print(f'An Error occurred when writing {output_file}')


def format_list_recursive(nested_list: list) -> str:
    """
    Recursively goes through a nested list, creating a single string
    :param nested_list: a nested list of strings
    :return: a string formated for the .csv
    """
    data_str = ''
    if type(nested_list) == list:
        for i in range(len(nested_list)):
            data_str += format_list_recursive(nested_list[i])
    else:
        data_str += f'{nested_list}\n'

    return data_str


# Run program
def main():
    # Create a python object from the .xml file
    obj = untangle.parse(SOUNDBANK_PATH)

    # List to store all soundbank objects
    soundbanks_list = []

    # Store soundbanks objects that are not Init.bnk in soundbanks_list
    for i in range(len(obj.SoundBanksInfo.SoundBanks)):

        if obj.SoundBanksInfo.SoundBanks.children[i].Path != INIT_BANK:
            soundbanks_list.append(obj.SoundBanksInfo.SoundBanks.children[i])

    # For each soundbank in the list, get the gamesync information and generate a .csv
    for i in range(len(soundbanks_list)):
        game_parameters = get_game_parameters_list(soundbanks_list[i])
        states = get_states(soundbanks_list[i])
        switches = get_switches(soundbanks_list[i])
        csv_data = f'{CSV_TOP_ROW}{format_list_recursive([switches, game_parameters, states])}'
        create_csv(csv_data, i, output_file)

    print(SUCCESS_MESSAGE)


if __name__ == '__main__':
    main()
