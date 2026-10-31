#1.0 INTRODUCTION TO DATA ANALYSIS WITH PYTHON
## LOAD DATASET BrazilEcommerce
## Question business in BrazilEcommerce project 
# %%
# BUSINESS QUESTIONS
# 1. How do orders and sales evolve month by month?
#    Data: orders + order_items. Technique: time grouping and trend analysis.
#
# 2. How long does a delivery take on average, and how is that time distributed?
#    Data: orders + customers + city_clean. Technique: delivery_days = customer_date - purchase_date;
#    mean, median, percentiles and outliers.
#
# 3. Do late deliveries lower customer review scores?
#    Data: orders + order_reviews. Technique: Mann-Whitney U test (review scores are ordinal, not normal).
#
# 4. Which order statuses have the highest cancellation rate?
#    Data: orders + customers + city_clean. Technique: contingency tables, chi-square test, Cramér's V.
#
# 5. Are late deliveries concentrated in certain regions?
#    Data: orders + customers + city_clean, with late = delivered after estimated date.
#    Technique: chi-square test and Cramér's V.
#
# 6. Is delivery-time variability the same across states?
#    Data: orders + customers + city_clean. Technique: Levene's test for equal variances.
#    If variances differ, use Kruskal-Wallis instead of ANOVA.
#
# 7. Does average product price change by product category?
#    Data: order_items + products + category translation. Technique: ANOVA or Kruskal-Wallis,
#    depending on the assumptions checked with Levene's test.
#
# 8. Did average order value increase from 2017 to 2018?
#    Data: orders + order_items. Technique: Welch's t-test or Mann-Whitney U, plus effect size.
#
# 9. Simpson's Paradox: does the ranking of states change when we split by category?
#    Data: orders + order_items + products + customers + city_clean.
#    Technique: compare average delivery time by state overall, then within each category.
#    If the ranking reverses, we have Simpson's Paradox.
#
# 10. Which factors predict a late delivery?
#     Data: all of the above + sellers, with seller-customer distance computed from
#     geolocation coordinates (Haversine formula).
#     Technique: Spearman correlation between distance and delivery days, and logistic
#     regression with late as the target variable.

## 1.1 importing libraries and loading the dataset

import pandas as pd 
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from IPython.display import display
from scipy.stats import mannwhitneyu, ttest_ind
from scipy.stats import chi2_contingency
from scipy.stats import levene
from scipy.stats import kruskal
from scipy.stats import levene, kruskal, f_oneway
from itertools import combinations
import statsmodels.api as sm

# %%
## load the data base 

orders = pd.read_csv("olist_orders_dataset.csv")
city = pd.read_csv("olist_geolocation_dataset.csv")
products = pd.read_csv("olist_products_dataset.csv")
customers = pd.read_csv("olist_customers_dataset.csv")
orders_items = pd.read_csv("olist_order_items_dataset.csv")
orders_reviews = pd.read_csv("olist_order_reviews_dataset.csv")
translation = pd.read_csv("product_category_name_translation.csv")
sellers = pd.read_csv("olist_sellers_dataset.csv")
display(orders.head())
display(city.head())
display(products.head())
display(customers.head())
display(orders_items.head())
display(orders_reviews.head())
display(sellers.head())

#%% 
# 2.1 Explore the info about the database

display(orders.info())
display(city.info())
display(products.info())
display(customers.info())
display(orders_items.info())
display(orders_reviews.info())

display(orders.isnull().sum())
display(city.isnull().sum())
display(products.isnull().sum())
display(customers.isnull().sum())
display(orders_items.isnull().sum())
display(orders_reviews.isnull().sum())

display("duplicates orders:", orders.duplicated().sum())
display("duplicates city:", city.duplicated().sum())
display("duplicates products:", products.duplicated().sum())
display("duplicates customers:", customers.duplicated().sum())
display("duplicates orders_items:", orders_items.duplicated().sum())
display("duplicates orders_reviews:", orders_reviews.duplicated().sum())

#%% data types columns. This helps to understand the structure of the data
#  and identify any potential issues with data types or missing 

## Rename columns to standarize the names and make them more readable

orders = orders.rename(columns={
    'order_id': 'order_id',
    'customer_id': 'customer_id',
    'order_status': 'status',
    'order_purchase_timestamp': 'purchase_date',
    'order_approved_at': 'approved_date',
    'order_delivered_carrier_date': 'carrier_date',
    'order_delivered_customer_date': 'customer_date',
    'order_estimated_delivery_date': 'delivery_date'
})

city = city.rename(columns={
    'geolocation_zip_code_prefix': 'zip_prefix',
    'geolocation_lat': 'latitude',
    'geolocation_lng': 'longitude',
    'geolocation_city': 'city_name',
    'geolocation_state': 'state'
})

