import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from scipy import stats
from scipy.stats import spearmanr,pointbiserialr, f_oneway,chi2_contingency

import matplotlib.pyplot as plt

#First, load the data and conduct a preliminary check to ensure the integrity and consistency of the data.
data = pd.read_csv('user_personalized_features.csv')

print(data.shape)
print(data.info())
print(data.isna().sum())
print(data.duplicated().sum())

#delete the first column due to "unnamed"
data = data.drop('Unnamed: 0', axis=1)
print(data)

#Unique values of categorical features are examined and descriptive statistical analysis is performed.
characteristic = ['Gender','Location','Interests','Product_Category_Preference','Newsletter_Subscription']
for i in characteristic:
    print(f'{i}:')
    print(data[i].unique())
    print('-'*50)
print(characteristic)

#There are no missing and duplicate values in the data set. The distribution of unique values of classification features is reasonable.


#Outliers are visualized by drawing a box diagram
df = pd.DataFrame(data)
feature_map = feature_map = {
    'Age': 'Age',
    'Income': 'Income Level',
    'Last_Login_Days_Ago': 'Number of days since last login',
    'Purchase_Frequency': 'Frequency of incoming purchases',
    'Average_Order_Value': '下单的平均价值',
    'Total_Spending': 'The average value of the order',
    'Time_Spent_on_Site_Minutes': 'Time spent on e-commerce platforms',
    'Pages_Viewed': 'The number of pages viewed during a visit'
}

