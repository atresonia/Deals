# deals
**Depersonalization of deal links**

Given a TSV file containing deals(with personalized links), the program will return the deals with depersonalized links and output the deals to a JSON file.

Depending on the deal, the personalized link may not be depersonalizable. The program tests a candidate depersonalized link using link validation and HTML document similarity score to make a determination. 

**Inputs**

`DEALS_INPUT_FILE`: the input TSV (tab-separated) file with format: `url\tdescription`

The first line should contain a header. 

`DEALS_OUTPUT_FILE`: the output JSON file will contain the result data. 

`MAX_DEALS`: the maximum number of deals read from input file

`MAX_WORKERS`: maximum number of worker threads created to process deals

`SIMILARITY_THRESHOLD`: HTML document similarity score is a value between 0.0 and 1.0, inclusive