products = products.rename(columns={
    'product_id': 'product_id',
    'product_category_name': 'category_name',
    'product_name_lenght': 'name_length',
    'product_description_lenght': 'description_length',
    'product_photos_qty': 'photos_quantity',
    'product_weight_g': 'weight_grm',
    'product_length_cm': 'length_cm',
    'product_height_cm': 'height_cm',
    'product_width_cm': 'width_cm'
})

customers = customers.rename(columns={
    'customer_id': 'customer_id',
    'customer_unique_id': 'unique_id',
    'customer_zip_code_prefix': 'zip_prefix',
    'customer_city': 'city_name',
    'customer_state': 'state'
})

orders_items = orders_items.rename(columns={
    'order_id': 'order_id',
    'product_id': 'product_id',
    'seller_id': 'seller_id',
    'quantity': 'quantity',
    'price': 'price'
})

orders_reviews = orders_reviews.rename(columns={
    'order_id': 'order_id',
    'review_id': 'review_id',
    'review_score': 'score',
    'review_comment_title': 'comment_title',
    'review_comment_message': 'comment_message',
    'review_creation_date': 'creation_date',
    'review_answer_timestamp': 'answer_timestamp'
})

display("orders columns:", orders.columns)
display("city columns:", city.columns)
display("products columns:", products.columns)
display("customers columns:", customers.columns)
display("order_items columns:", orders_items.columns)
display("order_reviews columns:", orders_reviews.columns)

#%%

## standarize the data types of the columns to make them more consistent and easier to work with

date_cols = ['purchase_date', 'approved_date', 'carrier_date', 'customer_date', 'delivery_date']
for col in date_cols:
    orders[col] = pd.to_datetime(orders[col], errors='coerce')
orders['purchase_year'] = orders['purchase_date'].dt.year
orders['purchase_month'] = orders['purchase_date'].dt.month

city['zip_prefix'] = city['zip_prefix'].astype(str).str.zfill(5)
city['latitude'] = pd.to_numeric(city['latitude'], errors='coerce')
city['longitude'] = pd.to_numeric(city['longitude'], errors='coerce')
city['city_name'] = city['city_name'].astype(str).str.strip().str.title()
city['state'] = city['state'].astype(str).str.strip().str.upper()

num_cols = ['name_length', 'description_length', 'photos_quantity', 'weight_grm', 'length_cm', 'height_cm', 'width_cm']
for col in num_cols:
    products[col] = pd.to_numeric(products[col], errors='coerce')

orders_reviews['creation_date'] == pd.to_datetime(orders_reviews['creation_date'], errors='coerce')
orders_reviews['answer_timestamp'] == pd.to_datetime(orders_reviews['answer_timestamp'], errors='coerce')
orders_reviews['score'] == pd.to_numeric(orders_reviews['score'], errors='coerce')

orders_items['shipping_limit_date'] == pd.to_datetime(orders_items['shipping_limit_date'], errors='coerce')
orders_items['price'] == pd.to_numeric(orders_items['price'], errors='coerce')
orders_items['freight_value'] == pd.to_numeric(orders_items['freight_value'], errors='coerce')

display(city.duplicated().sum())
city = city.drop_duplicates()   
display(city['zip_prefix'].nunique(), len(city))

city_clean = city.groupby('zip_prefix', as_index=False).agg(
    latitude=('latitude', 'mean'),
    longitude=('longitude', 'mean'),
    city_name=('city_name', 'first'),
    state=('state', 'first'),
)
display(city_clean.shape, city_clean['zip_prefix'].nunique())

products['category_name'] = products['category_name'].fillna('unknown')

measures = ['weight_grm', 'length_cm', 'height_cm', 'width_cm']
products[measures] = products[measures].fillna(products[measures].median())

orders_reviews['creation_date'] = pd.to_datetime(orders_reviews['creation_date'])

reviews_clean = (
    orders_reviews
    .sort_values(['order_id', 'creation_date'])
    .drop_duplicates(subset='order_id', keep='last')
)
display(orders.dtypes)
display(city.dtypes)
display(products.dtypes)
display(orders_reviews.dtypes)
display(orders_items.dtypes)
display(customers.dtypes)

#%%
# 2.2 analize nulls and duplicates after cleaning

display("orders nulls:")
display(orders.isnull().sum())
display(orders.duplicated().sum())
display("city nulls:")
display(city.isnull().sum())
display(city.duplicated().sum())
display("products nulls:")
display(products.isnull().sum())
display(products.duplicated().sum())
display("customers nulls:")
display(customers.isnull().sum())
display(customers.duplicated().sum()) 
display("order_items nulls:")
display(orders_items.isnull().sum())
display(orders_items.duplicated().sum())
display("order_reviews nulls:")
display(orders_reviews.isnull().sum())
display(orders_reviews.duplicated().sum())

# we can analize that products and orders are clear of duplicates, 
# but city has (261831 duplicates), and checking the nulls city is ok but orders has (2965,1783. and 160) 
# and products has (610  in four)

display(orders.columns.tolist())
display(city_clean.columns.tolist())
display(products.columns.tolist())
display(orders_items.columns.tolist())
display(orders_reviews.columns.tolist())
display(customers.columns.tolist())

