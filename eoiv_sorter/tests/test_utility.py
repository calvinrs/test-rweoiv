import pytest

from eoiv_sorter.utility import utility_model_json_to_model_dict
from eoiv_sorter.utility import utility_model_list_to_model_dict
from eoiv_sorter.utility import utility_model_dict_to_model_json

### Test values

test_json_string = '{"calibrationDate": "2020-09-30", "model": [{"name": "FactorVols.All", "values": [{"term": "1", "value": "0.974283407986904"}, {"term": "2", "value": "-1.8318607429997"}, {"term": "3", "value": "-1.01153078398766"}, {"term": "4", "value": "-0.343088219297554"}, {"term": "5", "value": "0.408032510787871"}, {"term": "6", "value": "0"}]}, {"name": "BE_E_Beta_f1", "values": [{"value": "0.974283407986904"}]}, {"name": "BE_E_Beta_f2", "values": [{"value": "-1.8318607429997"}]}, {"name": "BE_E_Beta_f3", "values": [{"value": "-1.01153078398766"}]}, {"name": "BE_E_Beta_f4", "values": [{"value": "-0.343088219297554"}]}, {"name": "BE_E_Beta_f5", "values": [{"value": "0.408032510787871"}]}, {"name": "BE_E_Beta_f6", "values": [{"value": "0"}]}], "toolRunId": null, "toolRunGuid": "3ec307d7-4bb1-4f94-a091-0bbe5d66e225", "format": "Structured", "isPersistent": false}'

test_json_string_model_direct = '[{"name": "FactorVols.All", "values": [{"term": "1", "value": "0.974283407986904"}, {"term": "2", "value": "-1.8318607429997"}, {"term": "3", "value": "-1.01153078398766"}, {"term": "4", "value": "-0.343088219297554"}, {"term": "5", "value": "0.408032510787871"}, {"term": "6", "value": "0"}]}, {"name": "BE_E_Beta_f1", "values": [{"value": "0.974283407986904"}]}, {"name": "BE_E_Beta_f2", "values": [{"value": "-1.8318607429997"}]}, {"name": "BE_E_Beta_f3", "values": [{"value": "-1.01153078398766"}]}, {"name": "BE_E_Beta_f4", "values": [{"value": "-0.343088219297554"}]}, {"name": "BE_E_Beta_f5", "values": [{"value": "0.408032510787871"}]}, {"name": "BE_E_Beta_f6", "values": [{"value": "0"}]}]'

test_model_dict = {'FactorVols.All': [{'term': '1', 'value': '0.974283407986904'},
  {'term': '2', 'value': '-1.8318607429997'},
  {'term': '3', 'value': '-1.01153078398766'},
  {'term': '4', 'value': '-0.343088219297554'},
  {'term': '5', 'value': '0.408032510787871'},
  {'term': '6', 'value': '0'}],
 'BE_E_Beta_f1': '0.974283407986904',
 'BE_E_Beta_f2': '-1.8318607429997',
 'BE_E_Beta_f3': '-1.01153078398766',
 'BE_E_Beta_f4': '-0.343088219297554',
 'BE_E_Beta_f5': '0.408032510787871',
 'BE_E_Beta_f6': '0'}

test_model_list = [{'name': 'FactorVols.All',
  'values': [{'term': '1', 'value': '0.974283407986904'},
   {'term': '2', 'value': '-1.8318607429997'},
   {'term': '3', 'value': '-1.01153078398766'},
   {'term': '4', 'value': '-0.343088219297554'},
   {'term': '5', 'value': '0.408032510787871'},
   {'term': '6', 'value': '0'}]},
 {'name': 'BE_E_Beta_f1', 'values': [{'value': '0.974283407986904'}]},
 {'name': 'BE_E_Beta_f2', 'values': [{'value': '-1.8318607429997'}]},
 {'name': 'BE_E_Beta_f3', 'values': [{'value': '-1.01153078398766'}]},
 {'name': 'BE_E_Beta_f4', 'values': [{'value': '-0.343088219297554'}]},
 {'name': 'BE_E_Beta_f5', 'values': [{'value': '0.408032510787871'}]},
 {'name': 'BE_E_Beta_f6', 'values': [{'value': '0'}]}]