plt.figure(figsize=(20, 15))
for i, (col, col_name) in enumerate(feature_map.items(), 1):
    plt.subplot(2, 4, i)
    sns.boxplot(y=data[col])
    plt.title(f'{col_name} Box Plot', fontsize=14)
    plt.ylabel('Value', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
#In general, the quality of the data set is high, there are no missing values, duplicate values and outliers, and the unique value distribution of the classification features is reasonable, and the data is directly used for analysis.

# Statistics descriptive analysis,
print(data.describe(include='all'))


#Users basic info. Analyze demographic information about users, including age, gender, and geographic distribution
plt.figure(figsize=(15, 10))
plt.subplot(2, 3, 1)
sns.histplot(data['Age'], kde=True)
plt.title('Age distribution')
plt.xlabel('Age')
plt.ylabel('Number of people')

plt.subplot(2, 3, 2)
gender_counts = data['Gender'].value_counts()
plt.pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%', startangle=140)
plt.title('Gender distribution')

plt.subplot(2, 3, 3)
sns.countplot(x='Location', data=data)
plt.title('Location distribution')
plt.xlabel('Location')
plt.ylabel('Number of people')

plt.subplot(2, 3, 4)
sns.boxplot(y=data['Income'])
plt.title('Box plot of income')
plt.ylabel('Income')

plt.subplot(2, 3, (5,6))
interests_text = ' '.join(data['Interests'])
wordcloud = WordCloud(background_color='white').generate(interests_text)
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Hobby distribution')
plt.tight_layout()
plt.show()


#Shopping behavier. Analyze users' shopping frequency, order value, total consumption, and product preferences.
plt.figure(figsize=(20, 15))
plt.subplot(2, 2, 1)
sns.boxplot(y=data['Purchase_Frequency'])
plt.title('Purchase frequency box plot')
plt.ylabel('Purchase frequency')


plt.subplot(2, 2, 2)
sns.histplot(data['Average_Order_Value'], kde=True)
plt.title('Average order value distribution')
plt.xlabel('Order value')
plt.ylabel('Number of people')

plt.subplot(2, 2, 3)
sns.histplot(data['Total_Spending'], kde=True)
plt.title('Average order value distribution')
plt.xlabel('Aggregate amount')
plt.ylabel('Number of people')

plt.subplot(2, 2, 4)
sns.countplot(x='Product_Category_Preference', data=data)
plt.title('Product category preference distribution')
plt.xlabel('Product category')
plt.ylabel('Number of people')

plt.tight_layout()
plt.show()

"""
RFM model is an important tool to measure customer value and customer's ability to create benefits. The model describes the value status of the customer through three indicators: recent purchase behavior, total purchase frequency and total purchase amount within a certain time range.
R (Recency) : Interval of the last consumption, that is, the time between the last transaction between the customer and the enterprise. It is usually measured in days, and the number of days since the user last logged in is considered here.
F (Frequency) : Total consumption frequency, that is, the cumulative frequency of transactions generated by customers in a certain period of time.
M (Monetary) : The total amount of consumption, that is, the total cumulative amount of transactions generated by the customer in a certain period of time.
The larger the R value, the longer the transaction cycle between the customer and the enterprise, the lower the customer activity, and the easier the customer loss. On the contrary, the transaction cycle between the customer and the enterprise is short, and the customer is in an active state.
The larger the F value, the more frequent the transactions between customers and enterprises, and the stronger the stickiness and loyalty of the cooperation between customers and enterprises. On the contrary, the cooperation between customers and enterprises is poor in stickiness and low in loyalty.
The larger the M value, that is, the larger the transaction amount between the customer and the enterprise, which reflects the large scale of the customer's own operation, large market share and strong financial capacity. On the contrary, the customer's business scale is small, the market share is small and the financial capacity is weak.
The RFM model generally divides customers into eight categories: important value customers, important retention customers, important development customers, important retention customers, general value customers, general retention customers, general development customers, and general retention customers.
"""
new_data = data.copy()
# Caculate RFM score
new_data['Recency_Score'] = pd.qcut(new_data['Last_Login_Days_Ago'], 5, labels=False, duplicates='drop') + 1
new_data['Frequency_Score'] = pd.qcut(new_data['Purchase_Frequency'].rank(method='first'), 5, labels=False, duplicates='drop') + 1
new_data['Recency_Score'] = 6 - new_data['Recency_Score']
new_data['Monetary_Score'] = pd.qcut(new_data['Total_Spending'], 5, labels=False, duplicates='drop') + 1

def assign_rfm_group(row):
    if row['Frequency_Score'] >= 4 and row['Monetary_Score'] >= 4 and row['Recency_Score'] >= 4:
        return 'Champions' #   Significant value customer
    elif row['Frequency_Score'] >= 4 and row['Monetary_Score'] >= 4 and row['Recency_Score'] < 4:
        return 'Loyal Customers' #  Important retention customer
    elif row['Frequency_Score'] < 4 and row['Monetary_Score'] >= 4 and row['Recency_Score'] >= 4:
        return 'Potential Loyalists' # Key development customer
    elif row['Frequency_Score'] < 4 and row['Monetary_Score'] >= 4 and row['Recency_Score'] < 4:
        return 'At Risk' # Key retention customer
    elif row['Frequency_Score'] >= 4 and row['Monetary_Score'] < 4 and row['Recency_Score'] >= 4:
        return 'Average Customers' # Average Customers, General value customer
    elif row['Frequency_Score'] >= 4 and row['Monetary_Score'] < 4 and row['Recency_Score'] < 4:
        return 'Need Attention' # Need Attention, General holding customer
    elif row['Frequency_Score'] < 4 and row['Monetary_Score'] < 4 and row['Recency_Score'] >= 4:
        return 'New Customers' # General development account
    else:
        return 'Hibernating' # General retention

new_data['Customer_Segment'] = new_data.apply(assign_rfm_group, axis=1)
data['Customer_Segment'] = new_data['Customer_Segment']

print(data['Customer_Segment'].value_counts())
"""
Hibernating (General Retention Customers): 
This group represents the largest proportion, indicating that many users have low purchase frequency and total spending and have not logged in for a long time. 
Marketing strategies for this group include reactivation campaigns, where special offers or gifts are sent through email or SMS to encourage them to return. Conducting surveys to invite participation helps in understanding their needs and preferences, allowing for targeted improvements. Awakening emails can be sent to remind them of the platform's advantages and new activities.

New Customers (General Development Customers): 
These are new customers who have recently logged in but have low purchase frequency and total spending and need further nurturing. 
Marketing strategies involve offering first purchase discounts to encourage them to place an order, providing a detailed shopping guide and platform introduction to help them become familiar with the platform, and introducing membership benefits to encourage them to register as members.

At Risk (Important Retention Customers): 
These customers have high total spending but have not logged in for a long time, indicating a high risk of churn. 
To address this, marketing strategies include reactivation campaigns that remind them of the time since their last login through email or SMS, offering special rewards or discounts. High-value coupons can be sent to encourage them to return and make a purchase. Conducting phone calls or care greetings helps understand the reasons for their inactivity and provides necessary assistance.

Need Attention (General Maintenance Customers): 
These users have high purchase frequency but low total spending and have logged in recently. 
Marketing strategies focus on frequent communication through email, SMS, and other channels to provide the latest product information and promotional activities. Encouraging them to accumulate points for rewards and discounts is also effective. Organizing member-exclusive activities enhances their engagement and keeps them active.

Average Customers (General Value Customers): 
Users in this category have high purchase frequency but low total spending and have not logged in for a long time. 
Marketing strategies aim to increase their spending through bundling sales or discounts for spending over a certain amount. Promoting high-value new products attracts them to try purchasing. Designing simple and effective loyalty programs helps increase their stickiness to the platform.

Potential Loyalists (Important Development Customers): 
These users have high total spending and have logged in recently but have low purchase frequency, showing potential to become loyal customers. 
Marketing strategies include designing promotional activities specifically for them to encourage more frequent purchases and promptly informing them about new product launches with samples or special discounts. Providing personalized services and recommendations based on their preferences can further boost their loyalty.

Loyal Customers (Important Maintenance Customers): 
These users have high purchase frequency, have logged in recently, and have high total spending, maintaining high loyalty. 
Marketing strategies involve frequent communication through email, SMS, and other methods to provide the latest product information and promotional activities. Encouraging them to earn rewards and discounts through accumulating points is beneficial, and organizing member-exclusive activities enhances their engagement.

Champions (High-Value Users): 
These are the most valuable customers with high purchase frequency, total spending, and recent login times, requiring focused maintenance and preferential treatment. 
Marketing strategies for champions include personalized recommendations based on their interests and purchase history, offering exclusive discounts, promotions, and reward programs. Providing priority customer service and after-sales support is crucial, along with designing special loyalty programs to increase their sense of belonging.
"""


# K-Means
new_data.drop(columns=['User_ID','Last_Login_Days_Ago', 'Purchase_Frequency', 'Total_Spending','Customer_Segment'],inplace=True)

new_data['Gender'] = new_data['Gender'].map({
    'Female': 0,
    'Male': 1})

new_data['Newsletter_Subscription'] = new_data['Newsletter_Subscription'].astype(int)

new_data = pd.get_dummies(new_data,columns=['Location','Interests','Product_Category_Preference']).astype('int')

scaler = StandardScaler()
num_features = ['Age', 'Income','Average_Order_Value','Time_Spent_on_Site_Minutes','Pages_Viewed','Recency_Score','Frequency_Score','Monetary_Score',]
new_data[num_features] = scaler.fit_transform(new_data[num_features])
print(new_data.head())

inertia = []
silhouette_scores = []
k_range = range(2, 11)
for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=10).fit(new_data)
    inertia.append(kmeans.inertia_)
    silhouette_scores.append(silhouette_score(new_data, kmeans.labels_))

