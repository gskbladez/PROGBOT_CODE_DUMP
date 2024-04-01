#Yadon keeps track of tables, which are stored in text files... it's slow, like Yadon...
#- "Keep it simple stupid"
#- Useful as a quick and dirty way to store data on drive if efficiency is not important
#- Keys and values are all strings
#- Each row is made up of the key followed by the row values, all separated by tabs
#- Tables are edited by simply rewriting the text file
#- Keep backups of tables in case writing fails for whatever reason!
#- When manually editing the text files, make sure the last line is empty (line break) so that appending will work properly
#- Each of these methods have an optional named_columns parameter which determines the data structure of the table:
#-- if False, {key -> [value1, value2]}
#-- if True, {key -> {column1: value1, column2: value2}}, where the first row is used to determine the column names

import sys, os
from collections import OrderedDict

#Reads a table and returns either a dictionary with the table data, or None if the table doesn't exist
#If named_columns is True, the first row is used as the header, and values will be a dictionary instead of a list
def ReadTable(table_name, named_columns=False):
    try:
        file = open(table_name, encoding="utf8")
    except FileNotFoundError:
        return None
    
    table = OrderedDict()
    lines = file.read().split("\n")
    
    column_names = []
    for i in range(len(lines)):
        line = lines[i]
        if line == "":
            continue
        entries = line.split("\t")
        
        if i == 0 and named_columns:
            column_names = entries
        elif named_columns:
            key = entries[0]
            table[key] = {}
            for j in range(1, len(column_names)):
                column_name = column_names[j]
                try:
                    table[key][column_name] = entries[j]
                except IndexError:
                    table[key][column_name] = ""
        else:
            key = entries[0]
            table[key] = entries[1:]
    
    return table

#Reads a row from a table given a key and returns the values
#Returns None if the table doesn't exist or the key doesn't exist in the table
def ReadRowFromTable(table_name, key, named_columns=False):
    table = ReadTable(table_name, named_columns)
    
    if table is None:
        return None
    elif str(key) not in table.keys():
        return None
    else:
        return table[str(key)]

#Writes a new table, or replaces a table if it exists already (use with caution!)
#Use OrderedDict instead of a normal dict if ordering is important
#If named_columns is True, column names will be collected from the table values and written as the first row
def WriteTable(table_name, table, named_columns=False):
    if not isinstance(table, dict):
        raise TypeError("yadon.WriteTable: table parameter should be a dict")
    
    #for safety measure
    old = ReadTable(table_name)
    
    try:
        file = open("{}.txt".format(table_name), "w", encoding="utf8")
    #Can happen occasionally if tables are being edited very quickly
    except OSError:
        raise
    
    try:
        if named_columns:
            #First collect column names from table values
            #Using OrderedDict instead of set since set is unordered
            column_names = OrderedDict()
            for key in table.keys():
                if not isinstance(table[key], dict):
                    raise TypeError("yadon.WriteTable: table values should be dicts if named_columns is True")
                for key2 in table[key].keys():
                    column_names[key2] = ""
            
            #Then write the header
            column_names = list(column_names.keys())
            column_names_string = "\t" + "\t".join(column_names) if column_names else ""
            file.write("HEADER" + column_names_string + "\n")
            
            #Then write the values
            for key in table.keys():
                values = []
                for column_name in column_names:
                    try:
                        values.append(str(table[key][column_name]))
                    except KeyError:
                        values.append("")
                file.write("\t".join([str(key)] + values) + "\n")
        else:
            for key in table.keys():
                if not isinstance(table[key], list):
                    raise TypeError("yadon.WriteTable: table values should be lists if named_columns is False")
                values = [str(x) for x in table[key]]
                file.write("\t".join([str(key)] + values) + "\n")
        file.close()
    #For whatever reason if writing fails, write the old table back
    except Exception as e:
        WriteTable(table_name, old)
        raise

