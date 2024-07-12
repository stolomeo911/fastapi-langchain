#
# Do not touch!
# This dummy llm ignores user input and just returns randomly one of the entries below
#
import json
from typing import Any, List, Optional

from langchain.llms.fake import FakeListLLM
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import LanguageModelInput

entries = [
    {
        "answer": "The paper introduces generative agents, computational software that simulates credible human behavior. These agents perform daily activities, interact with each other, form opinions, and even remember past events. An architecture is proposed that uses a large language model to record the agent's experiences as natural language, synthesize them into higher-level thoughts, and uses these memories to plan their behavior. These agents are applied in an interactive environment where users can communicate with them using natural language. In a test, these agents autonomously planned and attended a Valentine’s Day party, demonstrating their realistic individual and social behaviors. The architectural elements (observation, planning, and reflection) contribute critically to their authenticity. This research introduces interaction patterns and architectural structures for enabling believable simulations of human behavior.",
        "sources": [
            "arxiv.org/abs/2304.03442v1",
            "github.com/joonspk-research/generative_agents",
        ],
    },
    {
        "answer": "This paper introduces a new network architecture, the Transformer, which relies solely on attention mechanisms, eliminating the need for complex recurrent or convolutional neural networks in sequence transduction models. The Transformer has been shown to be superior in quality, more parallelizable, and requires significantly less training time. In tests on English-to-German and English-to-French translation tasks, the Transformer achieved better results than existing models, including ensembles, with improved BLEU scores and reduced training costs. The paper also shows that the Transformer generalizes well to other tasks, as demonstrated by successful applications to English constituency parsing with both large and limited training data.",
        "sources": ["arxiv.org/abs/1706.03762"],
    },
    {
        "answer": """This paper introduces DSPy, a programming model that reimagines language model (LM) pipelines as text transformation graphs, moving away from the hard-coded "prompt templates". DSPy modules are parameterizable, allowing them to learn and apply techniques such as prompting, fine-tuning, augmentation, and reasoning. A compiler is designed to optimize any DSPy pipeline for a particular metric. Case studies show that DSPy can optimize complex LM pipelines to reason about math problems, answer complex questions, and more. When compiled, DSPy allows models like GPT-3.5 and llama2-13b-chat to self-bootstrap pipelines that significantly outperform standard methods and expert-created demonstrations.""",
        "sources": ["arxiv.org/abs/2310.03714", "github.com/stanfordnlp/dspy"],
    },
    {
        "answer": "The paper presents the first model-stealing attack that extracts detailed information from black-box language models like OpenAI's ChatGPT or Google's PaLM-2. The attack recovers the transformer model's embedding projection layer using typical API access. For less than $20, the attack extracts the entire projection matrix of OpenAI's Ada and Babbage language models, confirming for the first time their hidden dimensions of 1024 and 2048, respectively. The attack also determines the hidden dimension size of the gpt-3.5-turbo model, estimating a cost of less than $2000 to recover its entire projection matrix. The paper concludes with potential defenses, mitigations, and discussion on future implications.",
        "sources": ["arxiv.org/abs/2403.06634"],
    },
]


class MyFakeLLM(FakeListLLM):
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Return next response"""
        response = json.loads(self.responses[self.i])
        prompt_len = len(prompt.split())
        # print(prompt_len)
        if self.i < len(self.responses) - 1:
            self.i += 1
        else:
            self.i = 0
        response["answer"] = f"{response['answer']}"
        return json.dumps(response)


llm = MyFakeLLM(responses=[json.dumps(entry) for entry in entries])
