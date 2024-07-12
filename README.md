# TermsFeed

@hercules you can place a small description of the project here as an introduction

## Prerequisites

 - Python v3.11.9
 - Conda 24.4.0
 - A MongoDB database (local or remote)

## Setup Instructions
Make sure you have Python and Conda installed on your OS. 

Then use pip to install dependencies located at the requirements.txt document
```
pip install -r requirements.txt
```
Update `.env` file to match your needs. Make sure that the DSN for the MongoDB database is correct and the collections needed (`crawler` and `abstracts`) are available.

## Fetch abstract links for 100 terms
```commandline
python.exe prepare Secale codends rice watercress Harmonia Bovidae Tetragonuridae Amomum enzymes tapioca beers Telmatherinidae marking Thuja Bulbophyllum Imperata cucumbers irradiation techniques garlic Belonidae Commelinales Salangidae Mullidae Amblycipitidae Anomalopidae kids Lolium bran middlings flamingoes drakes Toxopneustidae Galatheidae Lithodidae Hemisquillidae charcoal Platygaster Aphredoderidae Euphausiacea Arrhenatherum viscosity plovers breeding Chacidae Nepidae abalones alkalinity invertebrates meiosis Bromus mint Astrebla Homola owls Ctenoluciidae Tomicus Eurypharyngidae krill ducklings rums Gibberichthyidae Cetomimidae Pascopyrum Costus bitches Diodontidae Hypoderma Samaridae Barbourisiidae segregation Soleidae nutmegs hares chaff Liopsetta adaptability oregano crows Euphausiidae Dactylis flavour Otiorhynchus luminescence photogrammetry Lophiidae pheasants barnacles swallows Torpediniformes hyssop sherry Pseudomugilidae Scopelarchidae Hemerocallis cashews thyme Anostomidae Triodontidae Echinochloa 
```

## Crawl 1000 abstracts
```commandline
python.exe crawl 1000
```

## How to use
You can use this application via the command line. 

There are three available commands at your disposal.

**Command 1: Prepare**

This command search the AGRIS database using the agrovoc terms that are provided as arguments. For each term is locates all of the link for abstracts that are available and stores them on the crawler collection (MongoDB) for the crawler to be able to retrieve them.

Command syntax
```commandline
python.exe prepare agrovoc_term agrovoc_term agrovoc_term 
```
Example
`python.exe prepare agrovoc_term spraying `

**Command 2: Retrieve abstracts**

This command gets the links from the `crawler` collection (MongoDB) that have not been retrieved yet and crawls to extract and store the results in the `abstracts` collection. You can set the number of abstracts/links to be crawled by passing the number as an argument. If no argument is passed it fallbacks to the `.env` setting and if that also fails, it fallbacks to 1.

Command syntax
```commandline
python.exe crawl <how_many> 
```
Example
`python.exe crawl 10 `

**Command 3: Clear collection from records (Hard delete, cannot be undone)**
You can use this command to delete all entries from a collection.
```
python.exe clear <collection_name>
```

i.e.
`python.exe clear abstracts` or `python.exe clear crawler`


## Methodology

The data collection process is divided into N steps. 

### Step 1: Calculate acceptable sample terms length for our correlation to be strong

