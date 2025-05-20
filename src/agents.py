from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.agents import ChatAgent
from tools import gene_articles_tool

model = ModelFactory.create(
  model_platform=ModelPlatformType.OPENROUTER,
  model_type="google/gemini-2.5-pro-preview",
  model_config_dict={"temperature": 0.3, "max_tokens": 100000},
)

gl_agent = ChatAgent(
    system_message="You are a clinical geneticist analyzing research about genetic variants and rare diseases. Based on the scientific articles",
    tools=[gene_articles_tool],
    model=model)

def test_gl_agent():
    test_genes = "BRCA1, TP53"
    test_phenotypes = "breast cancer"
    response = gl_agent.step(
        f"""Rank the following genes {test_genes} and interpret the evidence for {test_phenotypes}.""")
    interpretation = response.msgs[0].content
    print(f"Genes: {test_genes}, Phenotype: {test_phenotypes}")
    print(f"Answer: {interpretation}")

if __name__ == "__main__":
    test_gl_agent()