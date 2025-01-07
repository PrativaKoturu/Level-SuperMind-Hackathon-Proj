import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import os

# Page Configuration
st.set_page_config(page_title="Social Media Analytics", page_icon="📊", layout="wide")

# Custom CSS for dark theme and enhanced UI
st.markdown("""
<style>
    .main {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .stPlotlyChart {
        background-color: #2B2B2B;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(255,255,255,0.1);
        padding: 10px;
        margin-bottom: 20px;
    }
    h1, h2, h3 {
        color: #4DA8DA;
        margin-bottom: 20px;
    }
    .stMetric {
        background-color: #2B2B2B;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(255,255,255,0.1);
    }
    .stSelectbox, .stMultiSelect, .stSlider {
        background-color: #2B2B2B;
        color: #FFFFFF;
        border-radius: 5px;
        padding: 5px;
        margin-bottom: 10px;
    }
    .stDateInput {
        background-color: #2B2B2B;
        color: #FFFFFF;
        border-radius: 5px;
        padding: 5px;
        margin-bottom: 10px;
    }
    .stTextInput {
        background-color: #2B2B2B;
        color: #FFFFFF;
        border-radius: 5px;
        padding: 5px;
        margin-bottom: 10px;
    }
    .stDataFrame {
        background-color: #2B2B2B;
        color: #FFFFFF;
        border-radius: 10px;
        padding: 10px;
    }
    .filter-container {
        background-color: #2B2B2B;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Load and process data
@st.cache_data
def load_data(file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        
        df = pd.read_csv(file_path)
        
        # Process the data
        df['post_datetime'] = pd.to_datetime(df['post_datetime'], errors='coerce')
        numeric_columns = ['post_reach', 'likes', 'comments', 'shares', 'saves', 'engagement_rate']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Using sample data instead.")
        # Create sample data
        df = pd.DataFrame({
            'post_id': range(1, 101),
            'platform': ['Twitter', 'Facebook', 'Instagram', 'LinkedIn'] * 25,
            'post_type': ['image', 'video', 'text', 'link'] * 25,
            'is_paid_promotion': [True, False] * 50,
            'num_hashtags': [0, 1, 2, 3, 4, 5] * 17,
            'post_datetime': pd.date_range(start='2023-01-01', periods=100, freq='D'),
            'day_of_week': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'] * 15,
            'post_reach': np.random.randint(1000, 10000, 100),
            'likes': np.random.randint(50, 500, 100),
            'comments': np.random.randint(10, 100, 100),
            'shares': np.random.randint(5, 50, 100),
            'saves': np.random.randint(0, 20, 100),
            'content_length': np.random.randint(50, 500, 100),
            'watch_time': np.random.randint(0, 300, 100),
            'engagement_rate': np.random.uniform(1, 10, 100)
        })
        return df

# Specify the file path
file_path = 'social_media_post_performance.csv'  # Adjust this to your actual file path
data = load_data(file_path)

# Dashboard Title
st.title("📊 Social Media Performance Analytics")
st.markdown("*Real-time insights into your social media performance*")

# Overview metrics
st.header("📈 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Posts", f"{len(data):,}")
col2.metric("Avg. Engagement Rate", f"{data['engagement_rate'].mean():.2f}%")
col3.metric("Total Reach", f"{data['post_reach'].sum():,}")
col4.metric("Top Platform", data['platform'].value_counts().index[0])

# Performance Over Time
st.header("📅 Performance Over Time")
with st.container():
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2,2,1])
    with col1:
        metric_options = ['post_reach', 'engagement_rate', 'likes', 'comments', 'shares']
        selected_metric = st.selectbox("Select Metric", options=metric_options)
    with col2:
        date_range = st.date_input("Select Date Range", 
                                   [data['post_datetime'].min().date(), data['post_datetime'].max().date()])
    with col3:
        rolling_window = st.number_input("Rolling Average Window", min_value=1, max_value=30, value=7)
    st.markdown('</div>', unsafe_allow_html=True)

filtered_data = data[(data['post_datetime'].dt.date >= date_range[0]) & (data['post_datetime'].dt.date <= date_range[1])]
filtered_data = filtered_data.sort_values('post_datetime')
filtered_data['rolling_average'] = filtered_data[selected_metric].rolling(window=rolling_window).mean()

fig_time = go.Figure()
fig_time.add_trace(go.Scatter(x=filtered_data['post_datetime'], y=filtered_data[selected_metric],
                              mode='markers', name='Actual', marker=dict(color='#4DA8DA', size=5)))
fig_time.add_trace(go.Scatter(x=filtered_data['post_datetime'], y=filtered_data['rolling_average'],
                              mode='lines', name=f'{rolling_window}-day Rolling Average', line=dict(color='#FF6B6B', width=2)))

fig_time.update_layout(
    title=f'{selected_metric.replace("_", " ").title()} Over Time',
    xaxis_title="Date",
    yaxis_title=selected_metric.replace("_", " ").title(),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font_color='#FFFFFF',
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#FFFFFF'))
)
st.plotly_chart(fig_time, use_container_width=True)

# Platform Analysis
st.header("📱 Platform Performance")
with st.container():
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    platform_filter = st.multiselect("Select Platforms", options=data['platform'].unique(), default=data['platform'].unique())
    st.markdown('</div>', unsafe_allow_html=True)

platform_data = data[data['platform'].isin(platform_filter)]
col1, col2 = st.columns(2)

with col1:
    platform_dist = platform_data['platform'].value_counts().reset_index()
    platform_dist.columns = ['Platform', 'Count']
    fig_platform = px.bar(platform_dist, x='Platform', y='Count', 
                          title='Posts Distribution by Platform', color='Platform')
    fig_platform.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#FFFFFF')
    st.plotly_chart(fig_platform, use_container_width=True)

with col2:
    platform_engagement = platform_data.groupby('platform')['engagement_rate'].mean().reset_index()
    fig_engagement = px.pie(platform_engagement, values='engagement_rate', names='platform',
                            title='Engagement Rate by Platform', hole=0.4)
    fig_engagement.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#FFFFFF')
    st.plotly_chart(fig_engagement, use_container_width=True)

# Content Analysis
st.header("📝 Content Analysis")
with st.container():
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    post_type_filter = st.multiselect("Select Post Types", options=data['post_type'].unique(), default=data['post_type'].unique())
    st.markdown('</div>', unsafe_allow_html=True)

post_type_data = data[data['post_type'].isin(post_type_filter)]
col1, col2 = st.columns(2)

with col1:
    post_type_dist = post_type_data['post_type'].value_counts().reset_index()
    post_type_dist.columns = ['Post Type', 'Count']
    fig_post_type = px.bar(post_type_dist, x='Post Type', y='Count', 
                           title='Distribution of Post Types', color='Post Type')
    fig_post_type.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#FFFFFF')
    st.plotly_chart(fig_post_type, use_container_width=True)

with col2:
    avg_engagement = post_type_data.groupby('post_type')['engagement_rate'].mean().reset_index()
    fig_avg_engagement = px.bar(avg_engagement, x='post_type', y='engagement_rate',
                                title='Average Engagement Rate by Post Type', color='post_type')
    fig_avg_engagement.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#FFFFFF')
    st.plotly_chart(fig_avg_engagement, use_container_width=True)

# Engagement Analysis
st.header("🔍 Engagement Analysis")
with st.container():
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    platform_scatter = st.multiselect("Select Platforms for Scatter Plot", options=data['platform'].unique(), default=data['platform'].unique())
    st.markdown('</div>', unsafe_allow_html=True)

scatter_data = data[data['platform'].isin(platform_scatter)]
fig_scatter = px.scatter(scatter_data, x='content_length', y='engagement_rate', 
                         color='platform', size='post_reach',
                         hover_data=['post_id', 'post_type'],
                         title='Engagement Rate vs Content Length')
fig_scatter.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font_color='#FFFFFF',
    xaxis_title="Content Length",
    yaxis_title="Engagement Rate (%)"
)
st.plotly_chart(fig_scatter, use_container_width=True)

# Hashtag Analysis
st.header("#️⃣ Hashtag Analysis")
with st.container():
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    max_hashtags = st.slider("Max number of hashtags", min_value=1, max_value=int(data['num_hashtags'].max()), value=int(data['num_hashtags'].max()))
    st.markdown('</div>', unsafe_allow_html=True)

hashtag_data = data[data['num_hashtags'] <= max_hashtags]
hashtag_impact = hashtag_data.groupby('num_hashtags')['engagement_rate'].mean().reset_index()
fig_hashtags = px.line(hashtag_impact, x='num_hashtags', y='engagement_rate',
                       title='Impact of Number of Hashtags on Engagement Rate')
fig_hashtags.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font_color='#FFFFFF',
    xaxis_title="Number of Hashtags",
    yaxis_title="Average Engagement Rate (%)"
)
st.plotly_chart(fig_hashtags, use_container_width=True)

# Day of Week Analysis
st.header("📆 Day of Week Analysis")
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_performance = data.groupby('day_of_week')['engagement_rate'].mean().reindex(day_order).reset_index()
fig_day = px.bar(day_performance, x='day_of_week', y='engagement_rate',
                 title='Average Engagement Rate by Day of Week', color='day_of_week')
fig_day.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font_color='#FFFFFF',
    xaxis_title="Day of Week",
    yaxis_title="Average Engagement Rate (%)"
)
st.plotly_chart(fig_day, use_container_width=True)

# Paid vs Organic Performance
st.header("💰 Paid vs Organic Performance")
paid_vs_organic = data.groupby('is_paid_promotion')[['likes', 'comments', 'shares', 'engagement_rate']].mean().reset_index()
paid_vs_organic['is_paid_promotion'] = paid_vs_organic['is_paid_promotion'].map({True: 'Paid', False: 'Organic'})
fig_paid = px.bar(paid_vs_organic, x='is_paid_promotion', y=['likes', 'comments', 'shares', 'engagement_rate'],
                  title='Paid vs Organic Performance Metrics', barmode='group')
fig_paid.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#FFFFFF')
st.plotly_chart(fig_paid, use_container_width=True)

# Top Performing Posts
st.header("🏆 Top Performing Posts")
top_posts = data.nlargest(10, 'engagement_rate')[
    ['post_id', 'platform', 'post_type', 'engagement_rate', 'post_reach', 'likes', 'comments', 'shares']
]
st.dataframe(top_posts.style.format({
    'engagement_rate': '{:.2f}%',
    'post_reach': '{:,.0f}',
    'likes': '{:,.0f}',
    'comments': '{:,.0f}',
    'shares': '{:,.0f}'
}))

# Full CSV Data Table
st.header("📊 Full Data Table")
st.markdown('<div class="filter-container">', unsafe_allow_html=True)
search_term = st.text_input("Search posts", "")
st.markdown('</div>', unsafe_allow_html=True)

if search_term:
    filtered_full_data = data[data.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
else:
    filtered_full_data = data

st.dataframe(filtered_full_data.style.format({
    'engagement_rate': '{:.2f}%',
    'post_reach': '{:,.0f}',
    'likes': '{:,.0f}',
    'comments': '{:,.0f}',
    'shares': '{:,.0f}',
    'saves': '{:,.0f}'
}), height=400)

# Footer
st.markdown("---")
st.markdown(f"Dashboard last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")