display(orders.loc[orders['customer_date'].isnull(), 'status'].value_counts().sum())
display(orders['customer_date'].isnull().sum())

display("reviews_original:", len(orders_reviews))
display("reviews_clean:", len(reviews_clean))
display("order_id unique:", reviews_clean['order_id'].is_unique)

delivered_status = ['delivered']
strange_nulls = orders[(orders['status'].isin(delivered_status)) & (orders["customer_date"].isna())]
print("delivered without delivery date:", len(strange_nulls))

## Nouticing several duplicates and nulls(city had 261831 duplicates, 
# which i dropped them and orders has 2965,1783. and 160 nulls, 
# products has 610 nulls in four columns), analizing nulos canceled(619), 
# unavailable(609),invoiced(314),processing(301),created(5),approved(2),, 
# some very data strangers(8) they should be in delivery date .
#%%
## analize the strucutre with describe 

display(orders.describe())
display(city.describe())
display(products.describe())
display(customers.describe())
display(orders_items.describe())
display(orders_reviews.describe())

print(orders.columns.tolist())
print(orders_reviews.columns.tolist())
print(products.columns.tolist())
print("nulos orders:\n", orders.isna().sum())
print("nulos city_clean:\n", city_clean.isna().sum())

#%%
# Tabla maestra orders + customers

customers['zip_prefix'] = customers['zip_prefix'].astype(str).str.zfill(5)

df = orders.merge(customers, on='customer_id', how="left")
display("customer after:", len(df), "| originals rows:", len(orders))

df = df.merge(city_clean, left_on='zip_prefix', right_on='zip_prefix', how='left')
display("after city_clean:", len(df))
display("without match in city:", df['latitude'].isna().sum())

df = df.merge(reviews_clean, on='order_id', how='left')
display("after reviews:", len(df))

display("before orders_items:", len(df))
df = df.merge(orders_items, on='order_id', how='left')
display("after orders_items:", len(df))
display("unique orders:", df['order_id'].nunique())

display("before products:", len(df))
df = df.merge(products, on='product_id', how='left')
display("after products:", len(df))
display("items without category:", df['category_name'].isna().sum())

df['category_name'] = df['category_name'].fillna('unkown')
display("items without category:", df['category_name'].isna().sum())

df = df.rename(columns={'state_x': 'customer_state', 'state_y': 'zip_state'})
display([c for c in df.columns if 'state' in c])

## analize (99.441) rows,, city clean (99.441), 
# very useful analize cities without match (278), geolocation is (0.3%) dont afected any outcome
#%%
# QUESTION ONE ABOUT THE BUSINESS
df['purchase_month_start'] = df['purchase_date'].dt.to_period('M')

month_sales = (
    df.groupby('purchase_month_start')
    .agg(orders=('order_id', 'nunique'),
         revenues=('price', 'sum'))
    .reset_index()
)
display(month_sales)

month_sales_full = month_sales[month_sales['purchase_month_start'] >= '2017-01'].copy()
month_sales_full['revenues'] = month_sales_full['revenues'].round(2)
display(month_sales_full)

#%%
# Monthly orders trend (from 2017)

trend = month_sales_full.copy()
trend['month'] = trend['purchase_month_start'].dt.to_timestamp()

fig, ax = plt.subplots(figsize=(9, 4))
fig.patch.set_facecolor("#C4BCCF")
ax.set_facecolor("#A79FB3")
ax.plot(trend['month'], trend['orders'], color="#0BE4EB", marker='o')
ax.set_xlabel('month', color="#0E7321")
ax.set_ylabel('orders', color="#0E7321")
ax.set_title('Monthly orders since 2017', color="#0E7321")
for side in ['top', 'right']:
    ax.spines[side].set_visible(False)
plt.tight_layout()
fig.savefig('analysis_q1_monthly_orders.png', dpi=150, bbox_inches='tight')
plt.show()

#%%
# QUESTION TWO ABOUT THE BUSINESS

delivered_orders = (
    df[df['status'] == 'delivered']
    .drop_duplicates(subset='order_id')
    .copy()
)
delivered_orders['delivery_days'] = (
    delivered_orders['customer_date'] - delivered_orders['purchase_date']
).dt.days
delivered_orders['late'] = delivered_orders['customer_date'] > delivered_orders['delivery_date']

display("delivered orders:", len(delivered_orders))
display("negative days:", (delivered_orders['delivery_days'] < 0).sum())
display("% late deliveries:", round(delivered_orders['late'].mean() * 100, 2))
display(delivered_orders['delivery_days'].describe())
display("orders with more than 60 days:", (delivered_orders['delivery_days'] > 60).sum())

display(delivered_orders.loc[delivered_orders['customer_date'].isna(), ['order_id', 'status', 'customer_date']])

with_date = delivered_orders[delivered_orders['customer_date'].notna()]
display("% late (date_base):", round(with_date['late'].mean() * 100, 2))