plt.figure(figsize=(15,5))

plt.subplot(1, 2, 1)
plt.plot(k_range, inertia, marker='o')
plt.xlabel('cluster centroids number')
plt.ylabel('inertia')
plt.title('Elbow rule diagram')

plt.subplot(1, 2, 2)
plt.plot(k_range, silhouette_scores, marker='o')
plt.xlabel('cluster centroids')
plt.ylabel('Silhouette Score')
plt.title('Silhouette Score Plot')

plt.tight_layout()
plt.show()

"""
1. The left figure is the elbow rule diagram, through which we can see that the curve decline rate decreases significantly at 7 to 8.
2. The figure on the right is the Silhouette coefficient diagram. At 2, the Silhouette coefficient is the highest, and it is also high at 7 and 8.
However, combining the two graphs, 7 is selected as the cluster number, and the decline rate of the elbow rule graph decreases significantly, and it is the second highest point in the contour coefficient diagram.
"""

# K-means, we identify "7"
kmeans_final = KMeans(n_clusters=7, random_state=15)
kmeans_final.fit(new_data)
# get cluster labels
cluster_labels = kmeans_final.labels_
# Add clustering labels to the raw data for analysis
data['Cluster'] = cluster_labels

# Calculate the variance of each feature at the center of all clusters; the greater the variance, the greater the importance of the feature to distinguish different clusters.

