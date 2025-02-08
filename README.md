# Visual Document Retrieval in Arabic

An attempt at recreating the data pipeline for the [Multilingual Visual Document Retrieval Dataset](https://huggingface.co/datasets/llamaindex/vdr-multilingual-train), in Arabic

## Data Gathering Pipeline

Ideally, we want a lot of PDFs, PPTs and rendered HTMLs, all in Arabic, we want them as messy as possible ideally to reflect real life data.

This is everything I have so far for the data pipeline, which will rapidly evolve very quickly, but for now, to gather PDFs, this is what I did:

1. Rely on Google for most of the heavy work, my query looks like this: `filetype:pdf lang:ar [TOPIC]`
2. Get seed topics from [Wikipedia](https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/2)
3. Use [SerpAPI](https://serpapi.com/search-api) to programitacally send the queries.
    - To vary the results, you can provide a location parameter to where the search will originate, I put together a list of middle eastern country codes, filtered them by reach, and used a random location per query, code for this is in `notebooks/02_serp_api.ipynb`
4. Use a simple GET request to try to download the PDFs.

What remains is scaling this approach, the reason I did exactly 98 queries to Serp with 30 results for each query is as follows:
1. I have 100 free queries. I used two to test the parameters. Wikipedia has levels of vitality for topics, top 10, top 100, I scraped them manually and I think I missed two so I have 98 queries.
2. 30 results per query seemed reasonable to test it, given the queries are generic, I think we need the max of 100 results.

Current findings:
1. The PDFs aren't contrained to Arabic content only, we need a way to remedy this.
2. Simple GET requests got me 1500/2856
3. I put together the links without their metadata for the scraper, so now they're decoupled, the results from Serp offer lots of metadata that might help catalouge them at scale, I'd like to keep them together next time.

## Roadmap
1. Scale data pipelines, deduplicate, validate quality and content language, classify and cluster into quality levels, add more file formats
2. Find a way to annotate these PDFs with queries...........