## delivered delay around (10 days), average(12), the 75% arrive in around (15 days), 
# and 25 around (6 days) the (8.11 % delay deliveries), 288 orders delayed more than 60 days with(0.3%), 
# limitation 8 orders with status delivered that not have customer_date they are keeping in delivered counts but not in stadistics days.
#%%
# %%

days = delivered_orders['delivery_days'].dropna()
mean, median = days.mean(), days.median()

fig, ax = plt.subplots(figsize=(9, 4))
fig.patch.set_facecolor('#EDE7F6')
ax.set_facecolor('#FBF9FE')

ax.hist(days, bins=range(0, 61, 2), color="#6ACEDA", edgecolor='#FBF9FE')
ax.axvline(mean, color="#0C37E5", linestyle='--', linewidth=1)
ax.axvline(median, color="#E70439", linestyle='-', linewidth=1.5)

ax.text(mean + 0.5, ax.get_ylim()[1] * 0.9, f'average {mean:.1f}', color="#13A050", fontsize=9)
ax.text(median + 0.5, ax.get_ylim()[1] * 0.8, f'median {median:.0f}', color="#079450", fontsize=9)

ax.set_xlabel('delivery days', color="#096832")
ax.set_ylabel('number of orders', color="#096832")
ax.set_title('Distribution of delivery days (until 60 days)', color="#096832")

for lado in ['top', 'right']:
    ax.spines[lado].set_visible(False)

plt.tight_layout()
fig.savefig('analysis_q2_delivery_days.png', dpi=150, bbox_inches='tight')
plt.show()

#%%
## QUESTION 3 ( LATE DELIVERIES VS CALIFICATION)

Q3 = delivered_orders[delivered_orders["customer_date"].notna() & delivered_orders['score'].notna()]

display("order with date and rate:", len(Q3))
display(Q3.groupby('late')['score'].describe())

## prove with alternative= 'less'

late = Q3.loc[Q3['late'], 'score']
on_time = Q3.loc[~Q3['late'], 'score']

stat, p = mannwhitneyu(late, on_time, alternative='less')
display("u =", stat, "| p_value =", p)

## diagnosis "the orders delievered after the stimated_date have significate califications lower(median(2 vs 5):
#  mann-whitneyu U,p < 0.001) is an association, no causation,,
#  delivered_orders also can have others problems, like damages products, lacking of information from deliveries, 
# for rushtime also would be a problem but dont have the dataset to know that others. "
#%%
## subplot about mannwhitneyu 

prop = (
    Q3.groupby('late')['score']
    .value_counts(normalize=True)
    .rename('proportion')
    .reset_index()
)
prop['group'] = prop['late'].map({False: 'on_time', True: 'late'})

fig, ax = plt.subplots(figsize=(8, 4))
fig.patch.set_facecolor("#E6DFEF")
ax.set_facecolor("#e6dfef")
    
color = {'on_time': "#5f8ccb", 'late': "#4573cf"}   
for group, sub in prop.groupby('group'):
    ax.bar(sub['score'] + (0.2 if group == 'late' else -0.2),
           sub['proportion'], width=0.4, label=group, color=color[group])

ax.set_xticks([1,2,3,4,5])
ax.set_xlabel('calification', color="#44714F")
ax.set_ylabel('proportion by orders', color="#44714F")
ax.set_title('calification between on_time and late', color="#44714F")
ax.legend(facecolor="#BBC9BF", edgecolor="#44714F")

for side in ['top', 'right']:
    ax.spines[side].set_visible(False)

plt.tight_layout()
fig.savefig('analysis_q3_late_vs_on_time_reviews.png', dpi=150, bbox_inches='tight')
plt.show()

#%%
## QUESTION 4 CANCELED RATE BY STATE OF BRAZIL 

orders = df.drop_duplicates(subset='order_id').copy()
orders['canceled'] = orders['status'] == 'canceled'

status_table = orders.groupby('customer_state').agg(
    orders=('order_id', 'count'),
    canceled=('canceled', 'sum'),
)
status_table['cancelation_rate_%'] = (
    status_table['canceled'] / status_table['orders'] * 100
).round(2)

## status wiht low orders
status_table = status_table[status_table['orders'] >=100]
display(status_table.sort_values('cancelation_rate_%', ascending=False))

# rate higher: RO(1.19%), PI(0.81%), and SP(0.78%). RO has just 253 orders and 3 cancelation.
# rate lower: BA(0.47%), SC and CE(0.52%)
# volumen: SP has the highest cancelations numbers (327), but his rate is around the average because has(41746 orders)
# the diferent between state is close (around 0.4% and 1.2%) i hope the chi2 show us more about it  
#%%
contingency = pd.crosstab(orders['customer_state'], orders['canceled'])
chi2, p, dof, _ = chi2_contingency(contingency)

n = contingency.values.sum()
k = min(contingency.shape) - 1
v_cramer = np.sqrt(chi2 / (n * k))
display("chi2 =", round(chi2, 2), "| p=", p, "| v of cramer =", round(v_cramer, 3))

