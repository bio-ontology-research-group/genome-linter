from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.agents import ChatAgent
from tools import genes_articles_tool, aberowl_hpo_tool

model = ModelFactory.create(
  model_platform=ModelPlatformType.OPENROUTER,
  model_type="google/gemini-2.0-flash-001",
  model_config_dict={"temperature": 0.3, "max_tokens": 1000000},
)

gl_agent = ChatAgent(
    system_message="You are a clinical geneticist analyzing research about "
    "genetic variants and rare diseases. Based on the articles tool and background knowledge of phenotypes",
    model=model,
    message_window_size=10)

genes_agent = ChatAgent(
    system_message="You are a helpful assistant that retrieves articles related to genes.",
    tools=[genes_articles_tool,],
    model=model,
    message_window_size=10)


pheno_agent = ChatAgent(
    system_message="You are a helpful assistant that retrieves background knowledge related to phenotypes from AberOWL.",
    tools=[aberowl_hpo_tool,],
    model=model)


def test_pheno_agent():
    test_phenotype = "breast carcinoma"
    response = pheno_agent.step(
        f"""Retrieve background knowledge about the phenotype {test_phenotype}.""")
    interpretation = response.msgs[0].content
    print(f"Phenotype: {test_phenotype}")
    print(f"Answer: {interpretation}")

def test_gl_agent():
    test_genes = "IL16, LRIG1, HSPA4, CALU, TAAR3P, HRES1, PPFIBP2, CALML6, PTN, CYP2D6, NDC80, TRBV7-6, MYO5C, GALNT12, PREP, UBC, LINC00471, HMBS, CDH20, PCDHA6, PPP1R2B, RTTN, CYP2U1, OR5B3, RCN3, LCP1, ZNF274, IL37, GSTA2, ADGRF4, CYB561, TRBV7-9, TRPM5, CBX8, TEX11, MRPL2"
    test_phenotypes = "Microcephaly, Delayed speech and language development, Abnormality of toe, Prominent nasal bridge, 2-3 toe syndactyly, Overlapping toe, Abnormality of skin pigmentation, Pectus excavatum"
    response = genes_agent.step(
        f"""Retrieve articles related to the following genes: {test_genes}.
Generate a context for the model for each gene based on the articles or your knowledge.""")
    articles = response.msgs[0].content
    print(articles)
    response = pheno_agent.step(
        f"""Retrieve background knowledge about the following phenotypes: {test_phenotypes}.
Generate a context for the model for each phenotype based on AberOWL or your knowledge.""")
    phenotypes = response.msgs[0].content
    print(phenotypes)
    response = gl_agent.step(
        f"""Genes context:\n {articles} \n
Phenotypes context:\n{phenotypes} \n
Rank the following genes {test_genes} that are directly or indirectly associated with phenotypes: {test_phenotypes}. 
Generate interpretation for each gene.""")
    interpretation = response.msgs[0].content
    print(f"Genes: {test_genes}\nPhenotype: {test_phenotypes}")
    print(f"Answer:\n{interpretation}")

if __name__ == "__main__":
    test_gl_agent()