# center of cluster
cluster_centers = kmeans.cluster_centers_
# Calculate the importance of features: the variance of each feature across all cluster centers
feature_variances = np.var(cluster_centers, axis=0)

# Put the features and their variances into the DataFrame and arrange them in descending order by variance
feature_importance = pd.DataFrame({
    'Feature': new_data.columns,
    'Variance': feature_variances
})
feature_importance = feature_importance[feature_importance['Feature'] != 'Cluster']
feature_importance = feature_importance.sort_values(by='Variance', ascending=False)
print(feature_importance)
"""
It can be found that the clustering is mainly divided by eight characteristics: R score (the number of days since the last login of the user), age, time spent on the platform, number of pages viewed during the visit, income, M score (the total amount of consumption), average value of orders placed, and F score (the frequency of purchases). 
Then compare the differences among these seven user groups. Focus on the most important features first.
"""

#Comparison between seven types of users
plt.figure(figsize=(10,6))
sns.boxplot(x='Cluster', y='Age', data=data, palette='viridis')
plt.xlabel('Cluster')
plt.ylabel('Age')
plt.title('Age distribution in different clusters')
plt.show()

plt.figure(figsize=(10,6))
sns.boxplot(x='Cluster', y='Income', data=data, palette='viridis')
plt.xlabel('Cluster')
plt.ylabel('Income')
plt.title('Income distribution in different clusters')
plt.show()

plt.figure(figsize=(10,6))
sns.boxplot(x='Cluster', y='Purchase_Frequency', data=data, palette='viridis')
plt.xlabel('Cluster')
plt.ylabel('Purchase frequency')
plt.title('Purchase frequency distribution in different clusters')
plt.show()

plt.figure(figsize=(10,6))
sns.boxplot(x='Cluster', y='Average_Order_Value', data=data, palette='viridis')
plt.xlabel('Cluster')
plt.ylabel('Average order value')
plt.title('Average order value distribution in different clusters')
plt.show()

plt.figure(figsize=(10,6))
sns.boxplot(x='Cluster', y='Total_Spending', data=data, palette='viridis')
plt.xlabel('Cluster')
plt.ylabel('Aggregate amount')
plt.title('Distribution of total consumption amount in different clusters')
plt.show()

plt.figure(figsize=(10,6))
sns.boxplot(x='Cluster', y='Last_Login_Days_Ago', data=data, palette='viridis')
plt.xlabel('Cluster')
plt.ylabel('Days')
plt.title('The distribution of days since last login in different clusters')
plt.show()

plt.figure(figsize=(10,6))
sns.boxplot(x='Cluster', y='Pages_Viewed', data=data, palette='viridis')
plt.xlabel('Cluster')
plt.ylabel('pages')
plt.title('Distribution of the number of viewed pages in different clusters')
plt.show()

plt.figure(figsize=(10,6))
sns.boxplot(x='Cluster', y='Time_Spent_on_Site_Minutes', data=data, palette='viridis')
plt.xlabel('Cluster')
plt.ylabel('Minutes')
plt.title('Different clusters distribute the time spent on the site')
plt.show()