# the cancelation rate change significantly between (chi2 = 47.71, p=0.006),
# but the association is weak (v_cramer = 0.022) rates are between 0.47% and 1.19%,
# so state is not very relevant to predict cancelations, states with rates higher (RO, PI)
# have small trails an the diference in some cancelations can change their percentage. 

#%%
# QUESTION 5 LATE DELIVERIES BY STATE 

Q5 = (
    df[df['status'] == 'delivered']
    .drop_duplicates(subset='order_id')
    .copy()
)
Q5 = Q5[Q5['customer_date'].notna()].copy()
Q5['late'] = Q5['customer_date'] > Q5['delivery_date']

late_table = Q5.groupby('customer_state').agg(
   orders=('order_id', 'count'),
   late=('late', 'sum'), 
)
late_table['late_rate_%'] = (late_table['late'] / late_table['orders'] * 100).round(2)
late_table = late_table[late_table['orders'] >= 100]
display(late_table.sort_values('late_rate_%', ascending=False))

# prove 

contingency_late = pd.crosstab(Q5['customer_state'], Q5['late'])
chi2, p, dof, _ = chi2_contingency(contingency_late)

n = contingency_late.values.sum()
k = min(contingency_late.shape) - 1
v_cramer = np.sqrt(chi2 / (n * k))
display("chi2 =", round(chi2, 2), "| p=", p, "| v of cramer =", round(v_cramer, 3))

# analizing late deliveries are concentrated in several states(chi_2 =1623, p<0.001, ve of cramer=0.13)
# highest rates are in north and west regions of Brazil (Alagoas 23.9%) in fron to an average of (8.1%)
# association is moderate: region explain a part of the delayed but not at all 
# west states have also bigger distances toward distribution center.

#%%
# subplot 

datas = late_table.sort_values('late_rate_%', ascending=True)
fig, ax = plt.subplots(figsize=(8, 6))
fig.patch.set_facecolor("#E6DFEF")
ax.set_facecolor("#E6DFEF")

ax.barh(datas.index, datas['late_rate_%'], color="#4592df")
ax.axvline(8.11, color="#F10F03", linestyle='--', linewidth=1)
ax.text(8.2, -0.8, 'average 8.11%', color="#f62f03", fontsize=9)

ax.set_xlabel('% of late deliveries orders', color="#115033")
ax.set_title('late deliveries by state', color="#115030")

for side in ['top', 'right']:
    ax.spines[side].set_visible(False)

plt.tight_layout()
fig.savefig('analysis_q5_late_deliveries_by_state.png', dpi=150, bbox_inches='tight')
plt.show()

#%%
# QUESTION 6 VARIABILITY OF TIME DELIVERY BY STATE

Q6 = Q5.copy()
Q6['delivery_days'] = (Q6['customer_date'] - Q6['purchase_date']).dt.days

validate_state = Q6['customer_state'].value_counts()
validate_state = validate_state[validate_state >= 100].index
Q6 = Q6[Q6['customer_state'].isin(validate_state)]

display(Q6.groupby('customer_state')['delivery_days'].describe().round(2))

# levene 

groups = [g['delivery_days'].values for _, g in Q6.groupby('customer_state')]
stat, p = levene(*groups)
display("levene w =", round(stat, 2), "| p =", p)

# kruskal 

h, p_kw = kruskal(*groups)
display("kruskal-wallis H =", round(h, 2), "| p =", p_kw)

# epsilon2

n = len(Q6)
k = Q6['customer_state'].nunique()
epsilon2 = (h - k + 1) / (n - k)
display("epsilon2 =", round(epsilon2, 3))

# Delivery time of variability is not equal between states (levene W=162.83, p < 0.001)
# so ANOVA is not valid, was using kruskal-wallis which also fond out differences significantly in the distribution
# (H=23864.96, p < 0.001), size effect is big (E2=0.248)
# states slowest and spread are (AM, AL, CE), most fastest and consistents are (DF and MA)   

# %%
# BOXPLOT

orden = Q6.groupby('customer_state')['delivery_days'].median().sort_values().index
datas_box = [Q6.loc[Q6['customer_state'] == s, 'delivery_days'] for s in orden]

fig, ax = plt.subplots(figsize=(10, 5))
fig.patch.set_facecolor("#C7C1D0")
ax.set_facecolor("#C6BFD0")

ax.boxplot(datas_box, tick_labels=orden, showfliers=False,
           patch_artist=True, boxprops=dict(facecolor="#42ADDE"),
           medianprops=dict(color="#E42F07"))
ax.set_ylabel('Delivery days', color="#065B24")
ax.set_title('Delivery days by state (without atipic)', color="#0B5121")
plt.xticks(rotation=25)
plt.tight_layout()
fig.savefig('analysis_q6_delivery_days_by_state.png', dpi=150, bbox_inches='tight')
plt.show()

# %%
# QUESTION SEVENT PRICE BY CATEGORY 

