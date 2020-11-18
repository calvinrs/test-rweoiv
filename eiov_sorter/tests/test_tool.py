## Tests
import pytest
from pytest import approx

## Tested data
from eiov_sorter.tool import eoiv_tool

from eiov_sorter.utility import utility_model_list_to_model_dict, utility_model_json_to_model_dict, utility_model_dict_flatten_single_values

import numpy as np
import json
import pandas as pd
import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

## End-to-end test
class TestToolRunUSDPreEndSept:

	@pytest.fixture(autouse=True)
	def return_E_USD_EndSep2020_Models_toolrun(self):

		# Test against E_USD_EndSep2020 - this is pre-update
		with open(os.path.join(THIS_DIR,'E_USD_EndSep2020_Models.json')) as json_file:
			dfdict = json.load(json_file)
		# Get the combined Models JSON from the dictionary
		model_dict = json.loads(dfdict['E_USD'])
		# Tool result
		output_model = eoiv_tool(model_dict)
		# Unpcack into parameter dictionary
		output_dict = utility_model_list_to_model_dict(json.loads(output_model)['Output'])

		self._output_dict = output_dict

	def test_E_USD_maxnegativeIV(self):

		output_dict = self._output_dict

		assert output_dict['Prob.NegativeIV.IVInf'] == approx(9.88072190993451e-11), "Probability output as expected"

	def test_E_USD_constants(self):

		output_dict = self._output_dict
		
		niv_constants = pd.DataFrame(output_dict['Prob.NegativeIV.DerivedConstants']).set_index('Name')

		consts_array = niv_constants.loc[['gamma_k','gamma_theta','sigma_J2','variance_mean','variance_var','nu_infty','parameter_a','parameter_b'],'Value'].to_numpy()

		expected_consts = np.array([	
			0.584103727767667,
			0.031541979614842,
			0.001310647989134,
			0.023107331271355,
			5.811227415562155e-04,
			0.017520020977745,
			0.005994191386288,
			-0.137224884648809])

		assert consts_array == approx(expected_consts), "All constants match expected values"
