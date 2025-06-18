from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.agents import ChatAgent
from tools import genes_articles_tool, aberowl_hpo_tool, phenotypes_articles_tool
from tools import aberowl_hpo, genes_articles, phenotypes_articles

def generate_interpretation(genes: str, phenotypes: str, model_type="deepseek/deepseek-chat-v3-0324:free") -> str:
    model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENROUTER,
    model_type=model_type,
    #model_type="google/gemini-2.5-pro-preview",
    #model_type="google/gemini-2.0-flash-001",
    model_config_dict={"temperature": 0.3, "max_tokens": 100000},
    )

    gl_agent = ChatAgent(
        system_message="You are a clinical geneticist analyzing research about "
        "genetic variants and rare diseases. Based on the articles tool and background knowledge of phenotypes",
        model=model)

    genes_agent = ChatAgent(
        system_message="You are a helpful assistant that retrieves articles related to genes.",
        tools=[genes_articles_tool,],
        model=model)

    aberowl_pheno_agent = ChatAgent(
        system_message="You are a helpful assistant that retrieves articles and background knowledge related to phenotypes.",
        tools=[aberowl_hpo_tool,],
        model=model)

    pubmed_pheno_agent = ChatAgent(
        system_message="You are a helpful assistant that retrieves articles to phenotypes.",
        tools=[phenotypes_articles_tool,],
        model=model)

    response = pubmed_pheno_agent.step(
        f"""Retrieve articles about the following phenotypes: {phenotypes}.
Generate a context for the model for each phenotype based on articles or your knowledge.""")
    pheno_articles = response.msgs[0].content
    response = aberowl_pheno_agent.step(
        f"""Retrieve background knowledge about the following phenotypes: {phenotypes}.
Generate a context for the model for each phenotype based on AberOWL or your knowledge.""")
    background_knowledge = response.msgs[0].content
    response = genes_agent.step(
        f"""Retrieve articles related to the following genes: {genes}.
Generate a context for the model for each gene based on the articles or your knowledge.""")
    articles = response.msgs[0].content

    # Uncomment for the models that do not support tools
    # background_knowledge = ""
    # for pheno in phenotypes.split(','):
    #     background_knowledge += aberowl_hpo(pheno.strip())
    # pheno_articles = phenotypes_articles(phenotypes)
    # articles = genes_articles(genes)

    response = gl_agent.step(
        f"""Genes context:\n {articles} \n\n
Phenotype articles context:\n{pheno_articles} \n\n
Phenotypes context:\n{background_knowledge} \n\n
Rank the following genes {genes} that are directly or indirectly associated with phenotypes: {phenotypes}. 
Generate interpretation for each gene in the following format:
Rank: <rank>
Gene: <gene_name>
Interpretation: <interpretation>""")
    interpretation = response.msgs[0].content
    return interpretation

def test_gl_agent():
    test_genes = "IL16, LRIG1, HSPA4, CALU, TAAR3P, HRES1, PPFIBP2, CALML6, PTN, CYP2D6, NDC80, TRBV7-6, MYO5C, GALNT12, PREP, UBC, LINC00471, HMBS, CDH20, PCDHA6, PPP1R2B, RTTN, CYP2U1, OR5B3, RCN3, LCP1, ZNF274, IL37, GSTA2, ADGRF4, CYB561, TRBV7-9, TRPM5, CBX8, TEX11, MRPL2"
    test_phenotypes = "Microcephaly, Delayed speech and language development, Abnormality of toe, Prominent nasal bridge, 2-3 toe syndactyly, Overlapping toe, Abnormality of skin pigmentation, Pectus excavatum"
    #test_phenotypes ="Progressive pes cavus, Intellectual disability, Peripheral axonal neuropathy"
    #test_genes = "CAPZA2, KCNH8, DYNLRB2, SLC9C2, UBE2G2, CHGA, MOK, SAMD8, CCDC54, FOXQ1, H2BC18, TIAL1, ZNF117, PRPF19, NPHS1, KCNJ13, SHQ1, OR2B8, SLC5A6, SLC2A9, GK, AP4M1, NOL8, ATF6, SMARCA2, APOC3, MYOD1, JCAD, RBPMS2, RPTOR, HSPG2, ZCCHC9, OSR2, RTP1, TRGC2, USP17L17, SPATA2L, FTMT, INE1, BCE1, SLC39A14, CENPC, TMEM248, UQCRC2, FIRRM, SDCBP2, SGK1, C3orf49, UNC13A, UBTF, MYH9, ZNF181, ASTE1, RDX, CBLN4, ADH1B, DCTN6, CABCOCO1, COX16, GART, HNRNPH1, IL17F, SLC39A7, ISL1, IGLV2-23, TNFRSF8, RASL12, PXYLP1, CLDN2, CASP10, RGS9, SH2B2, GNAO1, OCIAD1, RSL24D1, NRG1, PGM3, EXOC1, LONRF1, GPATCH1, CFAP70, DEFA5, ACTB, SLC17A4, OR6A2, VCX2, C3AR1, SLC7A1, OR5D13, SPANXN4, LIPT1, WDR83, TRAV20, GLB1L3, OR1S2, TFCP2L1, INTS5, ASAH2B, CRYBA4, CRELD1, TAS2R45, FNDC5, CCDC92, MED24, ATP2A3, GEMIN8, PKLR, BCL2L11, PRODH, MFSD3, ZDHHC7, SLX1A, GDPD2, ULK1"
    interpretation = generate_interpretation(test_genes, test_phenotypes)
    print(f"Genes: {test_genes}\nPhenotype: {test_phenotypes}")
    print(f"Answer:\n{interpretation}")

if __name__ == "__main__":
    test_gl_agent()