translation = translation.rename(columns={
    'product_category_name': 'category_name',
    'product_category_name_english': 'category_in',
})

Q7 = df[['category_name', 'price']].merge(translation, on='category_name', how='left')
Q7= Q7.dropna(subset=['price']).copy()
Q7 = Q7[Q7['category_in'].notna()]  # quita 'desconocido' y los que no tienen traducción

cat_table = Q7.groupby('category_in')['price'].agg(
    items='count', mean='mean', median='median', std='std'
).round(2)
cat_table = cat_table[cat_table['items'] >= 100].sort_values('mean', ascending=False)
display(cat_table)

#%%
# levene

groups7 = [Q7.loc[Q7['category_in'] == c, 'price'].values for c in cat_table.index]

w, p_lev = levene(*groups7)
print("Levene W =", round(w, 2), "| p =", p_lev)

h, p_kw = kruskal(*groups7)
print("Kruskal-Wallis H =", round(h, 2), "| p =", p_kw)

# price's products change significantly between categories (kruskal-wallis H=13136.01, p < 0.001, levene W=112.69, p < 0.001 because ANOVA didn't use it)
# computers has the highest price (median= 1100), while watches-gifts combine the bigger volume with moderate prices.
# the difference between average and median in several categories show what there are products with very very high price into them,
# so the median describe the best common price.

#%%
# BOXPLOT OF PRICE TOP 15 CATEGORIES BY MEDIAN  

Top15 = cat_table.sort_values('median', ascending=False).head(15).index
order = list(reversed(Top15))  # para que la más alta quede arriba
datas_box = [Q7.loc[Q7['category_in'] == c, 'price'] for c in order]

fig, ax = plt.subplots(figsize=(9, 7))
fig.patch.set_facecolor("#DEE1BE")
ax.set_facecolor("#D1D9BB")

ax.boxplot(datas_box, tick_labels=order, vert=False, showfliers=False,
           patch_artist=True, boxprops=dict(facecolor="#31A6C6"),
           medianprops=dict(color="#3F07EA"))
ax.set_xlabel('price (R$)', color="#05601B")
ax.set_title('Price by category: Top 15 highest price (without atipic)', color="#05601B")

for side in ['top', 'right']:
    ax.spines[side].set_visible(False)

plt.tight_layout()
fig.savefig('analysis_q7_price_by_category.png', dpi=150, bbox_inches='tight')
plt.show()

#%%
# QUESTION EIGHT TICKET AVERAGE BY ORDER 2017 / 2018

tickets = (
    df.groupby('order_id')
      .agg(year=('purchase_year', 'first'),
           price=('price', 'sum'),
           freight=('freight_value', 'sum'))
      .reset_index()
)
tickets['ticket'] = tickets['price'] + tickets['freight']

T8 = tickets[tickets['year'].isin([2017, 2018])].copy()
display(T8.groupby('year')['ticket'].describe().round(2)) 

# PROVE AND SIZE ABOUT THE EFFECT 

G17 = T8.loc[T8['year'] == 2017, 'ticket']
G18 = T8.loc[T8['year'] == 2018, 'ticket']

u, p_mw = mannwhitneyu(G17, G18, alternative='two-sided')
t, p_t = ttest_ind(G17, G18, equal_var=False)  # Welch

sp = np.sqrt((G17.var() + G18.var()) / 2)
d = (G18.mean() - G17.mean()) / sp

print("Mann-Whitney U =", u, "| p =", p_mw)
print("Welch t =", round(t, 2), "| p =", p_t)
print("Cohen's d =", round(d, 3))

# Average ticket by order was actually the same in (2017(158.37) - 2018(160.04))
# with one noutible size (d=0.008, welch p < 0.24)
# the median increase of (102 to 106)(Mann-whitneyu p < 0.001) a little bit change it.
# Mann-whitneyu compare distributions not averages, in spite of this can be significantly when welch doesn't
# the number of orders was growing up (45101 in 2017  and 54011 in 2018), although 2018 is incomplete.
    
#%%
# SUBPLOTS ABOUT THE YEAR

resume = T8.groupby('year')['ticket'].agg(['mean', 'median'])
x = np.arange(len(resume.index))
width = 0.35

fig, ax = plt.subplots(figsize=(7, 4))
fig.patch.set_facecolor("#CABFDB")
ax.set_facecolor("#BBAFCB")

ax.bar(x - width/2, resume['mean'], width, label='average', color="#3E9EC8")
ax.bar(x + width/2, resume['median'], width, label='median', color="#155E7D")

for i, (m, md) in enumerate(zip(resume['mean'], resume['median'])):
    ax.text(i - width/2, m + 2, f'{m:.0f}', ha='center', fontsize=9)
    ax.text(i + width/2, md + 2, f'{md:.0f}', ha='center', fontsize=9)

ax.set_xticks(x)
ax.set_xticklabels(resume.index.astype(str))
ax.set_ylim(0, resume['mean'].max() * 1.15)  # el eje empieza en cero
ax.set_ylabel('ticket by average (R$)', color="#076A34")
ax.set_title('Ticket by order: 2017 vs 2018', color="#097322")
ax.legend()

