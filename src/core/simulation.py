# -*- coding:utf-8 -*-
#
# This file is part of OpenFisca.
# OpenFisca is a socio-fiscal microsimulation software
# Copyright © 2011 Clément Schaff, Mahdi Ben Jelloul
# Licensed under the terms of the GVPLv3 or later license
# (see openfisca/__init__.py for details)


from datetime import datetime
import gc
import os
from src.core.datatable import DataTable, SystemSf
from src.parametres.paramData import XmlReader, Tree2Object
from src.core.utils_old import gen_output_data, of_import
from src import SRC_PATH

from pandas import DataFrame

from src.plugins.scenario.graph import drawTaux, drawBareme, drawBaremeCompareHouseholds


__all__ = ['Simulation', 'ScenarioSimulation', 'SurveySimulation' ]

class Simulation(object):
    """
    A simulation object contains all parameters to compute a simulation from a 
    test-case household (scenario) or a survey-like data 
    
    See also
    --------
    ScenarioSimulation, SurveySimulation 
    """
    def __init__(self):
        super(Simulation, self).__init__()
        self.reforme = False   # Boolean signaling reform mode 
        self.country = None    # String denoting the country 
        self.datesim = None
        self.P = None
        self.P_default = None
        self.totaux_file = None
        self.param_file = None
        
    def _set_config(self, **kwargs):
        """
        Sets some general Simulation attributes 
        """
        remaining = kwargs.copy()
        
        for key, val in kwargs.iteritems():
            if key == "year":
                date_str = str(val)+ '-01-01'
                self.datesim = datetime.strptime(date_str ,"%Y-%m-%d").date()
                remaining.pop(key)
                
            elif key in ['country', 'param_file', 'totaux_file']:
                if hasattr(self, key):
                    setattr(self, key, val)
                    remaining.pop(key)
                    
        if self.country is None:
            self.country = 'france'
            if "country" in remaining:
                remaining.pop('country')
    
        if self.param_file is None:
            if self.country is not None:
                self.param_file = os.path.join(SRC_PATH, 'countries', self.country, 'param', 'param.xml')
                
        if self.totaux_file is None:
            if self.country is not None:
                self.totaux_file = os.path.join(SRC_PATH, 'countries', self.country, 'totaux.xml')

        # Sets required country specific classes
        if self.country is not None:            
            self.InputTable = of_import('model.data', 'InputTable', country=self.country)
            self.ModelSF = of_import('model.model', 'ModelSF', country=self.country)        

        # TODO: insert definition of fam foy , QUIMEN QUIFOY etc etc here !

        return remaining
                        
    def set_param(self, param=None, param_default=None):
        """
        Sets the parameters of the simulation
        
        Parameters
        ----------
        
        param : a socio-fiscal parameter object to be used in the microsimulation. 
                By default, the method uses the one provided by the attribute param_file
        param_default : a socio-fiscal parameter object to be used 
                in the microsimulation to compute some gross quantities not available in the initial data. 
                parma_default is necessarily different from param when examining a reform
        """
        reader = XmlReader(self.param_file, self.datesim)
        rootNode = reader.tree

        if param_default is None:
            self.P_default = Tree2Object(rootNode, defaut=True)
            self.P_default.datesim = self.datesim
        else:
            self.P_default = param_default
            
        if param is None:
            self.P = Tree2Object(rootNode, defaut=False)
            self.P.datesim = self.datesim
        else:
            self.P = param
            
              
    def compute(self):
        NotImplementedError          
        
    def _preproc(self, input_table):
        """
        Prepare the output values according to the ModelSF definitions/Reform status/input_table
        """
        P_default = self.P_default     
        P         = self.P                 
        output = SystemSf(self.ModelSF, P, P_default, datesim = self.datesim, country = self.country)
        output.set_inputs(input_table, country = self.country)
                
        if self.reforme:
            output_default = SystemSf(self.ModelSF, P_default, P_default, datesim = self.datesim, country = self.country)
            output_default.set_inputs(input_table, country = self.country)
        else:
            output_default = output
    
        return output, output_default


    def clear(self):
        NotImplementedError
  
