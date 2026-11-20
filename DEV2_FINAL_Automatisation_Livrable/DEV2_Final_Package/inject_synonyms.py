#!/usr/bin/env python3
"""Safely apply approved English synonyms to Power BI TMDL linguisticMetadata.
Usage: python inject_synonyms.py /path/to/fr-FR.tmdl
The input is backed up; output is written to fr-FR.enriched.tmdl (never overwrites).
"""
import argparse, json, pathlib, shutil

SYNONYMS = {
 ('_Mesures','Total Sales'): ['sales revenue','total revenue','sales amount','turnover','total sales'],
 ('_Mesures','Total Quantity'): ['units sold','total units','sales quantity','quantity ordered','total quantity'],
 ('_Mesures','Total Cost'): ['total product cost','cost of sales','total costs'],
 ('_Mesures','Margin'): ['gross profit','sales margin','margin amount'],
 ('_Mesures','Margin %'): ['margin percentage','gross margin rate','profit margin percentage'],
 ('FactSales','SalesAmount'): ['sales value','transaction revenue','sales amount'],
 ('FactSales','OrderQuantity'): ['ordered units','quantity per order','order quantity'],
 ('FactSales','OrderDate'): ['sale date','purchase date','order date'],
 ('FactSales','UnitPrice'): ['selling price per unit','unit selling price'],
 ('FactSales','TotalProductCost'): ['transaction product cost','product cost amount'],
 ('DimProduct','EnglishProductName'): ['product name','item name','product title'],
 ('DimProduct','EnglishProductCategoryName'): ['product category','product family'],
 ('DimProduct','EnglishProductSubcategoryName'): ['product subcategory','subcategory'],
 ('DimProduct','Color'): ['product color','item color'],
 ('DimReseller','ResellerName'): ['reseller name','business customer name','reseller'],
 ('DimReseller','BusinessType'): ['reseller business type','business type'],
 ('DimSalesTerritory','SalesTerritoryRegion'): ['sales region','territory region','sales territory'],
 ('DimSalesTerritory','SalesTerritoryCountry'): ['sales country','territory country'],
 ('DimDate','Année'): ['calendar year','sales year','year'],
 ('DimDate','Mois'): ['calendar month','month name'],
 ('DimDate','Date'): ['calendar date','date'],
}

def transform(source):
    raw=source.read_text(encoding='utf-8-sig')
    marker='linguisticMetadata ='
    pos=raw.find(marker)
    if pos<0: raise ValueError('Missing linguisticMetadata')
    start=raw.find('{',pos)
    if start<0: raise ValueError('Missing linguistic JSON')
    data,end=json.JSONDecoder().raw_decode(raw[start:]); stop=start+end
    entities=data.get('Entities',{})
    mapped={}
    for ident,entry in entities.items():
        bind=entry.get('Definition',{}).get('Binding',{})
        key=(bind.get('ConceptualEntity'),bind.get('ConceptualProperty'))
        if key in SYNONYMS:
            if key in mapped: raise ValueError('Duplicate entity binding: '+str(key))
            mapped[key]=(ident,entry)
    missing=set(SYNONYMS)-set(mapped)
    if missing: raise ValueError('Unrecognized field bindings: '+repr(sorted(missing)))
    changes=[]
    for key,wanted in SYNONYMS.items():
        ident,entry=mapped[key]
        terms=entry.setdefault('Terms',[])
        existing={word.casefold() for term in terms for word in term}
        for word in wanted:
            if word.casefold() not in existing:
                # User-defined synonyms: omit Generated/Suggested state and preserve existing terms.
                terms.insert(0,{word:{}})
                existing.add(word.casefold());changes.append((key,word))
    # JSON only, keep TMDL header/contentType unchanged. Avoids modifying measures, relations, data.
    rendered=json.dumps(data,ensure_ascii=False,indent=2)
    # Match original indentation format of multiline property: first line follows the equals;
    # continuation lines receive two tabs. Existing TMDL uses 2-space indentation inside JSON.
    rendered=rendered.replace('\n','\n\t\t\t')
    result=raw[:start]+rendered+raw[stop:]
    return result,changes,len(mapped),data

def main():
    ap=argparse.ArgumentParser();ap.add_argument('file',type=pathlib.Path);args=ap.parse_args()
    path=args.file
    if not path.is_file(): ap.error('File not found')
    new,changes,count,d=transform(path)
    backup=path.with_name(path.name+'.backup')
    if not backup.exists():shutil.copy2(path,backup)
    out=path.with_name(path.stem+'.enriched'+path.suffix)
    out.write_text(new,encoding='utf-8')
    check=json.JSONDecoder().raw_decode(new[new.index('{',new.index('linguisticMetadata =')):])[0]
    assert len(check['Entities'])==len(d['Entities'])
    print(f'OK: {count} matched fields, {len(changes)} new terms; output: {out}; backup: {backup}')
    print('NOTE: Validate by reopening a COPY of the PBIP project in Power BI Desktop.')
if __name__=='__main__':main()