for lado in ['top', 'right']:
    ax.spines[side].set_visible(False)

plt.tight_layout()
fig.savefig('analysis_q8_ticket_2017_vs_2018.png', dpi=150, bbox_inches='tight')
plt.show()

#%%
# QUESTION 9 base by item (delivery days + state + category)

items9 = (
    df[df['status'] == 'delivered']
      .loc[lambda d: d['customer_date'].notna()]
      .merge(translation, on='category_name', how='left')
      .copy()
)
items9['delivery_days'] = (items9['customer_date'] - items9['purchase_date']).dt.days
items9 = items9[items9['category_in'].notna()]
print(items9.shape)

# general ranking vs ranking into every category

# %%
# PREGUNTA 9: ranking general vs ranking ino every category (simpsoms paradox)

states_ok = items9['customer_state'].value_counts()
states_ok = states_ok[states_ok >= 500].index
base9 = items9[items9['customer_state'].isin(states_ok)]

general = base9.groupby('customer_state')['delivery_days'].mean().sort_values()
display(general.round(2).to_frame('general_average'))

cats = base9['category_in'].value_counts().head(10).index
by_cat = (
    base9[base9['category_in'].isin(cats)]
    .groupby(['category_in', 'customer_state'])['delivery_days']
    .mean()
    .unstack('customer_state')
)
display(by_cat.round(1))

#%%
## RESULT simpsoms Paradox

results = []
for a, b in combinations(general.index, 2):
    general_order = np.sign(general[a] - general[b])
    cat_order = np.sign(by_cat[a] - by_cat[b]).dropna()
    if len(cat_order) and (cat_order != general_order).all():
        results.append((a, b, round(general[a], 2), round(general[b], 2)))

display("pairs with inversion in all categories:", results)

##

counts = []

for a, b in combinations(general.index, 2):
    general_order = np.sign(general[a] - general[b])
    cat_order = np.sign(by_cat[a] - by_cat[b]).dropna()
    inverts = (cat_order != general_order).sum()
    if inverts >= 1:
        counts.append((a, b, int(inverts), len(cat_order)))

counts = sorted(counts, key=lambda x: -x[2])
display("pairs (a, b, inverts categories, compared categories):")
for c in counts[:10]:
    display(c)

## compare pairs

for a, b in [('GO', 'MS'), ('MT', 'PE'), ('SC', 'RJ')]:
    display(a, b, round(general[a], 2), round(general[b], 2),
            "difference:", round(abs(general[a] - general[b]), 2))



# Analizing the counts i nouticed there was not relevant simpsoms paradox 
# no state of pair inverts his order in every analized categories, the highets inversion pairs
# (GO-MS, MT-PE, with six of ten all over categories), they have general differences lower to (0.35 dyas)
# so the order change is just nothing noise and not a structural inversion.
# north states are consistently lower and SP is consistently the fastest.

#%%
# dumbbell grafic GO vs MS general average vs by category

comp = by_cat[['GO', 'MS']].dropna()
comp = comp.sort_values('GO')

fig, ax = plt.subplots(figsize=(8, 5))
fig.patch.set_facecolor("#CDC8D5")
ax.set_facecolor("#BFB9C9")

y = range(len(comp))
for i, (cat, fila) in enumerate(comp.iterrows()):
    ax.plot([fila['GO'], fila['MS']], [i, i], color="#B9A8E0", zorder=1)
ax.scatter(comp['GO'], y, color="#0691B0", label='GO', zorder=2)
ax.scatter(comp['MS'], y, color="#E10539", label='MS', zorder=2)

ax.axvline(general['GO'], color="#039BDC", linestyle='--', linewidth=1)
ax.axvline(general['MS'], color="#F0033B", linestyle='--', linewidth=1)

ax.set_yticks(list(y))
ax.set_yticklabels(comp.index)
ax.set_xlabel('delivered average by day', color="#058928")
ax.set_title('GO vs MS by category (dotted lines = general average)', color="#0C9638")
ax.legend()

for side in ['top', 'right']:
    ax.spines[side].set_visible(False)

plt.tight_layout()
fig.savefig('analysis_q9_state_comparison_by_category.png', dpi=150, bbox_inches='tight')
plt.show()

#%%

## QUESTION 10 SELLERS COORDINATE
# merge city_clean with sellers

sellers['seller_zip_code_prefix'] = (
    sellers['seller_zip_code_prefix'].astype(str).str.zfill(5)
)
sellers_geo = sellers.merge(
    city_clean[['zip_prefix', 'latitude', 'longitude']],
    left_on='seller_zip_code_prefix',
    right_on='zip_prefix',
    how='left',
).rename(columns={'latitude': 'seller_lat', 'longitude': 'seller_lng'})
display(
    "sellers:", len(sellers),
    "| without coordinates:", sellers_geo['seller_lat'].isna().sum()
)

