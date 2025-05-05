
# CS 5804 Mini-Project: Sentiment Analysis of 10-K Reports to Predict Market Performance

**Group 6 Members:**
 - Devon Boldt devonsboldt@vt.edu 
 - Aziz Shaik azizs@vt.edu
 - Tayseer Hannan tayseerhanan@vt.edu
 - Thomas Spearing thomasjs@vt.edu
 - Jacob Tennant jacobtent97@vt.edu
 - Anthony Nguyen anthonyqn@vt.edu 
 - Kevin Severic kevins91@vt.edu

<h3 style="text-align:center;">How can we utilize sentiment analysis on annually filed 10-K reports to predict market performance for the subsequent fiscal year?</h3>

## Background Information
Annually, the U.S. Securities and Exchange Commission (SEC) mandates that companies file a 10-K report detailing their financial statements for the year, as well as risk factors the company is concerned about for the previous and coming year. It also includes a discussion of the company’s performance for the prior year, which can give an idea of what the company expects for the next fiscal year.

## Objectives
The project aims to develop a sentiment analysis model to evaluate the content of 10-K filings and assess its impact on market performance for certain publicly traded companies. This project leverages NLP techniques to investigate the relationship between sentiment scores and financial indicators like trading volume and stock volatility. Analyzing certain sections of 10-K reports would aid in capturing market response due to certain corporate actions such as regulatory changes or lawsuits.

## Methodology
**Overall Correlation**  
We found a correlation of **-0.0489** across all tickers and years. Essentially, the 10‑K sentiment scores and next‑year returns are basically not correlated when everything is pooled together.

**Interpretation**  
There isn’t a strong overall link between a company’s 10‑K sentiment and how its stock performs the following year if we look at the entire dataset at once.

**Per-Ticker Highlights**  

- **Strongest Positive Correlations**  
  - HUM: +0.559  
  - WBA: +0.482  
  - CMCSA: +0.442  
  - MSFT: +0.448  
  - PG: +0.445  

  These suggest that higher sentiment scores tended to go along with higher returns for these particular tickers.

- **Strongest Negative Correlations**  
  - META: -1.0 (only 2 data points)  
  - UNH: -0.796  
  - WFC: -0.824  (only 3 data points)
  - COR: -0.814  

  For these, more negative sentiment might have coincided with better returns (or the other way around), but small samples can distort the numbers like META and WFC.

- **Weak/Near-Zero Correlations**  
  - KR: +0.097  
  - CVS: +0.0037  

  Here, sentiment and next‑year returns barely move in tandem.

- **Insufficient Data**  
  - BAC, C, GS, JPM, MS showed “NaN” because there wasn’t enough overlapping data (often just one or two points).

**Cautions**  
- A correlation of “NaN” or ±1.0 often means minimal data.
- Correlation doesn’t imply causation.
- Different periods or methods (like quarterly analysis) may show different results.

**Key Takeaway**  
Overall, there is no single, across-the-board correlation between 10-K sentiment and next-year returns. Certain tickers exhibit moderate positive or negative relationships, but many have little or no apparent link. This suggests that while sentiment may matter for some companies, 10-K sentiment alone isn’t a universal or reliable predictor of future performance.

## Conclusion
<Add it in here once we finish\>
