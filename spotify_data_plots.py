# %%
from dotenv import load_dotenv
import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth


# %%
FEATURE_COLORS = {'Instrumentalness': '#636EFA', 'Danceability': '#EF553B', 'Acousticness': '#00CC96', 'Valence': '#AB63FA', 'Energy': '#FFA15A', 'Speechiness': '#19D3F3'}
MONTHS = {
            1: 'September',
            2: 'October',
            3: 'November',
            4: 'December',
            5: 'January',
            6: 'February',
            7: 'March',
            8: 'April',
            9: 'May',
            10: 'June',
            11: 'July',
            12: 'August'
        }

FIGS = {}

my_account_df = pd.read_json('MyData/StreamingHistory0.json')


# %%
my_account_df = my_account_df.rename(columns={'artistName':'Artist','trackName':'Track'})

if os.path.isfile('podcasts.csv'):
    podcasts_df = pd.read_csv('podcasts.csv')['Artist']
    #remove rows with podcast artists
    my_account_df = my_account_df[~my_account_df['Artist'].isin(podcasts_df)]

#create a dataframe for skipped tracks and remove those rows from my_account_df
skipped_tracks_df = my_account_df.loc[my_account_df['msPlayed'] < 10000] 
my_account_df = pd.concat([my_account_df,skipped_tracks_df]).drop_duplicates(keep=False)

#convert playtime from ms to hours
my_account_df['endTime'] = pd.to_datetime(my_account_df['endTime'])
my_account_df = my_account_df.rename(columns={'msPlayed':'hours'})
my_account_df['hours'] = my_account_df.hours.apply(lambda x: (x/1000)/3600)

# %%

daily_hours_df = my_account_df.groupby([my_account_df.endTime.dt.hour]).hours.sum()
daily_hours_df = daily_hours_df.reset_index()
fig = px.bar(daily_hours_df, x='endTime', y = 'hours' ,title = 'Total Hours Played By Hour of the Day')
fig.update_layout(
    xaxis_title='',
)
fig.update_xaxes(tickmode='linear')

FIGS['daily_hours'] = fig

# %%
top_aritists_df = my_account_df.groupby(['Artist']).hours.sum().sort_values(ascending=False).head(5)

ARTIST_COLORS = dict(zip(top_aritists_df.index.to_list(),px.colors.qualitative.Plotly))

top_month_df = my_account_df[my_account_df['Artist'].isin(top_aritists_df.index)].groupby(['Artist',my_account_df.endTime.dt.month]).hours.sum()
bottom_month_df = my_account_df[~my_account_df['Artist'].isin(top_aritists_df.index)].copy()
bottom_month_df['Artist'] = 'Other'
bottom_month_df = bottom_month_df.groupby(['Artist',bottom_month_df.endTime.dt.month]).hours.sum()
combined_df = pd.concat([bottom_month_df,top_month_df])

combined_df_months = combined_df.reset_index()
combined_df_months.endTime = combined_df_months.endTime.map(MONTHS)

fig = px.bar(combined_df_months , x='endTime', y='hours', color='Artist', color_discrete_map=ARTIST_COLORS , title = 'Total Hours Played By Month')
fig.update_layout(
    xaxis_title='',
)
FIGS['monthly_hours'] = fig



# %%

fig = px.pie(combined_df_months, values='hours', names=combined_df_months['Artist'].values, color='Artist' , color_discrete_map=ARTIST_COLORS , title='Top 5 Artists Distribution of Hours Played',labels={'hours': 'Hours', 'Artist': 'Artist'}, hole=.4)
fig.update_traces(hovertemplate='Artist=%{label}<br>Hours=%{value}')
FIGS['total_distribution_hours_played'] = fig


# %%
monthly_hours_df = my_account_df.groupby([my_account_df.endTime.dt.month]).hours.sum()
monthly_hours_df.index = monthly_hours_df.index.map(MONTHS)

merged_df = pd.merge(monthly_hours_df, combined_df_months, on='endTime')

merged_df.groupby(['endTime','Artist']).sum().reset_index()

merged_df['Ratio'] = (merged_df['hours_y']/merged_df['hours_x'])*100
merged_df

