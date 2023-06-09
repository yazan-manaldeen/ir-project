## IR Project (Search Engine)

## Damascus University

### About Project

We need to build search engine with two datasets from `ir_datasets`.
The first dataset is `qoura` and the second dataset is `antique`.
The project build by jubyter notebook, and then we use python rest-api and angular to build website for the search
engine.

### Parts of project

1. python back-end:
    * resources: contains the clean docs and queries csv for datasets and json files
    * qoura and antique _rest_api folders: contains the rest-api files for the search engine
        - `_main:` to run rest-api
        - `_lemmatize_text:` contains function that take query text, clean it and return the clean value
        - `_indexing:` contains the docs index and function that take clean query text and return the indexes of docs
          that contains clean query text words
        - `_docs_service:` contains function that take indexes array of docs and return these docs objects for return it
          to user
        - `_suggestions:` contains the queries index and function that take query text and return the suggestions for
          this query
    * clean folder: contains two files one of them for clean qoura dataset and other file to clean antique dataset,
      this file reads dataset docs, queries and qrels and save it to csv files in resources, and run two functions:
        - `clean_queries function:` to clean queries file of dataset
        - `clean_docs function:` to clean docs file of dataset
    * evaluation folder: contains two files to calculate evaluation for qoura and antique datasets,
      the evaluation calculate by run the dataset queries in and compare our search engine result with qrels related result
2. angular front-end:
    * contains search page that viewed by app component (html, css, ts)

### Development server

1. python rest-api: you need to run two `_main.py` files in qoura and antique folders,
   (qoura rest-api run in port: 5000 and antique rest-api run in port: 4000)
2. angular front-end: you need to run one of these commands,
   (angular front-end run in port: 5500)
    * `npm run start`: for a dev server
    * `npm run build`:  to build the project to `dist/` directory
    * `npm run start-build`: to run the build artifacts that will be built to `dist/` directory
3. Development server notes
    * You must have `python`, `nodejs` and `npm` in your computer and must install required libraries
    * For `npm run start-build` you must have `http-server` library
    * You must check availability for these ports (5000, 4000, 5500)