"""
Cluster 0
Characteristics: Middle income middle-aged user group, low purchase frequency, low average order value and total consumption, but short time since the last login, more pages viewed, and longer time spent on the website.
Marketing advice: Set up the first purchase discount, according to the online time to issue coupons to promote consumption.

Cluster 1
Characteristics: Older users with moderate income, moderate purchase frequency, average order value and total consumption, long time since last login, many pages viewed, and short time spent on the website.
Marketing advice: By SMS or email, remind them of the new activities of the platform, set up return rewards, and set up middle-aged and elderly models for them.

Cluster 2
Characteristics: Young users with high income, high purchase frequency and average order value, but low total consumption, short time since last login, many pages viewed, and long time spent on the website.
Marketing advice: Provide high-end products and VIP services, personalized recommendations to increase exposure to high-value goods.

Cluster 3
Features: High income young user group, low purchase frequency, high average order value, high total consumption, slightly longer time since the last login, low number of pages viewed, and particularly short time spent on the website.
Marketing advice: Offer limited-time offers and interactive content, increase the time spent on the site, and provide them with youth-oriented products.

Cluster 4
Characteristics: Low-income young user group, high purchase frequency, low average order value and total consumption, long time since the last login, small number of pages viewed, average time spent on the website.
Marketing advice: Offer price discounts and personalized recommendations to attract more purchases, inform return rewards through SMS or email, and issue coupons according to the time spent online.

Cluster 5
Characteristics: Low-income older user group, high purchase frequency, average order value medium, high total consumption, short time since last login, medium number of pages viewed, and slightly longer time spent on the website.
Marketing advice: Provide cost-effective products and loyalty rewards, enhance social media marketing, and set up a middle-aged and elderly model for them.

Cluster 6
Characteristics: Middle income middle-aged user group, low purchase frequency, high average order value and total spend, longer days since last login, fewer pages viewed, and longer time spent on the website.
Marketing advice: Provide targeted offers and personalized recommendations, quality content to extend the stay time, considering their low frequency of purchase, you can issue coupons for high-quality products to stimulate consumption.
"""

# The next step is to explore the relationship between the variables
"""
Spearman correlation or Pearson correlation is used directly for continuous and continuous variables, and then a correlation heat map with a significant relationship is drawn.
Continuous variables and binary variables (gender, whether to subscribe to marketing campaign notifications) were tested using dot two column correlation tests.
Continuous variables and multiple disordered variables (interest, shopping preference), using ANOVA, because the sample size is large, can not consider homogeneity and normality, of course, can also use other non-parametric tests.
Chi-square test is used between unordered categorical variables and unordered categorical variables.以上翻译结果来自有道神经网络翻译（YNMT）· 通用场景
"""

data['Gender'] = data['Gender'].map({
    'Female': 0,
    'Male': 1})
data['Newsletter_Subscription'] = data['Newsletter_Subscription'].astype(int)

# Easy to read, take * as P-value for significance level
def convert_pvalue_to_asterisks(pvalue):
    if pvalue <= 0.001:
        return "***"
    elif pvalue <= 0.01:
        return "**"
    elif pvalue <= 0.05:
        return "*"
    return ""
# Function to create a Spearman correlation heatmap
def spearman_corr_heatmap(features):
    #  Compute Spearman correlation matrix
    spearman_corr_matrix = data[num_features].corr(method='spearman')
    # Compute p-value matrix
    pvals = data[num_features].corr(method=lambda x, y:spearmanr(x, y)[1]) - np.eye(len(data[num_features].columns))

    # Apply the conversion function to p-values
    pval_star = pvals.applymap(lambda x: convert_pvalue_to_asterisks(x))

    # Convert to numpy array
    corr_star_annot = pval_star.to_numpy()

    # Prepare labels
    corr_labels = spearman_corr_matrix.to_numpy()
    p_labels = corr_star_annot
    shape = corr_labels.shape

    #  Combine correlation and p-value labels
    labels = (np.asarray(["{0:.2f}\n{1}".format(data, p) for data, p in zip(corr_labels.flatten(), p_labels.flatten())])).reshape(shape)

    #  Plot heatmap
    fig, ax = plt.subplots(figsize=(10, 8), dpi=100, facecolor="w")
    sns.heatmap(spearman_corr_matrix, annot=labels, fmt='', cmap='coolwarm',
                vmin=-1, vmax=1, annot_kws={"size":10, "fontweight":"bold"},
                linecolor="k", linewidths=.2, cbar_kws={"aspect":13}, ax=ax)

    ax.tick_params(bottom=False, labelbottom=True, labeltop=False,
                left=False, pad=1, labelsize=12)
    ax.yaxis.set_tick_params(labelrotation=0)

    # Customize colorbar format
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(direction="in", width=.5, labelsize=10)
    cbar.set_ticks([-1, -0.5, 0, 0.5, 1])
    cbar.set_ticklabels(["-1.00", "-0.50", "0.00", "0.50", "1.00"])
    cbar.outline.set_visible(True)
    cbar.outline.set_linewidth(.5)

    plt.title('Spearman Correlation Matrix')
    plt.show()

