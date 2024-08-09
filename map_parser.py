import os
import sys
import json, zcore

def parse(file):
    if not os.path.isfile(file):
        print("not a file, or does not exist")
        exit(1)
    with open(file) as f:
        lines = f.readlines()

    parsed_objects = []
    current_object = None
    
    for line in lines:
        line = line.strip()
        if line.startswith("@"):
            # Create a new object
            obj_type = line[1:]  # Get the object type (e.g., 'rect', 'circle')
            current_object = {
                "type": obj_type,
                "properties": {}
            }
            parsed_objects.append(current_object)
        elif line.startswith(".") and current_object is not None:
            # Define a property for the current object
            parts = line.split()
            prop_name = parts[0][1:]  # Get the property name (remove the leading '.')
            prop_type = parts[1]  # Get the type of the property
            prop_values = parts[2:]  # Get the values of the property
            
            # Store the property in the current object's properties dictionary
            current_object["properties"][prop_name] = {
                "type": prop_type,
                "values": prop_values
            }
    
    return parsed_objects
