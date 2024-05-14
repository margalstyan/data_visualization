import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode


# Load the dataset
@st.cache_data
def load_data():
    data = pd.read_csv('googleplaystore_1.csv')
    return data

filtered_data = load_data()
data = load_data()

# Filter options
filters = ['Category', 'Rating', 'Reviews', 'Installs', 'Genres']

# Filter unique categories
categories = data['Category'].unique()

# Select 6 random categories by default
if 'default_categories' not in st.session_state:
    st.session_state['default_categories'] = np.random.choice(categories, size=6, replace=False)

# Sidebar filters
st.sidebar.header('Filter Options')
selected_filters = st.sidebar.multiselect('Select Filters', filters)
filtered_data['Installs'] = filtered_data['Installs'].str.replace(',', '')
filtered_data['Installs'] = filtered_data['Installs'].str.replace('+', '').astype(int)

if 'Rating' in selected_filters:
    selected_rating = st.sidebar.slider('Select Rating', min_value=0, value=(0, 5), max_value=5)

    # Filter data based on selection
    filtered_data = filtered_data[data['Rating'].between(selected_rating[0], selected_rating[1])]

if 'Installs' in selected_filters:
    max_installs = filtered_data['Installs'].max()

    selected_installs = st.sidebar.slider('Select Installs', min_value=0, value=(0, max_installs), max_value=max_installs)

    # Filter data based on selection
    filtered_data = filtered_data[data['Rating'].between(selected_installs[0], selected_installs[1])]

if 'Reviews' in selected_filters:
    max_reviewers = filtered_data['Reviews'].max()
    selected_reviewers = st.sidebar.slider('Select Reviewers Range', min_value=0, value=[0, max_reviewers], max_value=max_reviewers)

    # Filter data based on selection
    filtered_data = filtered_data[data['Reviews'].between(selected_reviewers[0], selected_reviewers[1])]

if 'Genres' in selected_filters:
    genres_set = set()
    for genres in filtered_data['Genres']:
        for genre in genres.split(';'):
            genres_set.add(genre.strip())
    selected_genres = st.sidebar.multiselect('Select Genres', genres_set)
    if selected_genres:
        # Filter data based on selection
        filtered_data = filtered_data[data['Genres'].isin(selected_genres)]
    else:
        st.subheader('Please select at least one genre to see the charts.')

if 'Category' in selected_filters:
    selected_categories = st.sidebar.multiselect('Select Categories', categories, default=st.session_state['default_categories'])

    # Filter data based on selection
    filtered_data = filtered_data[data['Category'].isin(selected_categories)]

    # Display metrics
    st.header('App Data Analysis')
    if selected_categories:
        st.subheader(f'Selected Categories: {", ".join(selected_categories)}')

        # Calculate metrics
        mean_ratings = filtered_data.groupby('Category')['Rating'].mean()
        percentage_free_apps = filtered_data.groupby('Category')['Type'].apply(lambda x: (x == 'Free').mean() * 100)

        # Bar plot for mean ratings
        st.subheader('Mean Rating by Category')
        fig, ax = plt.subplots()
        mean_ratings.plot(kind='bar', ax=ax)
        ax.set_ylabel('Mean Rating')
        ax.set_xlabel('Category')
        ax.set_title('Mean Rating by Category')
        st.pyplot(fig)

        # line plot for percentage of free apps
        st.subheader('Percentage of Free Apps by Category')
        fig, ax = plt.subplots()
        percentage_free_apps.plot(kind='line', ax=ax)
        ax.set_ylabel('Percentage of Free Apps (%)')
        ax.set_xlabel('Category')
        ax.set_title('Percentage of Free Apps by Category')
        st.pyplot(fig)

        # Top 10 highest-rated apps
        st.subheader('Top 10 Highest-Rated Apps')
        top_10_apps = filtered_data.nlargest(10, 'Rating')[['App', 'Rating', 'Genres']].sort_values(by='Rating', ascending=False)
        st.table(top_10_apps)

        # Top categories
        st.subheader('Top Categories')

        # Calculate sum of installs for each category
        category_installs_sum = filtered_data.groupby('Category')['Installs'].sum()
        top_categories = st.table(category_installs_sum.sort_values(ascending=False))

    else:
        st.subheader('Please select at least one category to see the charts.')




# Display filtered data table with pagination and sorting




# Pagination settings
rows_per_page = 10
total_rows = len(filtered_data)
total_pages = (total_rows - 1) // rows_per_page + 1

# Streamlit slider for page selection
page = st.slider('Page', 1, total_pages, 1)

# Display paginated DataFrame
start_row = (page - 1) * rows_per_page
end_row = start_row + rows_per_page
paginated_df = filtered_data.iloc[start_row:end_row]

# Grid options for AgGrid
gb = GridOptionsBuilder.from_dataframe(paginated_df)
gb.configure_pagination(paginationPageSize=rows_per_page)
gb.configure_default_column(sortable=True)

gridOptions = gb.build()

# Display the grid
AgGrid(
    paginated_df,
    gridOptions=gridOptions,
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    update_mode='MODEL_CHANGED'
)

st.write(f"Page {page} of {total_pages}")