class ScenarioSimulation(Simulation):
    """
    A Simulation class tailored to deal with scenarios
    """
    
    def __init__(self):
        super(ScenarioSimulation, self).__init__()    
        self.Scenario = None
        self.scenario = None
        self.alternative_scenario = None
        self.nmen = None
        self.xaxis = None
        self.maxrev = None
        self.mode = None
        self.same_rev_couple = False
        self.data = None
        self.data_default = None
       
    def set_config(self, **kwargs):
        """
        Configures the ScenarioSimulation
        
        Parameters
        ----------
        scenario : a scenario (by default, None selects Scenario())
        country  : a string containing the name of the country
        param_file : the socio-fiscal parameters file
        totaux_file : the totaux file
        xaxis : the revenue category along which revenue varies
        maxrev : the maximal value of the revenue
        same_rev_couple : divide the revenue equally between the two partners
        mode : 'bareme' or 'castype' TODO: change this 
        """
        
        specific_kwargs = self._set_config(**kwargs)
        self.Scenario = of_import('utils', 'Scenario', country = self.country)
        if self.scenario is None:
            try:                
                self.scenario = kwargs['scenario']
            except:
                self.scenario = self.Scenario()

        self.scenario.year = self.datesim.year
        
        for key, val in specific_kwargs.iteritems():        
            if hasattr(self, key):
                setattr(self, key, val)
        
        self.scenario.nmen   = self.nmen
        self.scenario.maxrev = self.maxrev
        self.scenario.xaxis  = self.xaxis
        self.scenario.same_rev_couple  = self.same_rev_couple

    def create_description(self):
        '''
        Creates a description dataframe of the ScenarioSimulation
        '''
        now = datetime.now()
        descr =  [u'OpenFisca', 
                         u'Calculé le %s à %s' % (now.strftime('%d-%m-%Y'), now.strftime('%H:%M')),
                         u'Système socio-fiscal au %s' % str(self.datesim)]
        # TODO: addd other parameters
        
        return DataFrame(descr)
    
    def reset_scenario(self):
        """
        Reset scenario and alternative_scenario to their default values 
        """
        if self.Scenario is not None:
            self.scenario = self.Scenario()
        self.alternative_scenario = None
        

    def set_alternative_scenario(self, scenario):
        """
        Set alternative-scenario
        
        Parameters
        ----------
        scenario : an instance of the class Scenario
        """
        self.alternative_scenario = scenario
        
    def set_marginal_alternative_scenario(self, unit = None, id_in_unit = None, variable = None, value = None):
        """
        Modifies scenario by changing the setting value of the variable of the individual with 
        position 'id' if necessary in unit named 'unit' 
        """
        self.alternative_scenario = self.scenario.copy()
        scenario = self.alternative_scenario
        if unit is not None:
            alt_unit = getattr(scenario, unit)
            if id_in_unit is not None:
                alt_unit[id_in_unit][variable] = value

    def compute(self, difference = True):
        """
        Computes output_data for the ScenarioSimulation
        
        Parameters
        ----------
        difference : boolean, default True
                When in reform mode, compute the difference between actual and default  
        
        
        Returns
        -------
        data, data_default : Computed data and possibly data_default according to totaux_file
        
        """
        
        alter = self.alternative_scenario is not None
        if self.reforme and alter:
            raise Exception("ScenarioSimulation: 'self.reforme' cannot be 'True' when 'self.alternative_scenario' is not 'None'") 

        input_table = DataTable(self.InputTable, scenario = self.scenario, datesim = self.datesim, country = self.country)
        if not alter:
            output, output_default = self._preproc(input_table)
        else:
            input_table_alter = DataTable(self.InputTable, scenario = self.alternative_scenario, datesim = self.datesim, country = self.country)
            output, output_default = self.preproc_alter_scenario(input_table_alter, input_table)
        
        data = gen_output_data(output, filename = self.totaux_file)
        
        if self.reforme or alter:
            output_default.reset()
            data_default = gen_output_data(output_default, filename = self.totaux_file) # TODO: take out gen_output_data form core.utils
            if difference:
                data.difference(data_default)            
        else:
            data_default = data

        self.data = data
        self.data_default = data_default
        return data, data_default

        
    def preproc_alter_scenario(self, input_table_alter, input_table):
        """
        Prepare the output values according to the ModelSF definitions and 
        input_table when an alternative scenario is present
        """
        P_default = self.P_default     
        P         = self.P         
                
        output = SystemSf(self.ModelSF, P, P_default, datesim = self.datesim, country = self.country)
        output.set_inputs(input_table, country = self.country)
                
        output_alter = SystemSf(self.ModelSF, P, P_default, datesim = self.datesim, country = self.country)
        output_alter.set_inputs(input_table_alter, country = self.country)
    
        return output_alter, output

    def get_results_dataframe(self, default = False, difference = True, index_by_code = False):
        """
        Formats data into a dataframe
        
        Parameters
        ----------
        default : boolean, default False
                  If True compute the default results
        difference :  boolean, default True
                  If True compute the default results
        index_by_code : boolean, default False
                  Index the row by the code instead of name of the different element
                  of totaux_file  
        
        Returns
        -------
        df : A DataFrame with computed data according to totaux_file
        """
        data, data_default = self.compute(difference = difference)
        
        data_dict = dict()
        index = []
        
        if default is True:
            data = data_default
        
        for row in data:
            if not row.desc in ('root'):
                if index_by_code is True:
                    index.append(row.code)
                    data_dict[row.code] = row.vals
                else:
                    index.append(row.desc)
                    data_dict[row.desc] = row.vals
                
        df = DataFrame(data_dict).T
        df = df.reindex(index)
        return df
        
    def draw_bareme(self, ax, graph_xaxis = None, legend = False, position = 1):
        """
        Draws a bareme on matplotlib.axes.Axes
        """
        reforme = self.reforme 
        alter = (self.alternative_scenario is not None)
        data, data_default = self.compute()
        data.setLeavesVisible()
        data_default.setLeavesVisible()
        if graph_xaxis is None:
            graph_xaxis = 'sal'
        if not alter:
            drawBareme(data, ax, graph_xaxis, reforme, data_default, legend, country = self.country)
        else:
            drawBaremeCompareHouseholds(data, ax, graph_xaxis, data_default, legend, country = self.country, position = position)
        
    def draw_taux(self, ax, graph_xaxis = None, legend = True):
        """
        Draws a bareme on matplotlib.axes.Axes object ax
        """
        reforme = self.reforme or (self.alternative_scenario is not None)
        data, data_default = self.compute()
        data.setLeavesVisible()
        data_default.setLeavesVisible()
        if graph_xaxis is None:
            graph_xaxis = 'sal'
        drawTaux(data, ax, graph_xaxis, reforme, data_default, legend = legend, country = self.country)
        
        
        