test_model_list_PascalCase = [{'name': 'FactorVols.All',
  'values': [{'term': '1', 'value': '0.974283407986904'},
   {'term': '2', 'value': '-1.8318607429997'},
   {'term': '3', 'value': '-1.01153078398766'},
   {'term': '4', 'value': '-0.343088219297554'},
   {'term': '5', 'value': '0.408032510787871'},
   {'term': '6', 'value': '0'}]},
 {'name': 'BE_E_Beta_f1', 'values': [{'Value': '0.974283407986904'}]},
 {'name': 'BE_E_Beta_f2', 'values': [{'Value': '-1.8318607429997'}]},
 {'name': 'BE_E_Beta_f3', 'values': [{'Value': '-1.01153078398766'}]},
 {'name': 'BE_E_Beta_f4', 'values': [{'Value': '-0.343088219297554'}]},
 {'name': 'BE_E_Beta_f5', 'values': [{'Value': '0.408032510787871'}]},
 {'name': 'BE_E_Beta_f6', 'values': [{'Value': '0'}]}]

test_model_dict_unflattened = {'FactorVols.All': [{'term': '1', 'value': '0.974283407986904'},
  {'term': '2', 'value': '-1.8318607429997'},
  {'term': '3', 'value': '-1.01153078398766'},
  {'term': '4', 'value': '-0.343088219297554'},
  {'term': '5', 'value': '0.408032510787871'},
  {'term': '6', 'value': '0'}],
 'BE_E_Beta_f1': [{'value': '0.974283407986904'}],
 'BE_E_Beta_f2': [{'value': '-1.8318607429997'}],
 'BE_E_Beta_f3': [{'value': '-1.01153078398766'}],
 'BE_E_Beta_f4': [{'value': '-0.343088219297554'}],
 'BE_E_Beta_f5': [{'value': '0.408032510787871'}],
 'BE_E_Beta_f6': [{'value': '0'}]}

test_model_list_entrytables = [{'name': 'FactorVols.All',
  'values': [{'term': '1', 'value': '0.974283407986904'},
   {'term': '2', 'value': '-1.8318607429997'},
   {'term': '3', 'value': '-1.01153078398766'},
   {'term': '4', 'value': '-0.343088219297554'},
   {'term': '5', 'value': '0.408032510787871'},
   {'term': '6', 'value': '0'}]},
 {'name': 'BE_E_Beta_f1', 'values': [{'entry': '0.974283407986904', 'Value': '-0.343088219297554'}]},
 {'name': 'BE_E_Beta_f2', 'values': [{'entry': '-1.8318607429997'}]},
 {'name': 'BE_E_Beta_f3', 'values': [{'value': '-1.01153078398766', 'Value': '-1.01153078398766'}]},
 {'name': 'BE_E_Beta_f4', 'values': [{'Value': '-0.343088219297554'}]},
 {'name': 'BE_E_Beta_f5', 'values': [{'Valooo': '0.408032510787871'}]},
 {'name': 'BE_E_Beta_f6', 'values': [{'entry': '0'}]}]

test_model_dict_entrytables = {'FactorVols.All': [{'term': '1', 'value': '0.974283407986904'},
  {'term': '2', 'value': '-1.8318607429997'},
  {'term': '3', 'value': '-1.01153078398766'},
  {'term': '4', 'value': '-0.343088219297554'},
  {'term': '5', 'value': '0.408032510787871'},
  {'term': '6', 'value': '0'}],
 'BE_E_Beta_f1': [{'entry': '0.974283407986904',
   'Value': '-0.343088219297554'}],
 'BE_E_Beta_f2': [{'entry': '-1.8318607429997'}],
 'BE_E_Beta_f3': [{'value': '-1.01153078398766',
   'Value': '-1.01153078398766'}],
 'BE_E_Beta_f4': '-0.343088219297554',
 'BE_E_Beta_f5': [{'Valooo': '0.408032510787871'}],
 'BE_E_Beta_f6': [{'entry': '0'}]}

test_out_model_json = [{'name': 'FactorVols.All',
  'values': [{'Value': [{'term': '1', 'value': '0.974283407986904'},
     {'term': '2', 'value': '-1.8318607429997'},
     {'term': '3', 'value': '-1.01153078398766'},
     {'term': '4', 'value': '-0.343088219297554'},
     {'term': '5', 'value': '0.408032510787871'},
     {'term': '6', 'value': '0'}]}]},
 {'name': 'BE_E_Beta_f1', 'values': [{'Value': '0.974283407986904'}]},
 {'name': 'BE_E_Beta_f2', 'values': [{'Value': '-1.8318607429997'}]},
 {'name': 'BE_E_Beta_f3', 'values': [{'Value': '-1.01153078398766'}]},
 {'name': 'BE_E_Beta_f4', 'values': [{'Value': '-0.343088219297554'}]},
 {'name': 'BE_E_Beta_f5', 'values': [{'Value': '0.408032510787871'}]},
 {'name': 'BE_E_Beta_f6', 'values': [{'Value': '0'}]}]

