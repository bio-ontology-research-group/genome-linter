#! /usr/bin/env python3

import json
import requests


url = 'https://amelie.stanford.edu/api/gene_list_api/'


def main():
    response = requests.post(
        url,
        verify=False,
        data={'patientName': 'Example patient',
              'phenotypes': ','.join(['HP:0001332', 'HP:0100275']),
              'genes': 'PLIN4,MYH14,TUBB1,FGF5,WDR17,ASS1,VEZF1,LRFN4,DNAI1,NAA60,' +               'CNTN5,GIMAP2,SLC25A47,USP30,KMT2A,PRKRA,FADS6,WRNIP1,UGDH,' +               'NACA,PRX,FANCD2,KRTAP5-8,SNX1,PHKG1,THNSL1,CHRNE,DGKZ,CMYA5,' +               'EPHA6,VNN2,CTRB2,CAPN10,EMILIN1,OLIG3,CACNA1B,CYP4B1,HTR1D,' +               'SLC7A2,CMPK1,RBMXL3,DSG2,CCDC184,PM20D2,C2orf78,ACCSL,CHRD,' +               'MROH2B,ANO8,NOC4L,WDR4,FAM8A1,SLC1A5,SYNE1,SERAC1,VCX,SSC5D,' +               'APOB,TRABD,CAMTA2,HMGCS2,DSPP,LRBA,GP1BA'})
    print(json.dumps(response.json(), indent=4))


if __name__ == "__main__":
    main()