base10 = (
    df[df['status'] == 'delivered']
    .loc[lambda d: d['customer_date'].notna()]
    .drop_duplicates(subset='order_id')
    .drop(columns='seller_id')
    .copy()
)
base10['delivery_days'] = (base10['customer_date'] - base10['purchase_date']).dt.days
base10['late'] = base10['customer_date'] > base10['delivery_date']

display("before of coordinates:", len(base10))

seller_ordered = (
    orders_items[['order_id', 'seller_id']]
    .drop_duplicates(subset='order_id')
)
base10 = base10.merge(seller_ordered, on='order_id', how='left')
base10 = base10.merge(
    sellers_geo[['seller_id', 'seller_lat', 'seller_lng']], on='seller_id', how='left'
)
display("after of sellers:", len(base10))

base10 = base10.dropna(subset=['latitude', 'longitude', 'seller_lat', 'seller_lng'])
display("order with calculate distances:", len(base10))
                                     
# %%
# DISTANCE Haversine CLIENT-SELLERS (KM)

R = 6371  # radio de la Tierra en km
lat1 = np.radians(base10['seller_lat'])
lon1 = np.radians(base10['seller_lng'])
lat2 = np.radians(base10['latitude'])
lon2 = np.radians(base10['longitude'])

a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
base10['distance_km'] = 2 * R * np.arcsin(np.sqrt(a))

display(base10['distance_km'].describe().round(1))

#%%
## OUT OF MIND CASES 

display("more than 4300 km:", (base10['distance_km'] > 4300).sum())

# %%
# delivery late rate by distance subplot

datos10 = base10[base10['distance_km'] <= 4300].copy()
datos10['bloque_km'] = pd.cut(datos10['distance_km'], bins=range(0, 4501, 500))
rate = datos10.groupby('bloque_km', observed=True)['late'].agg(['mean', 'count'])
rate['rate_%'] = rate['mean'] * 100
rate = rate[rate['count'] >= 100]

fig, ax = plt.subplots(figsize=(9, 4))
fig.patch.set_facecolor("#C1BBC9")
ax.set_facecolor("#B9AFC8")

labels = [f'{int(i.left)}–{int(i.right)}' for i in rate.index]
ax.bar(labels, rate['rate_%'], color="#208AB4")
for i, (v, n) in enumerate(zip(rate['rate_%'], rate['count'])):
    ax.text(i, v + 0.3, f'{v:.1f}%\n(n={n:,})', ha='center', fontsize=8)

ax.axhline(datos10['late'].mean() * 100, color="#BB1212", linestyle='--', linewidth=1)
ax.set_xlabel('client-seller distance (km)', color="#0B8736")
ax.set_ylabel('% late deliveries', color="#0B8736")
ax.set_title('deliveries late by distances', color="#0B8736")

for side in ['top', 'right']:
    ax.spines[side].set_visible(False)

plt.tight_layout()
fig.savefig('analysis_q10_late_rate_by_distance.png', dpi=150, bbox_inches='tight')
plt.show()

# the probability of late delivery increasing with the distance between client-seller
# (6.9% until 500km, 10.2% until 1000 and 1500km, 14.0% until 2000 and 2500km)
# after 2500 km the rate become stable between 11% and 13%.
# the block of 3500 and 4000km (33%) have just (3 orders)and its not ocnsiderted 
# its a clear association but the distance doesn't explain all the late deliveries
# was lost just (4) orders of (95992) and its just wrong coordinates not real datas so dont change the analysis (so they are just exclude by distance >4300)   

#%%
# logistic regressison around the late deliveries

m = datos10.dropna(subset=['price', 'freight_value']).copy()

X = pd.get_dummies(m[['distance_km', 'price', 'freight_value', 'customer_state']],
                   columns=['customer_state'], drop_first=True, dtype=float)
X = sm.add_constant(X)
y = m['late'].astype(int)

model = sm.Logit(y, X).fit(disp=False)
print(model.summary2().tables[1][['Coef.', 'P>|z|']].round(4))

# %%
odds = pd.DataFrame({
    'odds_ratio': np.exp(model.params),
    'p_value': model.pvalues
}).round(4)
display(odds)

display("OR by each 100km:", round(np.exp(model.params['distance_km'] * 100), 3))

# Adjust model logistic

print("pseudo R² (McFadden):", round(model.prsquared, 4))
print("AIC:", round(model.aic, 1))
print("order by model:", int(model.nobs))

# in the logistic model, the distance seller-client increase the late delivered probability
# but his adjust effect is small (OR=1.014 por 100km, p < 0.001)
# client state is the strongest factor,, Alagoas has 9 times odds bigger than reference
# price has a slow effect (OR=1.02 by R$100) and the carriage is not significantly

# as a limitation: the variable late just compare delivery vs stimated_date so that date is calculated by the platform using region and distance
# pseudo R2  of McFadde=0.028 coeficients are significatives by size trail this help us how predict patterns not to predict what order willl arive late or doesn't it