fig = px.bar(merged_df , x='endTime', y='Ratio', color='Artist', color_discrete_map=ARTIST_COLORS , title = 'Top 5 Artist Ratio of Hours Played by Month')
fig.update_layout(
    xaxis_title='',
)
FIGS['monthly_ratio_hours_played'] = fig


# %%
load_dotenv()
client_ID = os.getenv('client_ID')
client_SECRET = os.getenv('client_SECRET')
redirect_uri = os.getenv('client_redirect_uri')
username = os.getenv('username')

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_ID, client_secret= client_SECRET, redirect_uri=redirect_uri))




# %%
if os.path.isfile('features.csv'):
    df = pd.read_csv('features.csv')
else:
    top_tracks_df = my_account_df.groupby(['Artist','Track']).hours.sum().sort_values(ascending=False).head(500).reset_index()
    d=[]
    print('Fetching track features from Spotify')
    for (track,artist) in top_tracks_df[['Track','Artist']].value_counts().index:
        results = sp.search(q=f"artist:{artist} track:{track}", type='track',limit=1)['tracks']['items']
        if not results:
            print(f"Skipped {track},{artist} : not found")
            continue
        result = results[0]
        features = sp.audio_features(result['id'])
        if not features[0]:
            print(f"Skipped {track},{artist} : no features")
            continue
        if result['name'] == track and result['artists'][0]['name'] == artist:
            d.append({
                            'Track' : result['name'],
                            'Artist' : result['artists'][0]['name'],
                            'Track Number' : result['track_number'],
                            'Popularity' : result['popularity'],
                            'Explicit' : result['explicit'],
                            'Duration' : result['duration_ms'],
                            'Acousticness' : features[0]['acousticness'],
                            'Danceability' : features[0]['danceability'],
                            'Energy' : features[0]['energy'],
                            'Instrumentalness' : features[0]['instrumentalness'] ,
                            'Loudness' : features[0]['loudness'],
                            'Speechiness' : features[0]['speechiness'],
                            'Valence': features[0]['valence'],
                            'Time Signature' : features[0]['time_signature'],
                            'Tempo' : features[0]['tempo'],
                        }  
            )
        else:
            print(f"Skipped {track},{artist} : not found")
    df = pd.DataFrame(d)
    df.to_csv('features.csv', index=False)

# %%

features_df = df[['Acousticness','Speechiness','Valence','Danceability','Energy','Instrumentalness']]
features_df = features_df[sorted(features_df.columns,key=lambda x: x)]

fig = px.histogram(features_df,barmode = 'overlay',color_discrete_map=FEATURE_COLORS,title='Audio Feature Histogram',labels={'variable':'Feature'})

FIGS['features_histogram'] = fig

# %%
mean_df = features_df.mean()
mean_df = mean_df.reset_index().rename(columns={0: 'Value','index':'Feature'}).sort_values(by='Value',ascending=True)

fig = px.bar(mean_df, x='Value', y='Feature', color='Feature' ,color_discrete_map=FEATURE_COLORS, title = 'Audio Feature Mean Values')
fig.update_layout(
    xaxis_title='',
    yaxis_title='',
)
FIGS['features_mean'] = fig


# %%
std_df = features_df.std()
std_df = std_df.reset_index().rename(columns={0: 'Value','index':'Feature'}).sort_values(by='Value',ascending=True)

fig = px.bar(std_df, x='Value', y='Feature', color='Feature' ,color_discrete_map=FEATURE_COLORS, title = 'Audio Feature Standard Deviation Values')
fig.update_layout(
    xaxis_title='',
    yaxis_title='',
)
FIGS['features_std'] = fig


# %%
df['Duration'] = (df['Duration']/1000)/60
fig = px.histogram(df, x='Duration', title='Duration Histogram')
fig.update_layout(
    xaxis_title='Duration (minutes)',
)
FIGS['duration'] = fig


# %%
fig = px.histogram(df, x='Tempo',title='Tempo Histogram')
FIGS['tempo'] = fig

# %%
fig = px.histogram(df, x='Popularity',title = 'Popularity Histogram')
FIGS['popularity'] = fig

# %%
with open('plots.html', 'a') as f:
    for fig in FIGS:
        f.write(FIGS[fig].to_html(full_html=False, include_plotlyjs='cdn'))