We used G*Power software (https://www.psychologie.hhu.de/arbeitsgruppen/allgemeine-psychologie-und-arbeitspsychologie/gpower) to calculate the minimum sample size needed to achieve a strong correlation. 

**<ins>G*Power configuration used</ins>**

**Test Family and Statistical Test:**
- **Test Family**: `Exact`
- **Statistical Test**: `Correlation: Bivariate normal model`

**Type of Power Analysis:**
- **Type**: `A priori` (Compute required sample size given α, power, and effect size)

**Input Parameters:**
- **Tail(s)**: `Two` - This implies testing for both directions of correlation (positive or negative).
- **Determine ⇒ Correlation ρ H1**: `0.5` - Anticipated correlation coefficient, indicating a moderate expected correlation.
- **α err prob**: `0.05` - Alpha error probability, commonly set to control the Type I error rate.
- **Power (1-β err prob)**: `0.95` - Desired statistical power to detect the effect, set high to minimize Type II error.
- **Correlation ρ H0**: `0` - Null hypothesis correlation, assuming no correlation under the null hypothesis.

**Output Parameters:**
- **Lower critical r**: `-0.2907065` - The critical value of r below which the correlation is considered significantly negative.
- **Upper critical r**: `0.2907065` - The critical value of r above which the correlation is considered significantly positive.
- **Total sample size**: `46` - The required number of pairs of data points to achieve the desired power and effect size.
- **Actual power**: `0.9535111` - The calculated power of the test based on the sample size and specified effect size.


### Step 2: Get random agrovoc terms
We used SPARQL to get random agrovoc terms from https://agrovoc.fao.org/sparql.

We used the following query to get the terms.

```commandline
PREFIX skos: <http://www.w3.org/2004/02/skos/core#> 
PREFIX skosxl: <http://www.w3.org/2008/05/skos-xl#> 
SELECT ?concept ?prefLabel 
WHERE { 
  ?concept a skos:Concept . 
  ?concept skosxl:prefLabel/skosxl:literalForm ?prefLabel . 
  FILTER(lang(?prefLabel) = 'en') .
  FILTER REGEX(?prefLabel, '^[a-zA-Z0-9_]+$') .
} ORDER BY RAND() LIMIT 100
```

### Step 3: Fetch abstract links for the 100 terms
We used the `prepare` command to fetch the abstract links for the 100 terms.
```commandline
python.exe prepare Secale codends rice watercress Harmonia Bovidae Tetragonuridae Amomum enzymes tapioca beers Telmatherinidae marking Thuja Bulbophyllum Imperata cucumbers irradiation techniques garlic Belonidae Commelinales Salangidae Mullidae Amblycipitidae Anomalopidae kids Lolium bran middlings flamingoes drakes Toxopneustidae Galatheidae Lithodidae Hemisquillidae charcoal Platygaster Aphredoderidae Euphausiacea Arrhenatherum viscosity plovers breeding Chacidae Nepidae abalones alkalinity invertebrates meiosis Bromus mint Astrebla Homola owls Ctenoluciidae Tomicus Eurypharyngidae krill ducklings rums Gibberichthyidae Cetomimidae Pascopyrum Costus bitches Diodontidae Hypoderma Samaridae Barbourisiidae segregation Soleidae nutmegs hares chaff Liopsetta adaptability oregano crows Euphausiidae Dactylis flavour Otiorhynchus luminescence photogrammetry Lophiidae pheasants barnacles swallows Torpediniformes hyssop sherry Pseudomugilidae Scopelarchidae Hemerocallis cashews thyme Anostomidae Triodontidae Echinochloa 
```

### Step 4: Crawl 1000 abstracts
We used the `crawl` command to crawl 1000 abstracts.
```commandline
python.exe crawl 1000
```
You can repeat this step as many times as you want to get more abstracts and/or increase the number of abstracts to be crawled.

### Step 5: Preprocess the abstracts
we used the `preprocess` command to preprocess the abstracts. 
Pre-processing involves: removal of punctuation, removal of whitespaces, removal of stopwords, tokenization, and conversion of the text to lower case.
```commandline
python.exe preprocess
```

### Step 6: Calculate the TF-IDF for each term and save the average value in the database
We used the `tfidf` command to calculate the TF-IDF for each term and save the average value in the database.
```commandline
python.exe tfidf_calc
```

### Step 7: Tokenize the agrovoc terms
We use the BERT tokenizer to tokenize the agrovoc terms. This is required for the vectorization step to be able to run successfully.
```commandline
python.exe tokenize_terms
```

### Step 8: Vectorize the abstracts
We used the `vectorize` command to vectorize the abstracts. BertModel was used to vectorize the abstracts with the recobo/agriculture-bert-uncased pre-trained weights.

```commandline
python.exe vectorize
```

### Step 9: Calculate mean vectors via mean pooling
We used the `mean_pooling` command to calculate the mean vectors via mean pooling.
```commandline
python.exe mean_pooling
```

### Step 10: Calculate the occurrence semantic distances of each term in the abstracts
We used the `occurrence` command to calculate the occurrence distances of each term in the abstracts.
```commandline
python.exe occurrence_distances
```

### Step 11: Calculate the occurrence abstract semantic distances
```commandline
python.exe occurrence_abstract_distances
```

### Step 12: Calculate the cosine similarity between the mean vectors and the occurrence abstract distances
```commandline
python.exe abstract_distances
```