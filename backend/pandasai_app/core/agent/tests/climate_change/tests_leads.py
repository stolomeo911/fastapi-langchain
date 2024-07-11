import unittest
from backend.pandasai_app.core.agent.pandasai_agent import get_agent
import pandas as pd
import yaml
from yaml import Loader
import warnings
warnings.simplefilter('ignore')
from shared_libraries.utils import setup_logger

logger = setup_logger(__name__)


class AgentUnitTestLeads(unittest.TestCase):
    def setUp(self):
        # Set up any resources or configurations needed for your tests
        # This method will be called before each tests case
        # Create sample data for testing
        self.agent = get_agent()
        config = yaml.load(open('backend/pandasai_app/core/agent/training/config.yml'), Loader=Loader)
        self.config = config
        with open('backend/pandasai_app/core/agent/tests/climate_change/questions.yml') as file:
            self.questions = yaml.load(file, Loader=Loader)['questions']

    def tearDown(self):
        # Clean up any resources after your tests (if needed)
        # This method will be called after each tests case
        pass

    def test_leads_number_in_2024(self):
        #df = pd.read_pickle(self.config['pickle_path'])
        #leads_2024 = df[df['lead_timestamp'].dt.year == 2024]['contact_id'].nunique()
        response = self.agent.chat(self.questions['top_country_with_temp_increase'])
        print(response)
        #self.assertEquals(leads_2024, response)