class SurveySimulation(Simulation):
    """
    A Simulation class tailored to deal with survey data
    """
    def __init__(self):
        super(SurveySimulation, self).__init__()
        
        self.survey = None
        self.descr = None
        self.outputs = None
        self.outputs_default = None
  
        self.label2var = dict()
        self.var2label = dict()
        self.var2enum  = dict() 

    
    def set_config(self, **kwargs):
        """
        Configures the SurveySimulation
        
        """
        # Setting general attributes and getting the specific ones
        specific_kwargs = self._set_config(**kwargs)

        for key, val in specific_kwargs.iteritems():        
            if hasattr(self, key):
                setattr(self, key, val)
  
    def set_survey(self, filename = None, datesim = None, country = None):
        """
        Set survey input data
        """
        if self.datesim is not None:
            datesim = self.datesim        
        elif datesim is not None:
            datesim = datesim 
            
        if self.country is not None:
            country = self.country        
        elif country is not None:
            country = country
            
        if filename is None:
            if country is not None:
                filename = os.path.join(SRC_PATH, 'countries', country, 'data', 'survey.h5')
        
        self.survey = DataTable(self.InputTable, survey_data = filename, datesim = datesim, country = country)

        self._build_dicts(option = 'input_only')

    def inflate_survey(self, inflators):
        """
        Inflate some variable of the survey data
        
        Parameters
        ----------
        
        inflators : dict or DataFrame which keys or variable column contains the variable to inflate 
        and values of the value column the value of the inflator
        """
        
        if isinstance(inflators, DataFrame):
            for varname in inflators['variable']:
                inflators.set_index('variable')
                inflator = inflators.get_value(varname, 'value')
                self.survey.inflate(varname, inflator)
        if isinstance(inflators, dict):
            for varname, inflator in inflators.iteritems():
                self.survey.inflate(varname, inflator)

    def compute(self):
        """
        Computes output_data from scenario
        """            
        # Clear outputs
        self.clear()
        gc.collect()
        self.outputs, self.outputs_default = self._calculate_all()
        self._build_dicts(option = 'output_only')

    def aggregated_by_household(self, varlist = None, all_output_vars = True, all_input_vars = False):
        """
        Generates aggregates at the household level ('men')
        """
        if self.outputs is None:
            raise Exception('self.outputs should not be None')
        
        models = [self.outputs]
        if self.reforme is True:
            models.append(self.outputs_default) 
        
        out_tables = []
        
        for model in models:
            out_dct = {}
            inputs = model._inputs
            unit = 'men'
            idx = model.index[unit]
            enum = inputs.description.get_col('qui'+unit).enum
            people = [x[1] for x in enum]

            input_varlist = set(['wprm'])
            if all_input_vars:           
                input_varlist = input_varlist.union(set(inputs.col_names))
            if varlist is not None:
                input_varlist = input_varlist.union( set(inputs.col_names).intersection(varlist))
 
            if varlist is not None:
                output_varlist = set(model.col_names).intersection(varlist)
            if all_output_vars:
                output_varlist = set(model.col_names)
                
            varnames = output_varlist.union(input_varlist)
            for varname in varnames:
                if varname in model.col_names:
                    if model.description.get_col(varname)._unit != unit:
                        val = model.get_value(varname, idx, opt = people, sum_ = True)    
                    else:
                        val = model.get_value(varname, idx)
                elif varname in inputs.col_names:
                    val = inputs.get_value(varname, idx)
                else:
                    raise Exception('%s was not find in model nor in inputs' % varname)
                
                out_dct[varname] = val      
            # TODO: should take care the variables that shouldn't be summed automatically
            
            out_tables.append(DataFrame(out_dct))
        
        if self.reforme is False:
                out_tables.append(None)
                
        return out_tables[0], out_tables[1]


    def _calculate_all(self):
        """
        Compute all prestations
        
        Returns
        -------
        output, output_default
        """
        input_table = self.survey
        output, output_default = self._preproc(input_table)
        
        output.calculate()
        if self.reforme:
            output_default.reset()
            output_default.calculate()
        else:
            output_default = output

        return output, output_default

    def clear(self):
        """
        Clear the outputs table 
        """
        self.survey_outputs = None
        self.survey_outputs_default = None
        
    @property
    def input_var_list(self):
        """
        List of input survey variables
        
        Returns
        -------
        survey.description.col_names : List of input survey variables 
        """
        return self.survey.description.col_names
        
    @property
    def output_var_list(self):
        """
        List of output survey variables
        """
        return self.outputs.description.col_names
        
    @property
    def var_list(self):
        """
        List of variables pesent in survey and output
        """
        try:
            return list(set(self.survey.description.col_names).union(set(self.outputs.description.col_names)))
        except:
            return list(set(self.survey.description.col_names))

    def _build_dicts(self, option = None):
        """
        Builds dictionaries from description
        """
        try:
            if option is 'input_only':
                descriptions = [self.survey.description]
            elif option is 'output_only': 
                descriptions = [self.outputs.description]
            else:
                descriptions = [self.survey.description, self.outputs.description] 
        except:
            descriptions = [self.survey.description]
        
        for description in descriptions:
            l2v, v2l, v2e = description.builds_dicts()
            self.label2var.update(l2v)
            self.var2label.update(v2l)
            self.var2enum.update(v2e)
