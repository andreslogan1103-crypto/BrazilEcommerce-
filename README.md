# Brazil E-commerce Analytics (Olist)

An end-to-end analysis of the Olist marketplace in Brazil (2016–2018). The project answers ten business questions about delivery performance, customer reviews, cancellations, prices and order value, using descriptive statistics and formal hypothesis tests.

## Executive Summary

- **8.1%** of delivered orders arrived after the estimated delivery date.
- Late orders have a median review score of **2**, versus **5** for on-time orders (Mann-Whitney U, p < 0.001). This is an association, not proof of causation.
- Late rates are highest in the north and northeast: **Alagoas 23.9%**, **Maranhão 19.7%**, against 8.1% nationally.
- Seller-to-customer distance raises late-delivery odds only slightly: **odds ratio 1.014 per 100 km** after adjusting for state, price and freight.
- The adjusted logistic model has a McFadden pseudo R² of **0.028**. Most of the variation in late deliveries comes from factors not in the dataset.

## Data

Nine Olist CSV tables are integrated: orders, order items, payments, reviews, customers, products, sellers, geolocation and category translations. The dataset is public and was obtained from Kaggle.

## Cleaning Decisions

- **Column names:** renamed to consistent snake_case. Keys in the rename dictionaries match the original CSV headers, including the source typos (`product_name_lenght`, `product_description_lenght`).
- **Zip codes:** normalized to 5 digits with `zfill(5)`.
- **Duplicates:** order-level tables were deduplicated on `order_id` before analysis. Joining items to orders would otherwise count one order several times.
- **Geolocation:** averaged to one latitude and longitude per zip prefix.
- **Delivery dates:** not imputed. Missing delivery dates are explained by order status (canceled, unavailable, etc.).
- **Missing categories:** labeled `desconocido`.
- **Measures:** missing numeric values replaced by the median where imputation was needed.
- **Joins:** the master table has 99,441 orders after the customer join and 113,425 rows after order items, which is expected because some orders contain several items.

## Business Questions and Results

| # | Question | Method | Result |
|---|----------|--------|--------|
| 1 | Monthly order trend | Grouped time series | See notebook |
| 2 | How long do deliveries take? | Descriptive statistics | Mean 12.1 days, median 10, 75th percentile 15, max 209. 288 orders took more than 60 days. 8.11% were late. |
| 3 | Do late deliveries lower review scores? | Mann-Whitney U (one-sided) | Median 5 on time vs 2 late, p ≈ 0 |
| 4 | Does cancellation vary by state? | Chi-square, Cramér's V | χ² = 47.71, p = 0.0058, V = 0.022 (weak) |
| 5 | Are late deliveries concentrated in some states? | Chi-square, Cramér's V | χ² = 1623.19, p ≈ 0, V = 0.13 (moderate). Alagoas 23.9%, Maranhão 19.7% |
| 6 | Does delivery-time variability differ by state? | Levene, Kruskal-Wallis | Levene W = 162.83, p ≈ 0. Kruskal-Wallis H = 23,864.96, p ≈ 0, ε² = 0.248 (large) |
| 7 | Do prices differ by category? | Levene, Kruskal-Wallis | Levene W = 112.69, p ≈ 0. Kruskal-Wallis H = 13,136.01, p ≈ 0 |
| 8 | Did average order value change from 2017 to 2018? | Mann-Whitney U, Welch t-test, Cohen's d | Means R$ 158.37 vs R$ 160.04. Medians R$ 102.23 vs R$ 106.40. Mann-Whitney p = 4.2e-07, Welch p = 0.238, d = 0.008 (negligible) |
| 9 | Simpson's Paradox: does the state ranking reverse within categories? | Pairwise rank comparison across top categories | No reversals. Largest gap (GO–MS) is 0.29 days |
| 10 | Which factors predict a late delivery? | Haversine distance, logistic regression | Mean distance 601 km, median 434 km. Odds ratio 1.014 per 100 km (p = 0.0004). Price odds ratio 1.0002 per R$ (p = 0.0006). Alagoas about 9× the odds of the reference state. Pseudo R² = 0.0275. Model n = 95,988 |

## Key Limitations

- **Late is defined against the platform's estimated date.** That estimate already reflects region and distance, so part of the distance effect may be built into the definition.
- **Observational data.** The results show associations, not causes.
- **Low explanatory power.** The model predicts patterns, not individual late deliveries.
- **8 delivered orders** have no customer delivery date. They are kept in delivered counts but excluded from timing statistics.
- **4 orders** with a seller-to-customer distance above 4,300 km were excluded from the distance model as coordinate errors.

## Project Structure

```
BrazilEcommerce/
├── BrazilEcommerce.py   # Full analysis, cell by cell (# %% markers)
├── README.md
└── data/                # Olist CSV files (not included)
```

## Technologies

Python, pandas, NumPy, SciPy, statsmodels, Seaborn, Matplotlib, Jupyter-style cells in VS Code.

## How to Run

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

   ```bash
   pip install pandas numpy seaborn matplotlib scipy statsmodels ipython
   ```

4. Place the Olist CSV files in `data/`.
5. Open `BrazilEcommerce.py` and run it top to bottom (Restart kernel, then Run all). Running cells out of order causes NameError or KeyError.

## Author

Camilo andres delagdo — data analyst in career transition.

## License and Dataset Attribution

The Olist dataset is publicly available on Kaggle. Please credit the dataset when reusing this analysis.