def point_biserial_correlation(binary_vars, target_var):
    results = []
    for var in binary_vars:
        corr, p_value = pointbiserialr(data[var], data[target_var])   # Calculate point biserial correlation and p-value
        results.append((var, corr, p_value))
    return pd.DataFrame(results, columns=['Feature', 'Point Biserial Correlation', 'Point Biserial P-value'])

def categorical_anova_analysis(categorical_vars, target_var):
    results = []
    for var in categorical_vars:
        groups = [data[data[var] == level][target_var] for level in data[var].unique()]  # Group the target variable by each level of the categorical variable
        f_value, p_value = f_oneway(*groups)  # Perform ANOVA (Analysis of Variance)
        results.append((var, f_value, p_value))
    return pd.DataFrame(results, columns=['Feature', 'F-Value', 'ANOVA P-value'])

def numeric_anova_analysis(numeric_vars, target_var):
    results = []
    for var in numeric_vars:
        groups = [data[data[target_var] == level][var] for level in data[target_var].unique()]
        f_value, p_value = f_oneway(*groups)
        results.append((var, f_value, p_value))
    return pd.DataFrame(results, columns=['Feature', 'F-Value', 'ANOVA P-value'])

def chi_square_test(input_variables, target_var):
    results = []
    for var in input_variables:   # Create a contingency table
        contingency_table = pd.crosstab(data[var], data[target_var])   # Create a contingency table
        chi2, p_value, dof, expected = chi2_contingency(contingency_table)  # Perform Chi-Square test
        results.append((var, chi2, p_value))
    return pd.DataFrame(results, columns=['Feature', 'Chi-Square Value', 'Chi-Square Test P-value'])

num_features = ['Age', 'Income', 'Last_Login_Days_Ago', 'Time_Spent_on_Site_Minutes', 'Pages_Viewed','Purchase_Frequency','Average_Order_Value','Total_Spending']
print(spearman_corr_heatmap(num_features))

"""
Variables such as age, number of days since last login, time spent on e-commerce platforms, and number of pages viewed during a visit had no significant impact on purchase frequency, average value of orders, and total amount of money spent.
Income has no significant effect on purchase frequency and average value of orders, and has a weak negative correlation with the total amount of consumption.
"""

# Define the binary variables and categorical variables
binary_vars = ['Gender', 'Newsletter_Subscription']
categorical_vars = ['Location', 'Interests', 'Product_Category_Preference']
# Define the target variable
target_var = 'Purchase_Frequency'
# Perform point biserial correlation analysis
point_biserial = point_biserial_correlation(binary_vars, target_var)
# Perform ANOVA analysis
anova = categorical_anova_analysis(categorical_vars, target_var)
# Merge the point biserial correlation and ANOVA results
combined_results = pd.merge(point_biserial, anova, on='Feature', how='outer')
# Consolidate the P-value columns
combined_results['P-value'] = combined_results[['Point Biserial P-value', 'ANOVA P-value']].bfill(axis=1).iloc[:, 0]
# Drop the original P-value columns
combined_results.drop(columns=['Point Biserial P-value', 'ANOVA P-value'], inplace=True)
# Display the combined results
print(combined_results)  #Gender, user location, interests, preference for specific product categories, and whether or not you subscribed to campaign notifications had no significant impact on the average value of orders.

