import pandas as pd
import json


#########################################################################
# Utility functions 
#########################################################################

def utility_model_json_to_model_dict(json_string, model_key='model'):   
    """ Converts a "model_json" json_string into a model dictionary.

    Args: 
        json_string: a provided string that can be parsed into json using 'json.loads'. This should be valid model json.

        model_key: Optional, default 'model'. The key of the inner dictionary that contains the model parameters. Model json has keys for each criteria value and the 'model' itself. If this is user-created and the model parameter is at the top level, this can be set to None.

    Returns:

        A dictionary mapping model parameters to values. Values for single entries are 'flattened' so that the value can be accessed immediately by the parameter name. Tables are returned as a list of dictionaries - this can be converted to a pandas table easily.         
    """
    
    # Convert the json string to a python dictionary with `json.loads`
    json_dict = json.loads(json_string)
    
    # The parameters are contained in the 'model' key in this dictionary
    # If this is created by other code it may not have this key, set to 'None'
    # these are contained in a flat list of key value pairs
    if model_key is None:
        model_list = json_dict
    else:
        model_list = json_dict[model_key]
    
    # We can convert the list of key value pairs into a dictionary, assuming they are unique
    model_dict = utility_model_list_to_model_dict(model_list)   
                                                 
    return model_dict

def utility_model_list_to_model_dict(model_list):
    """ Converts a "model_list" of model parameters into a model parameter dictionary.

    Args: 
        model_list: A list of dictionaries with model parameters, that are key-value pairs 'name' and 'values'.

    Returns:

        A dictionary version of the listed parameters. Values for single entries are 'flattened' so that the value can be accessed immediately by the parameter name.
               
    """
    # We can convert the list of key value pairs into a dictionary, assuming they are unique
    model_dict = { d['name']: d['values'] for d in model_list }   
     
    model_dict = utility_model_dict_flatten_single_values(model_dict)
                                                    
    return model_dict

def utility_model_dict_flatten_single_values(model_dict):
    """ Takes a "model_dict" of model parameters and indentifies 'single' parameters.

    Args: 
        model_dict: A dictionary containing model parameters, that are key-value pairs 'name' and 'values' 

    Returns:

        A dictionary version of the listed parameters. Values for single entries are 'flattened' so that the value can be accessed immediately by the parameter name. These may be classed as 'single' parameters, if and only if 1) They are a list of length 1 and b) the dictionary contains the single key 'Value' or 'value'. Otherwise, the entries are left as they are.
               
    """
    # Convert Single parameters to dictionary entries, rather that a list of one dict entry
    # So can be accessed as "dict[k]" and not the unwieldy "dict[k][0]['value']""  
    for k in model_dict:
        if len(model_dict[k]) == 1:            
            entry = model_dict[k][0]            
            # Both casing options for 'Value' or 'value' should be considered
            if entry.keys()=={'value'}:
                model_dict[k] = model_dict[k][0]['value']
            if entry.keys()=={'Value'}:
                model_dict[k] = model_dict[k][0]['Value']
                                                    
    return model_dict

# And we will need the inverse of this function to re-pack
def utility_model_dict_to_model_json(model_dict):
    """ Takes a valid "model_dict" of model parameters repacks this as a 'model_json' string.

    Args: 
        model_dict: A dictionary of 'name' keys and and inner 'values', which may be a 'single' parameter (a non-iterable object) or a list of key-value dictionaries (representing a table).

    Returns:

        A 'model_json' list of dictionaries of the prepared dictionary. The model_dict is prepared first by expanding any 'single' parameters back into the expected pattern for a single value - (a list of length 1 and containing a dictionary with the single key 'Value'. This can be converted to a json string using 'json.dumps()' which will be the correct format to send back as a Model.
               
    """   
    json_list = []
    for k in model_dict:
        if isinstance(model_dict[k], pd.DataFrame):            
            entry = model_dict[k].to_dict('records')
        else:
            entry = [{'Value':model_dict[k]}]
        
        json_list.append({'name':k,'values':entry})
                                                 
    return json_list