#Writes a row to a table only if the key doesn't exist yet (use AppendValuesToRow if this check is unwanted)
#Returns 0 if successful, -1 if not (key already exists)
#If named_columns is False, appends to text file instead of rewriting the whole file, which should be faster
def AppendRowToTable(table_name, key, values, named_columns=False):
    if not named_columns and not isinstance(values, list):
        raise TypeError("yadon.AppendRowToTable: values parameter should be a list if named_columns is False")
    if named_columns and not isinstance(values, dict):
        raise TypeError("yadon.AppendRowToTable: values parameter should be a dict if named_columns is True")
    
    table = ReadTable(table_name, named_columns)
    
    if table is None:
        WriteTable(table_name, {key:values}, named_columns)
    elif str(key) in table.keys():
        return -1
    elif not named_columns:
        file = open("{}.txt".format(table_name), "a", encoding="utf8")
        file.write("\t".join([str(key)] + [str(x) for x in values]) + "\n")
        file.close()
        return 0
    else:
        table[str(key)] = values
        WriteTable(table_name, table, named_columns)
        return 0

#Writes a row to a table
#Creates a new table if it doesn't exist yet
#Replaces the row's values if the key already exists in the table
def WriteRowToTable(table_name, key, values, named_columns=False):
    if not named_columns and not isinstance(values, list):
        raise TypeError("yadon.WriteRowToTable: values parameter should be a list if named_columns is False")
    if named_columns and not isinstance(values, dict):
        raise TypeError("yadon.WriteRowToTable: values parameter should be a dict if named_columns is True")
    
    table = ReadTable(table_name, named_columns)
    
    #if table doesn't exist yet
    if table is None:
        WriteTable(table_name, {key:values}, named_columns)
    #if row doesn't exist in table yet
    elif str(key) not in table.keys():
        AppendRowToTable(table_name, key, values, named_columns)
    else:
        table[str(key)] = values
        WriteTable(table_name, table, named_columns)

#Appends a list of values to a row in a table
#If named_columns is True, the values are merged into the table instead
#Creates a new table if it doesn't exist yet
#Creates a new row if the key doesn't exist in the table yet
def AppendValuesToRow(table_name, key, values, named_columns=False):
    if not named_columns and not isinstance(values, list):
        raise TypeError("yadon.WriteRowToTable: values parameter should be a list if named_columns is False")
    if named_columns and not isinstance(values, dict):
        raise TypeError("yadon.WriteRowToTable: values parameter should be a dict if named_columns is True")
    
    table = ReadTable(table_name, named_columns)
    
    #if table doesn't exist yet
    if table is None:
        WriteTable(table_name, {key:values}, named_columns)
    #if row doesn't exist in table yet
    elif str(key) not in table.keys():
        AppendRowToTable(table_name, key, values, named_columns)
    elif not named_columns:
        table[str(key)] += values
        WriteTable(table_name, table, named_columns)
    else:
        for key2 in values.keys():
            table[str(key)][key2] = values[key2]
        WriteTable(table_name, table, named_columns)

#Removes a row from a table
#Returns 0 if successful, -1 if not (nonexistent table or key)
#Note: named_columns is used for writing the table
def RemoveRowFromTable(table_name, key, named_columns=False):
    table = ReadTable(table_name, named_columns)
    
    #if table doesn't exist
    if table is None:
        return -1
    #if row doesn't exist in table
    elif str(key) not in table.keys():
        return -1
    else:
        del table[str(key)]
        WriteTable(table_name, table, named_columns)
        return 0

#Removes a value from a row in a table
#If named_columns is True, value is interpreted as the column name, and the value is simply reset to an empty string
#If there are identical values in the row, the first one is removed
#Returns 0 if successful, -1 if not (nonexistent table or key, or value not in row)
def RemoveValueFromRow(table_name, key, value, named_columns=False):
    table = ReadTable(table_name, named_columns)
    
    #if table doesn't exist
    if table is None:
        return -1
    #if row doesn't exist in table
    elif str(key) not in table.keys():
        return -1
    #if key doesn't exist in row
    elif str(value) not in table[str(key)]:
        return -1
    elif not named_columns:
        table[str(key)].remove(str(value))
        WriteTable(table_name, table, named_columns)
        return 0
    else:
        if value not in table[str(key)].keys():
            return -1
        table[str(key)][str(value)] = ""
        WriteTable(table_name, table, named_columns)
        return 0