test_out_model_json_entrytables = [{'name': 'FactorVols.All',
  'values': [{'Value': [{'term': '1', 'value': '0.974283407986904'},
     {'term': '2', 'value': '-1.8318607429997'},
     {'term': '3', 'value': '-1.01153078398766'},
     {'term': '4', 'value': '-0.343088219297554'},
     {'term': '5', 'value': '0.408032510787871'},
     {'term': '6', 'value': '0'}]}]},
 {'name': 'BE_E_Beta_f1',
  'values': [{'Value': [{'entry': '0.974283407986904',
      'Value': '-0.343088219297554'}]}]},
 {'name': 'BE_E_Beta_f2',
  'values': [{'Value': [{'entry': '-1.8318607429997'}]}]},
 {'name': 'BE_E_Beta_f3',
  'values': [{'Value': [{'value': '-1.01153078398766',
      'Value': '-1.01153078398766'}]}]},
 {'name': 'BE_E_Beta_f4', 'values': [{'Value': '-0.343088219297554'}]},
 {'name': 'BE_E_Beta_f5',
  'values': [{'Value': [{'Valooo': '0.408032510787871'}]}]},
 {'name': 'BE_E_Beta_f6', 'values': [{'Value': [{'entry': '0'}]}]}]

 ### Tests

class TestModelJSONToModelDict:

	def test_utility_model_json_to_model_dict_default(self):

		out_model_dict = utility_model_json_to_model_dict(test_json_string)

		assert test_model_dict == out_model_dict, "The dictionary is as expected when the JSON has an inner 'model' key, and the 'model_key' parameter is allowed to be the default value"

	def test_utility_model_json_to_model_dict_given_model_key(self):

		out_model_dict_given_key = utility_model_json_to_model_dict(test_json_string, model_key='model')

		assert test_model_dict == out_model_dict_given_key, "The dictionary is as expected when the JSON has an inner 'model' key, and the 'model_key' parameter is passed the 'model' explicitly"

	def test_utility_model_json_to_model_dict_no_inner_key(self):

		out_model_direct_dict = utility_model_json_to_model_dict(test_json_string_model_direct, model_key=None)

		assert test_model_dict == out_model_direct_dict, "The dictionary is as expected when the JSON has no inner 'model' key (the parameter list is the immediate data), and the 'model_key' parameter is allowed to be the default value"

class TestModelListToModelDict:

	def test_utility_model_list_to_model_dict_default(self):

		out_model_direct_dict = utility_model_list_to_model_dict(test_model_list)

		assert test_model_dict == out_model_direct_dict, "The dictionary is as expected when the model list is passed"

	def test_utility_model_list_to_model_dict_empty_list(self):

		out_model_empty_dict = utility_model_list_to_model_dict([])

		assert {} == out_model_empty_dict, "The dictionary is as empty when the model list is empty"
	
	def test_utility_model_list_to_model_dict_PascalCase_Values(self):

		out_model_pascal_dict = utility_model_list_to_model_dict(test_model_list_PascalCase)

		assert test_model_dict == out_model_pascal_dict, "The dictionary is as expected when the inner single values use a PascalCase 'Value' rather than 'value'"

	def test_utility_model_list_to_model_dict_singles_not_values(self):

		out_model_direct_dict = utility_model_list_to_model_dict(test_model_list_entrytables)

		assert test_model_dict_entrytables == out_model_direct_dict, "The dictionary is as expected and ignores anything (returns the entry as-is) that does not match the pattern for a single value"

class TestModelDictToModelJSON:

	def utility_model_dict_to_model_json_flat(self):

		out_model_direct_dict = utility_model_dict_to_model_json(test_model_dict)

		assert test_out_model_json == out_model_direct_dict, "The model json list is as expected when the test dictionary is passed, where all single parameters have been 'flattened'"	

	def utility_model_dict_to_model_json_unflattened(self):

		out_model_direct_dict = utility_model_dict_to_model_json(test_model_dict_unflattened)

		assert test_out_model_json == out_model_direct_dict, "The model json list is as expected when the test dictionary is passed, where all single parameters have NOT been 'flattened'"

	def utility_model_dict_to_model_json_entrytables(self):

		out_model_direct_dict = utility_model_dict_to_model_json(test_model_dict_entrytables)

		assert test_out_model_json_entrytables == out_model_direct_dict, "The model json list is as expected when the test dictionary is passed, using the case where the single parameters are badly formed (so are treated as Tables)"