
## Impact Lens
A lot of information on the internet like news, social media posts etc that can impact brands. Directly, in the form of positive or negative PR and indirectly in that their product strategy could be potentially informed from these. Identifying such news is extremely useful for large brands or analytics divisions to get ahead of the PR cycle and formulate an early response.

We attempt to identify information that can be potentially impactful to a brand. We decided to tackle this problem by using classification algorithms and impact analysis methods. This project focuses on using classification to break down the documents into various categories and then look through the lens of a specific brand to calculate an impact score of each document. We present a stack rank of such documents back to the brand.

## Steps
0. go to git root
1. pipenv --python 3.7
2. pipenv shell
3. pipenv install Pipfile


## FAQs

1. How is this different from search?

Search looks at indexing words entered from your search query. google search arguably also performs contextual search, but we don't know the complete sauce outside the company.
Impact Lens currently has a simple impact score method - it looks for words that are contextually similar to the vocabulary input for the brand. There is scope to expand this to take into account credibility, factfullness etc