binary_vars = ['Gender', 'Newsletter_Subscription']
categorical_vars = ['Location', 'Interests', 'Product_Category_Preference']
target_var = 'Time_Spent_on_Site_Minutes'

# Perform point biserial correlation analysis
point_biserial = point_biserial_correlation(binary_vars, target_var)
# Perform ANOVA analysis
anova = categorical_anova_analysis(categorical_vars, target_var)
# Merge point biserial correlation and ANOVA results
combined_results = pd.merge(point_biserial, anova, on='Feature', how='outer')
# Consolidate the P-value columns
combined_results['P-value'] = combined_results[['Point Biserial P-value', 'ANOVA P-value']].bfill(axis=1).iloc[:, 0]
combined_results.drop(columns=['Point Biserial P-value', 'ANOVA P-value'], inplace=True)
# Display the combined results
print(combined_results)

binary_vars = ['Gender', 'Newsletter_Subscription']
categorical_vars = ['Location', 'Interests', 'Product_Category_Preference']
target_var = 'Pages_Viewed'
# Perform point biserial correlation analysis
point_biserial = point_biserial_correlation(binary_vars, target_var)
# Perform ANOVA analysis
anova = categorical_anova_analysis(categorical_vars, target_var)
# Merge point biserial correlation and ANOVA results
combined_results = pd.merge(point_biserial, anova, on='Feature', how='outer')
# Consolidate the P-value columns
combined_results['P-value'] = combined_results[['Point Biserial P-value', 'ANOVA P-value']].bfill(axis=1).iloc[:, 0]
combined_results.drop(columns=['Point Biserial P-value', 'ANOVA P-value'], inplace=True)
# Display the combined results
print(combined_results)

num_vars = ['Age', 'Income']
categorical_vars = ['Gender', 'Location', 'Interests']
target_var = 'Newsletter_Subscription'
# Perform ANOVA analysis for numeric variables
anova = numeric_anova_analysis(num_vars, target_var)
# Perform Chi-Square test for categorical variables
chi_square = chi_square_test(categorical_vars, target_var)
# Merge ANOVA results and Chi-Square test results
combined_results = pd.merge(anova, chi_square, on='Feature', how='outer')
# Consolidate the P-value columns
combined_results['P-value'] = combined_results[['Chi-Square Test P-value', 'ANOVA P-value']].bfill(axis=1).iloc[:, 0]
combined_results.drop(columns=['Chi-Square Test P-value', 'ANOVA P-value'], inplace=True)
# Display the combined results
print(combined_results)

"""
Age, gender, income, interests, and location had no significant impact on the number of days since a user last logged in, whether they subscribed to marketing campaign notifications, the number of pages viewed during a visit, or the amount of time spent on the digital platform.
"""


"""
The above results show that most variables are not significant factors affecting user consumption and online behavior, indicating that in this dataset, user behavior has significant randomness, which makes it very complicated to explore its influencing factors. Here are some of the factors that contribute to this randomness:

Individual differences: Each user's consumption preferences and online habits on e-commerce platforms are very different. In the previous clustering, it is not difficult to find that class 3 belongs to the high-income group, but their purchase frequency is relatively low, while class 2 also belongs to the high-income group, but their purchase frequency is particularly high. There are many such cases in the data, and such individual differences make it difficult to use a unified model to capture the behavior of all users.
External environment: The consumer behavior of users is affected by a variety of external factors, such as economic conditions, social trends and marketing activities. For example, during a bad economy, users may reduce non-essential purchases, while during a promotion, users' desire to buy may increase. Of course, there are no such external factors in the data, so it is impossible to explore whether it is affected by the external environment.
Of course, in addition to using statistical tests, some models can also be built to explore the influencing factors, such as: Multiple linear regression model, random forest model, logistic regression model, etc., using regression model to explore the factors affecting the consumption frequency, consumption amount, time spent on e-commerce platform and other numerical variables, using classification model to explore the user's preference for specific product categories, whether to subscribe to the notification of marketing activities of the subtype variables. 
In the same way, you can do feature engineering, build new feature variables, consider interactions, or build polynomials to capture potential influences.
"""












