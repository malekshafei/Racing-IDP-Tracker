import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import plotly.express as px
import plotly.graph_objects as go
import calendar
import os

# Set page config
st.set_page_config(
    page_title="Racing IDP Tracker", 
    #page_icon="⚽",
    layout="wide"
)

player_id_matching = {
   
    'Courtney Petersen': 49057,
    'Lauren Milliet': 33367,

    
    'Arin Wright': 4942,
    'Ellie Jean': 62960,
    'Angela Baron': 403272,
    'Elli Pikkujamsa': 225161,
    'Allie George': 451020,

    'Taylor Flint': 428578,
    'Avery Kalitta': 454905,
    'Marisa DiGrande': 30524,
    'Ary Borges': 389488,
    "Katie O'Kane": 469677,
    "Jordan Baggett": 30652,

    
    'Ella Hase': 453203,

    'Janine Sonis': 4992,
    'Emma Sears': 428576,
    'Sarah Weber': 454724,
    'Kayla Fischer': 389487,
    'Savannah DeMelo': 218506,
    'Uchenna Kanu': 25461

}


# File path for the Excel workbook
EXCEL_FILE = "MitchIDPs.xlsx"
df2 = pd.read_excel(EXCEL_FILE, sheet_name = 'Player Bios')


def load_data():
    """Load data from Excel file, create sample data if file doesn't exist"""
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE, sheet_name = 'Sheet1')

        df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d', dayfirst=False)
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
        

        return df

def save_data(df):
    """Save data to Excel file"""
    try:
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            df2.to_excel(writer, sheet_name='Player Bios', index=False)
        
            #df.to_excel(EXCEL_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

def add_training_entry(player_name, training_type, training_detail, training_date, coach_name, notes, session_id=None):
    """Add a new training entry to the data - returns True/False for success"""
    df = load_data()
    
    if session_id is None:
        if 'Session_ID' in df.columns and not df.empty:
            # Get the highest existing session ID and add 1
            session_id = df['Session_ID'].max() + 1
        else:
            # First entry or no Session_ID column exists
            session_id = 1

    new_entry = {
        "Player": player_name,
        "Type": training_type,
        "Detail": training_detail,
        "Date": training_date.strftime("%Y-%m-%d"),
        "Coach": coach_name,
        "Notes": notes,
        "Session_ID": session_id
    }
    
    # Add new entry to DataFrame
    new_row = pd.DataFrame([new_entry])
    df = pd.concat([df, new_row], ignore_index=True)
    
    # Sort by date (newest first)
    df = df.sort_values("Date", ascending=False)
    
    # Save to Excel and return result
    return save_data(df)




def remove_entry(df, index_to_remove):
    """Remove an entry from the dataframe"""
    df = df.drop(index=index_to_remove).reset_index(drop=True)
    return save_data(df)


def create_training_pie_chart(df_player, col, title_text):
    """Create a pie chart showing training type breakdown"""
    type_counts = df_player[col].value_counts()
    
    fig = px.pie(
        values=type_counts.values,
        names=type_counts.index,
        title = title_text
        #title='Training Types Distribution'
    )
    
    return fig

def display_player_page(player_name, df):
    """Display individual player's training page"""
    
    

    
    raw_player_name = player_name.strip()
    print("")
    print(raw_player_name)
    print("")
    player_row = df2[df2['Player'] == raw_player_name].iloc[0]
    # player_row = df2.loc[df2['Player'] == player_name]

    st.title(f"#{player_row['Kit #']} {player_name}")
    # player_img_path = f'/Users/malekshafei/Downloads/Racing PNGs/{raw_player_name}.png'
    # st.image(player_img_path, width=300)
    st.title(f"📕  Bio")

    col1, col2, col3 = st.columns([0.45,0.45,0.8 ])
    

    from datetime import datetime

    def calculate_age(dob_str):
        dob_1 = datetime.strptime(str(dob_str), "%Y.%m.%d")
        today = datetime.today()
        age = (today - dob_1).days / 365.25
        return round(age, 1)

    dob = player_row['DOB']
    
    with col1:
        st.metric("Age", calculate_age(dob))
        
    with col2:
        st.metric("DOB", dob)  
        
    with col3: 
        st.metric("From", player_row['From'])
        

    col1, col2, col3, col4 = st.columns([0.45,0.15,0.3,0.8 ])

    with col1:
        if pd.isna(player_row['Secondary Position']): pos_string = f"{player_row['Primary Position']}"
        else: pos_string = f"{player_row['Primary Position']} ({player_row['Secondary Position']})"
        st.metric("Primary Position (Secondary)", pos_string)
        
    
    with col2:
        st.metric("Foot", player_row['Foot'])
        
    with col3:
        st.metric("Height", player_row['Height'])

    

    with col4:
        
        
        st.metric("Joined Club", player_row['Joined Club']) 
    
    
    st.title(f"📈 Season Overview")
    game_overview = pd.read_parquet("Racing Mins.parquet")
    
    poss_matches = game_overview['match_id'].nunique()
    max_mins_per_match = game_overview.groupby('match_id')['Minutes'].max()
    poss_mins =  max_mins_per_match.sum()

    player_squad_apps = len(game_overview[(game_overview['Player'] == raw_player_name) & (game_overview['In Squad'] == True)])
    player_starts = len(game_overview[(game_overview['Player'] == raw_player_name) & (game_overview['Started'] == True)])
    player_came_on = len(game_overview[(game_overview['Player'] == raw_player_name) & (game_overview['Came On'] == True)])
    player_apps = player_starts + player_came_on
    player_mins = sum(game_overview[game_overview['Player'] == raw_player_name]['Minutes'])
    pct_possible_mins = int((player_mins / poss_mins) * 100)
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1: st.metric("Made Squad", f"{player_squad_apps}/{poss_matches}")
    with col2: st.metric("Played", f"{player_apps}")
    with col3: st.metric("Started", f"{player_starts}")
    with col4: st.metric("Minutes", f"{player_mins}")
    with col5: st.metric("% of Mins", f"{pct_possible_mins}%")

    if player_mins > 100:
        sb_player_id = player_id_matching[raw_player_name]
        season_data = pd.read_parquet("NWSL2025-AppPlayerSeasonPercentiles.parquet")
        season_data.drop(['Matches Played','pctDistance','pctRunning Distance','pctHSR Distance','pctCount HSR', 'pctSprinting Distance', 'pctSprint Count', 'pctHI Distance', 'pctHI Count', 'pctMedium Accels','pctHigh Accels','pctMedium Decels', 'pctHigh Decels', 'pctWalking to HSR Count', 'pctWalking to Sprint Count', 'pctMatches Played', 'pctTop Speed', 'pctTime to Sprint', 'pctTime to HSR', 'pctWalking Distance', 'pct% of Distance Walking', 'pct% of Distance HI', 'pct% of Distance Sprinting', 'pct% of HI Distance Sprinting','Speed', 'Intensity', 'Explosiveness','Agility'],axis=1)

        # pos_map = {
        #     1: 'GK',
        #     3: 'FB/WB',
        #     4: 'CB',
        #     6: 'CM',
        #     10: 'AM',
        #     7: 'W',
        #     9: 'ST'

        # }

        #season_data['Position Group'] = season_data['pos_group'].apply(lambda x: pos_map.get(x, x))

        player_data = season_data[season_data['player_id'] == sb_player_id]
        #position_minutes = player_data.groupby('Position Group')['Minutes'].sum().to_dict()
        position_minutes = {k: int(v) for k, v in player_data.groupby('Position Group')['Minutes'].sum().to_dict().items()}

        #position_labels = [f"{position} ({position_minutes[position]} mins)" for position in sorted(player_data['Position Group'].unique())]
        position_labels = [
                f"{position} ({position_minutes[position]} mins)" 
                for position in sorted(player_data['Position Group'].unique(), key=lambda pos: position_minutes[pos], reverse=True)
        ]

        col1, col2, col3 = st.columns(3)
        with col1:
            positions = st.pills("Select Position(s)", 
                                position_labels, #sorted(player_data['Position Group'].unique()), 
                                selection_mode = "multi", default = position_labels[0])
            
            positions = [label.split(' ')[0] for label in positions]
            if positions == []: st.error('Please select at least one position')
            comp_data = season_data[season_data['Position Group'].isin(positions)].sort_values(by='Minutes',ascending=False)
            #st.write(positions)
        with col2:
            compare = st.radio('Compare with another player?', ["No", "Yes"])

        with col3:
            if compare == 'Yes': 
                comp_player_name = st.selectbox('Player', comp_data[comp_data['Player'] != raw_player_name]['Player'].unique())
            else: comp_player_name = '...'
        
        median_mins = np.median(comp_data['Minutes'])

        comp_data = comp_data[(comp_data['player_id'] == sb_player_id) | (comp_data['Player'] == comp_player_name) | (comp_data['Minutes'] > median_mins)]
        # highlight = comp_data[(comp_data['player_id'] == sb_player_id) | (comp_data['Player'] == comp_player_name)]
        # #st.write(highlight[['Player', 'pos_group', 'Minutes', 'Top Speed']])
        special_cols = ['Player', 'pos_group', 'Team', 'Competition', 'Season', 'Minutes', 'Number', 'Foot', 'player_id', 'Position', 'Detailed Position', 'Position Group', 'offline_player_id', 'statsbomb_id']
        for col in comp_data.columns:
            if col not in special_cols:#and col not in phys_cols:
                comp_data[col] = comp_data[col] * comp_data['Minutes']


        aggs = {col: 'sum' for col in comp_data.columns if col not in special_cols}
        aggs['Position Group'] = 'first'
        aggs['pos_group'] = 'first'
        aggs['Team'] = 'first'
        aggs['Competition'] = 'first'
        aggs['Season'] = 'first'
        aggs['Minutes'] = 'sum'
        aggs['Number'] = 'first'
        aggs['Foot'] = 'first'
        aggs['player_id'] = 'first'
        aggs['Position'] = 'first'
        aggs['Detailed Position'] = 'first'
        aggs['offline_player_id'] = 'first'
        aggs['statsbomb_id'] = 'first'
        
        
        phys_cols = [
                    'Distance','Running Distance', 'HSR Distance', 'Count HSR',
                    'Sprinting Distance', 'Sprint Count', 'HI Distance', 'HI Count',
                    'Medium Accels', 'High Accels', 'Medium Decels', 'High Decels',
                    'Walking to HSR Count', 'Walking to Sprint Count', 
                    'Top Speed', 'Time to Sprint',
                    'Time to HSR', 'Walking Distance', '% of Distance Walking',
                    '% of Distance HI', '% of Distance Sprinting']
        phys_pct_cols = [
            'pctDistance',
                'pctRunning Distance', 'pctHSR Distance',
            'pctCount HSR', 'pctSprinting Distance', 'pctSprint Count',
            'pctHI Distance', 'pctHI Count', 'pctMedium Accels', 'pctHigh Accels',
            'pctMedium Decels', 'pctHigh Decels', 'pctWalking to HSR Count',
            'pctWalking to Sprint Count', 'pctTop Speed',
            'pctTime to Sprint', 'pctTime to HSR', 'pctWalking Distance',
            'pct% of Distance Walking', 'pct% of Distance HI',
            'pct% of Distance Sprinting', 'pct% of HI Distance Sprinting'
        ]
        
            
        comp_data = comp_data.groupby('Player').agg(aggs).reset_index()
        for col in comp_data.columns:
            if col not in special_cols and col != 'Top Speed':
                comp_data[col] = comp_data[col] / comp_data['Minutes']    
                if col not in phys_cols + phys_pct_cols: comp_data[f'pct{col}'] = round(comp_data[col].rank(pct=True) * 100,2)
                #comp_data[f'pct{col}'].fillna(0)
        
        
        important_metrics = []
        selected_metrics = []

        comp_data['Shot Stopping'] = (0.05 * comp_data['pctGK Shots on Target Faced']) + (0.1 * comp_data['pctBig Chances Save %']) + (0.7 * comp_data['pctGoals Prevented']) + (0.15 * comp_data['pctGK Save %'])
        comp_data['Short Distribution'] = (0.15 * comp_data['pctForward Pass %']) + (0.2 * comp_data['pctPressured Pass %']) + (0.65 * comp_data['pctShort Pass %'])
        comp_data['Long Distribution'] = (0.2 * comp_data['pctProgressive Passes']) + (0.1 * comp_data['pctPasses into Final Third']) +  (0.35 * comp_data['pctLong Passes Completed']) + (0.1 * comp_data['pctPass OBV']) + (0.25 * comp_data['pctLong Pass %'])
        comp_data['Stepping Out'] = (0.1 * comp_data['pctGK Avg. Distance'])
        comp_data['Saving Big Chances'] = (0.25 * comp_data['pctBig Chances Faced']) + (0.75 * comp_data['pctBig Chances Save %'] )
        comp_data['1v1 Saving'] = (1 * comp_data['pctGK 1v1s Save Rate'])
        
        comp_data['Chance Creation'] = (0.3 * comp_data['pctxA']) + (0.15 * comp_data['pctKey Passes']) + (0.25 * comp_data['pctBig Chances Created']) + (0.1 * comp_data['pctPass OBV']) + (0.2 * comp_data['pctAssists'])
        comp_data['Ball Progression'] = (0.2 * comp_data['pctPass OBV']) + (0.15 * comp_data['pctPasses into Final Third']) + (0.25 * comp_data['pctProgressive Carries']) + (0.3 * comp_data['pctProgressive Passes']) + (0.1 * comp_data['pctLong Passes Completed'])
        comp_data['Ball Retention'] = (0.15 * comp_data['pctForward Pass %']) + (0.55 * comp_data['pctBall Retention %']) + (0.2 * comp_data['pctPressured Pass %']) + (0.1 * comp_data['pctShort Pass %'])
        comp_data['Verticality'] = (0.25 * comp_data['pct% of Passes Progressive']) + (0.6 * comp_data['pct% of Passes Forward']) + (0.15 * (1- comp_data['pct% of Passes Backward']))
        comp_data['Carrying'] = (0.25 * comp_data['pctTake Ons']) + (0.1 * comp_data['pctCarries']) + (0.5 * comp_data['pctProgressive Carries']) + (0.15 * comp_data['pctDribble %'])
        comp_data['Poaching'] = (0.55 * comp_data['pctxG']) + (0.2 * comp_data['pctxG/Shot']) + (0.2 * comp_data['pctBox Receptions']) + (0.05 * comp_data['pctSix Yard Box Receptions'])
        comp_data['Finishing'] = (0.25 * comp_data['pctGoals per xG']) + (0.15 * comp_data['pctxGOT per xG']) + (0.45 * comp_data['pctGoal Conversion']) + (0.15 * comp_data['pctGoals'])
        comp_data['Goal Threat'] = (0.3 * comp_data['pctxG']) + (0.3 * comp_data['pctGoals']) + (0.2 * comp_data['pctBox Receptions']) + (0.1 * comp_data['pctGoal Conversion']) + (0.1 * comp_data['pctxGOT per xG'])
        comp_data['Crossing'] = (0.3 * comp_data['pctCrosses Completed into Box']) + (0.2 * comp_data['pctCross into Box %']) + (0.25 * comp_data['pctCross Shot Assists']) + (0.25 * comp_data['pctCross Assists'])
        comp_data['Heading'] = (0.7 * comp_data['pctAerial %']) + (0.3 * comp_data['pctAerial Wins'])
        comp_data['Set Piece Threat'] = (0.75 * comp_data['pctAttacking SP Aerial Wins']) + (0.25 * comp_data['pctAttacking SP Aerial %'])

        # comp_data['Speed'] = (0.4 * comp_data['pctPSV-99']) + (0.45 * comp_data['pctPSV-85']) + (0.15 * comp_data['pctSprinting Distance'])
        # comp_data['HSR Distance'] = (0.4 * comp_data['pctDistance']) + (0.6 * comp_data['pctHI Running Distance'])

        comp_data['High Pressing'] = (0.25 * comp_data['pctAttacking Half Pressures']) + (0.15 * comp_data['pctAttacking Third Pressures']) + (0.2 * comp_data['pctAttacking Half Pressure Regains']) + (0.1 * comp_data['pctPressure Regains Leading to Shots']) + (0.3 * comp_data['pctAverage Defensive Action Distance'])
        comp_data['Defending High'] = (0.2 * comp_data['pctAttacking Half Pressures']) + (0.05 * comp_data['pctAttacking Half Pressure Regains']) + (0.75 * comp_data['pctAverage Defensive Action Distance'])
        comp_data['Tackle Accuracy'] = (0.2 * (100 - comp_data['pctDribbled Past'])) + (0.65 * comp_data['pctTackle %']) + (0.15 * comp_data['pctTackles Won'])
        comp_data['Defensive Output'] = (0.1 * comp_data['pctBlocks']) + (0.3 * comp_data['pctTackles Won']) + (0.4 * comp_data['pctBall Recoveries']) + (0.2 * comp_data['pctInterceptions'])
        comp_data['Receiving Forward'] = (0.6 * comp_data['pctFinal Third Receptions']) + (0.15 * comp_data['pctBox Receptions']) + (0.15 * comp_data['pctShots']) + (0.1 * comp_data['pctxG'])

        # for col in comp_data.columns:
        #     print(col)
        comp_data['Speed'] = (1 * comp_data['pctTop Speed'])
        comp_data['Intensity'] = (0.1 * comp_data['pctDistance']) + (0.3 * comp_data['pctRunning Distance']) + (0.2 * comp_data['pctHSR Distance']) + (0.15 * comp_data['pctSprinting Distance']) + (0.15 * comp_data['pctSprint Count']) + (0.1 * comp_data['pct% of Distance HI'])
        comp_data['Explosiveness'] = (0.3 * comp_data['pctWalking to Sprint Count']) + (0.3 * comp_data['pctWalking to HSR Count']) + (0.2 * (100 - comp_data['pctTime to HSR'])) + (0.2 * (100 - comp_data['pctTime to Sprint']))
        comp_data['Agility'] = (0.2 * comp_data['pctHigh Decels']) + (0.2 * comp_data['pctHigh Accels']) + (0.3 * comp_data['pctMedium Decels']) + (0.3 * comp_data['pctMedium Accels'])


        #highlight = comp_data[(comp_data['player_id'] == sb_player_id) | (comp_data['Player'] == comp_player_name)]
        #st.write(comp_data[['Player', 'pos_group', 'Minutes', 'Top Speed','pctTop Speed', 'Speed']])


        if 'CB' in positions:
                #print('CB')
                important_metrics.append(['Speed','Tackle Accuracy', 'Defending High', 'Defensive Output', 'Heading', 'Ball Retention', 'Ball Progression', 'Verticality'])
                selected_metrics.append(['Top Speed', 'Average Defensive Action Distance', 
                                         'Tackle %', 'Tackles Won',
                                         'Interceptions', 'Blocks',
                                         'Aerial Wins', 'Aerial %',
                                         'Progressive Passes', 'Passes into Final Third', 
                                         'Progressive Carries', 'Ball Retention %'])
        if 'FB/WB' in positions:
            #print('FB/WB')
            important_metrics.append(['Crossing','Chance Creation','Receiving Forward','Speed', 'High Pressing', 'Tackle Accuracy', 'Defensive Output',  'Ball Retention', 'Ball Progression', 'Verticality', 'Heading',])
            selected_metrics.append(['Top Speed', 'HI Distance',
                                        'Key Passes', 'Big Chances Created',
                                        'xA', 'Assists',
                                        'Cross Shot Assists', 'Cross into Box %',
                                        'Tackle %', 'Tackles Won',
                                        'Attacking Third Pressures', 'Attacking Half Pressure Regains'
                                        ])
        if 'CM' in positions:
            #print('CM')
            important_metrics.append(['Tackle Accuracy', 'Defensive Output', 'High Pressing', 'Heading', 'Set Piece Threat', 'Ball Retention', 'Ball Progression', 'Carrying','Receiving Forward','Chance Creation','Speed', 'Intensity', 'Goal Threat', 'Verticality'])
            selected_metrics.append(['Top Speed', 'HI Distance',
                                        'xA', 'Assists',
                                        'xG', 'Goals',
                                        'Progressive Passes', 'Progressive Carries',
                                        'Tackle %', 'Ball Recoveries',
                                        'Attacking Third Pressures', 'Attacking Half Pressure Regains'
                                        ])
            

        if 'AM' in positions:
            #print('AM')
            important_metrics.append(['Chance Creation', 'Carrying', 'Speed', 'Goal Threat', 'Defensive Output', 'High Pressing', 'Chance Creation', 'Ball Progression', 'Ball Retention', 'Crossing',  'Intensity', 'Poaching', 'Finishing'])
            selected_metrics.append(['Top Speed', 'HI Distance',
                                    'Goals', 'xG',
                                    'Box Receptions', 'Goal Conversion',
                                    'Assists', 'xA',
                                    'Progressive Carries', 'Dribble %',
                                    'Attacking Third Pressures', 'Ball Recoveries'])
        if 'W' in positions:
            #print('W')
            important_metrics.append(['Chance Creation', 'Carrying', 'Speed', 'Goal Threat', 'Defensive Output', 'High Pressing', 'Chance Creation', 'Ball Progression', 'Ball Retention', 'Crossing',  'Intensity', 'Poaching', 'Finishing'])
            selected_metrics.append(['Top Speed', 'HI Distance',
                                    'Goals', 'xG',
                                    'Box Receptions', 'Goal Conversion',
                                    'Assists', 'xA',
                                    'Progressive Carries', 'Dribble %',
                                    'Attacking Third Pressures', 'Ball Recoveries'])
            
        if 'ST' in positions:
            #print('ST')
            important_metrics.append(['Finishing', 'Poaching', 'High Pressing', 'Speed', 'Intensity', 'Defensive Output', 'Chance Creation', 'Ball Retention', 'Carrying',  'Goal Threat', 'Heading', 'Set Piece Threat'])
            selected_metrics.append(['Goals', 'xG',
                                    'Shots', 'Box Receptions',
                                    'Goal Conversion', 'Big Chance Conversion',
                                    'Key Passes', 'Ball Retention %',
                                    'Attacking Third Pressures', 'Ball Recoveries',
                                    'Top Speed', 'HI Distance'])

        #important_metrics = list(set(item for sublist in important_metrics for item in sublist))

        all_ratings = ['Speed', 'Intensity', 'Explosivness', 'Agility', 'Defensive Output', 'Defending High', 'High Pressing', 'Tackle Accuracy', 'Heading', 'Ball Retention', 'Ball Progression', 'Verticality', 'Carrying', 'Chance Creation', 'Crossing', 'Poaching', 'Finishing', 'Goal Threat', 'Receiving Forward', 'Set Piece Threat','Shot Stopping', 'Short Distribution', 'Long Distribution', 'Stepping Out', 'Saving Big Chances', '1v1 Saving']
        

        important_ratings_unique = []
        seen = set()
        for sublist in important_metrics:
            for item in sublist:
                if item not in seen:
                    seen.add(item)
                    important_ratings_unique.append(item)

        important_ratings = important_ratings_unique

        #st.write(important_ratings)

        import plotly.graph_objects as go

        def create_comparison_radar(comp_data, player_name, important_ratings, compare=False, comp_player_name=None):
            """Create radar chart for player comparison"""
            
            # Get player data
            player_data = comp_data[comp_data['player_id'] == sb_player_id].iloc[0]
            player_mins = player_data.get('Minutes', 0)
            
            # Get player ratings (assuming they're 0-100 scale)
            player_ratings = [player_data[rating] for rating in important_ratings]
            
            # Process metric names (similar to your original logic)
            processed_metrics = []
            for metric in important_ratings:
                # Remove 'pct' prefix if exists
                if metric.startswith('pct'):
                    metric = metric[3:]
                
                # Add line breaks for long names
                if ' ' in metric:
                    metric = metric.replace(' ', '<br>')
                
                processed_metrics.append(metric)
            
            # Create figure with dark theme
            fig = go.Figure()
            
            # Add main player
            fig.add_trace(go.Scatterpolar(
                r=player_ratings,
                theta=processed_metrics,
                fill='toself',
                name=f'{player_name}',
                line=dict(color='#00ff00', width=2),
                fillcolor='rgba(0, 255, 0, 0.3)',
                marker=dict(size=8, color='#00ff00')
            ))
            
            # Initialize comp_player_mins
            comp_player_mins = None
            
            # Add comparison player if needed
            if compare == 'Yes' and comp_player_name:
                comp_player_data = comp_data[comp_data['Player'] == comp_player_name].iloc[0]
                comp_player_mins = comp_player_data.get('Minutes', 0)
                comp_player_ratings = [comp_player_data[rating] for rating in important_ratings]
                
                fig.add_trace(go.Scatterpolar(
                    r=comp_player_ratings,
                    theta=processed_metrics,
                    fill='toself',
                    name=f'{comp_player_name}',
                    line=dict(color='#ff0000', width=3),
                    fillcolor='rgba(255, 0, 0, 0.4)',
                    marker=dict(size=8, color='#ff0000')
                ))
            
            # Update layout to match your dark theme
            fig.update_layout(
                polar=dict(
                    bgcolor='#200020',
                    #bgcolor = 'rgba(0,0,0,0)',
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        showticklabels=False,
                        gridcolor='white',
                        gridwidth=1,
                        tickvals=[25, 50, 75, 100],
                    ),
                    angularaxis=dict(
                        tickfont=dict(size=14, color='white'),
                        gridcolor='white',
                        gridwidth=1,
                        linecolor='white',
                        linewidth=2
                    )
                ),
                showlegend=False,
                paper_bgcolor='#200020',
                plot_bgcolor='#200020',
                #paper_bgcolor='rgba(0,0,0,0)',
                #plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=14),
                height=600,
                margin=dict(l=80, r=80, t=80, b=80)
            )
            
            # Add main player annotations AFTER layout is set
            fig.add_annotation(
                x=0.05, y=1.18,
                text=f"{player_name}",
                showarrow=False,
                font=dict(size=20, color='#00ff00', family='Arial Black'),
                xref="paper", yref="paper"
            )
            fig.add_annotation(
                x=0.05, y=1.13,
                text=f"{player_mins} mins",
                showarrow=False,
                font=dict(size=15, color='#00ff00'),
                xref="paper", yref="paper"
            )
            
            # Add comparison player annotations if needed
            if compare == 'Yes' and comp_player_name and comp_player_mins is not None:
                fig.add_annotation(
                    x=0.95, y=1.18,
                    text=f"{comp_player_name}",
                    showarrow=False,
                    font=dict(size=20, color='#ff0000', family='Arial Black'),
                    xref="paper", yref="paper",
                    xanchor="right"
                )
                fig.add_annotation(
                    x=0.95, y=1.13,
                    text=f"{comp_player_mins} mins",
                    showarrow=False,
                    font=dict(size=15, color='#ff0000'),
                    xref="paper", yref="paper",
                    xanchor="right"
                )
    
            #return fig, player_mins, comp_player_mins
            
            return fig, player_mins, comp_player_mins if compare == 'Yes' and comp_player_name else None

        
      
        # Create and display radar chart
        if not compare or (compare and comp_player_name):
            radar_fig, player_mins, comp_mins = create_comparison_radar(
                comp_data, 
                player_name, 
                important_ratings, 
                compare=compare, 
                comp_player_name=comp_player_name
            )
            # Display title and minutes like your original
       
        st.plotly_chart(radar_fig, use_container_width=True)
        if comp_data[comp_data['player_id'] == sb_player_id].iloc[0]['Top Speed'] == 0:
            st.warning(f"Physical Data for {raw_player_name} not available")
        if compare == 'Yes' and comp_data[comp_data['Player'] == comp_player_name].iloc[0]['Top Speed'] == 0:
            st.warning(f"Physical Data for {comp_player_name} not available")
        
















    col1, col2 = st.columns([0.5,0.5])


    
    with col1:
        pass
    with col2:
        pass



    st.title(f"🏃‍♂️ Training Profile")
    
    

    # Filter data for selected player
    df_player = df[df['Player'] == raw_player_name].copy()
    
    if len(df_player) != 0:
        print('!!')
        df_player['Date'] = pd.to_datetime(df_player['Date'])
        
        if df_player.empty:
            st.warning(f"No training data found for {player_name}")
            return
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4) 
        
        with col1:
            st.metric("Total Sessions", len(df_player))
        
        with col2:
            recent_sessions = len(df_player[df_player['Date'] >= (datetime.now() - timedelta(days=30))])
            st.metric("Sessions (Last 30 Days)", recent_sessions)
        
        with col3:
            unique_types = df_player['Detail'].nunique() 
            st.metric("Areas Covered", unique_types)
        
        with col4:
            last_session = df_player['Date'].max().strftime('%Y-%m-%d')
            st.metric("Last Session", last_session)
        
        # Charts row
        col1, col2 = st.columns([0.35,0.65])
        
        with col1:
            # Pie chart for training types
            st.subheader("Areas Covered")
            pie_fig = create_training_pie_chart(df_player, 'Type', 'Training Types')
            st.plotly_chart(pie_fig, use_container_width=True)

            pie_fig = create_training_pie_chart(df_player, 'Detail', 'Areas Covered')
            st.plotly_chart(pie_fig, use_container_width=True)
        
        with col2:
            # Calendar heatmap
            
        
        # Recent sessions table
            st.subheader("All Sessions")
            
            # Date range filter
            col1, col2 = st.columns(2)
            with col1:
                if not df_player.empty:
                    earliest_date = pd.to_datetime(df['Date']).min().date()
                else:
                    earliest_date = datetime.now().date() - timedelta(days=30)

                start_date = st.date_input("Start Date", 
                                        value=earliest_date,
                                        key=f"start_{player_name}")

                # start_date = st.date_input("Start Date", 
                #                         value=df_player['Date'].min().date() if not df_player.empty else datetime.now().date() - timedelta(days=30),
                #                         key=f"start_{player_name}")
            
            with col2:
                end_date = st.date_input("End Date", 
                                    value=datetime.now(),
                                    key=f"end_{player_name}")
            
            # Filter by date range
            df_filtered = df_player[
                (df_player['Date'] >= pd.to_datetime(start_date)) &
                (df_player['Date'] <= pd.to_datetime(end_date))
            ]
            
            # Display sessions table
            if not df_filtered.empty:
                display_df = df_filtered.copy()
                display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
                display_df = display_df.sort_values('Date', ascending=False)
                st.dataframe(display_df[['Date', 'Type', 'Detail', 'Coach', 'Notes']], 
                            use_container_width=True, height=400)
            else:
                st.info("No sessions found for the selected date range.")

            st.title(f"🎯 Goals")
        
            col1, col2 = st.columns([0.5,0.5])
            with col1:
                st.write(f"Short Term Goals")
                st.write(f"1. {player_row['Short Term #1']}")
                st.write(f"2. {player_row['Short Term #2']}")
                st.write(f"3. {player_row['Short Term #3']}")

            with col2:
                st.write(f"Long Term Goals")
                st.write(f"1. {player_row['Long Term #1']}")
                st.write(f"2. {player_row['Long Term #2']}")
                st.write(f"3. {player_row['Long Term #3']}")
    else:
        st.info("No sessions with player.")

def main():
    
    
    # Initialize session state for success messages
    if 'show_success' not in st.session_state:
        st.session_state.show_success = False
    if 'success_message' not in st.session_state:
        st.session_state.success_message = ""
    if 'show_error' not in st.session_state:
        st.session_state.show_error = False
    if 'error_message' not in st.session_state:
        st.session_state.error_message = ""
    
    # Load data
    df = load_data()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    
    # Get list of players for individual pages
    players = (df2["Player"].tolist()) if not df2.empty else []
    
    # Navigation options
    nav_options = ["Overview", "Add New Entry", "Remove Entry", "Analytics"] + [f"👤  {player}" for player in players]
    page = st.sidebar.selectbox("Select Page", nav_options)
    
    # Show success/error messages at the top
    if st.session_state.show_success:
        st.success(st.session_state.success_message)
        st.session_state.show_success = False
    
    if st.session_state.show_error:
        st.error(st.session_state.error_message)
        st.session_state.show_error = False
    
    if page == "Overview":
       
        st.title("Racing IDP Tracker")
        
        st.markdown("Track and monitor player training sessions")

        st.header("Training Sessions Overview")
        
        # Player selection
        players_filter = ["All Players"] + players
        selected_player = st.selectbox("Select Player", players_filter)
        
        df_filtered = df.copy()
        # Date range filter
        col1, col2 = st.columns(2)
        with col1:
            if not df_filtered.empty:
                earliest_date = pd.to_datetime(df_filtered['Date']).min().date()
            else:
                earliest_date = datetime.now().date() - timedelta(days=30)

            start_date = st.date_input("Start Date", 
                                    value=earliest_date)
                                    
        with col2:
            end_date = st.date_input("End Date", 
                                   value=datetime.now())
        
        # Filter data
        
        df_filtered['Date'] = pd.to_datetime(df_filtered['Date'])
        
        # Apply filters
        df_filtered = df_filtered[
            (df_filtered['Date'] >= pd.to_datetime(start_date)) &
            (df_filtered['Date'] <= pd.to_datetime(end_date))
        ]
        
        if selected_player != "All Players":
            df_filtered = df_filtered[df_filtered["Player"] == selected_player]
        
        # Display metrics
        if not df_filtered.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Sessions", df_filtered['Session_ID'].nunique())
            with col2:
                st.metric("Players", df_filtered["Player"].nunique())
            with col3:
                spw = round(df_filtered['Session_ID'].nunique() / ((end_date - start_date).days / 7),1)
                st.metric("Sessions per Week", spw)
            
        
        # Display data table
        st.subheader("Training Sessions")
        if not df_filtered.empty:
            display_df = df_filtered.copy()
            display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
            st.dataframe(display_df, use_container_width=True, height=400)
        else:
            st.info("No training sessions found for the selected criteria.")
    
    elif page == "Add New Entry":
        st.header("Add New Training Entry")
        
        # Get existing data for dropdowns
        existing_players = sorted(df2["Player"].unique().tolist()) if not df.empty else []
        existing_types = sorted(df["Type"].unique().tolist()) if not df.empty else []
        existing_details = sorted(df["Detail"].unique().tolist()) if not df.empty else []
        existing_coaches = sorted(df["Coach"].unique().tolist()) if not df.empty else []

        # Default training types
        default_types = ["Individual", 'Combined', 'Group', 'Video', 'Unit Meeting', 'Player Meeting']
        all_types = sorted(list(set(existing_types + default_types)))

        col1, col2 = st.columns(2)
        
        with col1:
            # Player selection
            player_option = st.radio("Player Selection", ["Select Existing", "Add New Player"])
            
            add_multiple = st.checkbox("Add multiple players (group session)")

            if add_multiple:
                if existing_players:
                    selected_players = st.multiselect("Select Players for Group Session", existing_players)
                    player_name = selected_players
                else: player_name = []
            else:
                if player_option == "Select Existing" and existing_players:
                    player_name = st.selectbox("Select Player", existing_players)
                else:
                    player_name = st.text_input("Enter Player Name")
            
            # Training type
            type_option = st.radio("Training Type", ["Select from List", "Enter Custom"])
            if type_option == "Select from List":
                training_type = st.selectbox("Select Training Type", all_types)
            else:
                training_type = st.text_input("Enter Training Type")
            
            # Detail
            detail_option = st.radio("Detail", ["Select from List", "Enter Custom"])
            if detail_option == "Select from List" and existing_details:
                training_detail = st.selectbox("Select Detail", existing_details)
            else:
                training_detail = st.text_input("Enter Detail")
        
        with col2:
            training_date = st.date_input("Date", value=datetime.now().date())
            
            # Coach selection
            coach_option = st.radio("Coach Selection", ["Select Existing", "Add New Coach"])
            if coach_option == "Select Existing" and existing_coaches:
                coach_name = st.selectbox("Select Coach", existing_coaches)
            else:
                coach_name = st.text_input("Enter Coach Name")
            
            notes = st.text_area("Notes", placeholder="Additional notes...")
        
        # Submit button
        if st.button("Add Training Entry", type="primary"):
            if add_multiple:
                if selected_players and training_type and training_type.strip():

                    df_temp = load_data()
                    if 'Session_ID' in df_temp.columns and not df_temp.empty:
                        next_session_id = df_temp['Session_ID'].max() + 1
                    else:
                        next_session_id = 1

                    success_count = 0
                    for player in selected_players:
                        success = add_training_entry(
                            player.strip(), 
                            training_type.strip(), 
                            training_detail.strip() if training_detail else "", 
                            training_date, 
                            coach_name.strip() if coach_name else "", 
                            notes.strip(),
                            session_id=next_session_id
                        )
                        if success:
                            success_count += 1
                    
                    if success_count == len(selected_players):
                        print('hi')
                        st.session_state.show_success = True
                        st.session_state.success_message = f"Group session added for {success_count} players!"
                        st.rerun()
                    else:
                        st.session_state.show_error = True
                        st.session_state.error_message = f"Only {success_count}/{len(selected_players)} entries were saved successfully!"
                        st.rerun() 
                else:
                    st.error("Please select players and fill in training type for group session")

            else:

            
                if player_name and player_name.strip() and training_type and training_type.strip():
                    success = add_training_entry(
                        player_name.strip(), 
                        training_type.strip(), 
                        training_detail.strip() if training_detail else "", 
                        training_date, 
                        coach_name.strip() if coach_name else "", 
                        notes.strip()
                    )
                    if success:
                        st.session_state.show_success = True
                        st.session_state.success_message = "Entry successfully added!"
                        st.rerun()
                    else:
                        st.session_state.show_error = True
                        st.session_state.error_message = "Failed to save entry!"
                        st.rerun()
                else:
                    st.error("Please fill in all required fields (Player and Training Type)")

    elif page == "Remove Entry":
        st.header("Remove Training Entry")
        
        if df.empty:
            st.info("No entries to remove.")
        else:
            # Filter options
            col1, col2 = st.columns(2)
            
            with col1:
                # Player filter
                player_filter_options = ["All Players"] + sorted(df["Player"].unique().tolist())
                selected_player_filter = st.selectbox("Filter by Player", player_filter_options, key="remove_player_filter")
            
            with col2:
                # Date range for filtering
                filter_days = st.selectbox("Show entries from", 
                                         ["Last 7 days", "Last 30 days", "Last 90 days", "All time"],
                                         key="remove_date_filter")
            
            # Apply filters
            df_filtered = df.copy()
            df_filtered['Date'] = pd.to_datetime(df_filtered['Date'])
            
            # Date filter
            if filter_days == "Last 7 days":
                cutoff = datetime.now() - timedelta(days=7)
                df_filtered = df_filtered[df_filtered['Date'] >= cutoff]
            elif filter_days == "Last 30 days":
                cutoff = datetime.now() - timedelta(days=30)
                df_filtered = df_filtered[df_filtered['Date'] >= cutoff]
            elif filter_days == "Last 90 days":
                cutoff = datetime.now() - timedelta(days=90)
                df_filtered = df_filtered[df_filtered['Date'] >= cutoff]
            
            # Player filter
            if selected_player_filter != "All Players":
                df_filtered = df_filtered[df_filtered["Player"] == selected_player_filter]
            
            # Display entries for removal
            if not df_filtered.empty:
                st.subheader(f"Select Entry to Remove ({len(df_filtered)} entries found)")
                
                # Create a display dataframe with formatted dates and row numbers
                display_df = df_filtered.copy()
                display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
                display_df = display_df.sort_values('Date', ascending=False).reset_index()
                
                # Show the data
                st.dataframe(display_df[['Date', 'Player', 'Type', 'Detail', 'Coach', 'Notes']], 
                           use_container_width=True, height=300)
                
                # Entry selection for removal
                st.subheader("Remove Entry")
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Create options for selection (showing key info)
                    options = []
                    for idx, row in display_df.iterrows():
                        option_text = f"{row['Date']} - {row['Player']} - {row['Type']} - {row['Detail']}"
                        options.append((option_text, row['index']))  # Store original index
                    
                    if options:
                        selected_option = st.selectbox(
                            "Select entry to remove:",
                            range(len(options)),
                            format_func=lambda x: options[x][0]
                        )
                        
                        selected_index = options[selected_option][1]  # Get original index
                
                with col2:
                    if st.button("🗑️ Remove Entry", type="secondary", help="This action cannot be undone"):
                        if remove_entry(df, selected_index):
                            st.session_state.show_success = True
                            st.session_state.success_message = "Entry successfully removed!"
                            st.rerun()
                        else:
                            st.session_state.show_error = True
                            st.session_state.error_message = "Failed to remove entry!"
                            st.rerun()
                
                # Show warning
                st.warning("⚠️ Warning: Removing an entry cannot be undone!")
            else:
                st.info("No entries found matching the selected filters.")

    elif page == "Analytics":
        st.header("Training Analytics")
        
        if df.empty:
            st.info("No data available for analytics.")
            return
        
        # Convert date column for analysis
        df_analysis = df.copy()
        df_analysis['Date'] = pd.to_datetime(df_analysis['Date'])
        
        filter_days = st.selectbox("Show entries from", 
                                         ["All time","Last 7 days", "Last 30 days", "Last 90 days"],
                                         key="remove_date_filter")
            
        # Apply filters
        df_filtered = df.copy()
        df_filtered['Date'] = pd.to_datetime(df_filtered['Date'])
        
        # Date filter
        if filter_days == "Last 7 days":
            cutoff = datetime.now() - timedelta(days=7)
        elif filter_days == "Last 30 days":
            cutoff = datetime.now() - timedelta(days=30)

        elif filter_days == "Last 90 days":
            cutoff = datetime.now() - timedelta(days=90)
        else:
            cutoff = datetime.now() - timedelta(days=1000)
            
        # Recent data (last 30 days)
        #recent_cutoff = datetime.now() - timedelta(days=30)
        df_recent = df_analysis[df_analysis['Date'] >= cutoff]
        

        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Sessions by Player")
            if not df_recent.empty:
                player_stats = df_recent.groupby("Player").size().reset_index(name='Sessions')
                player_stats = player_stats.sort_values('Sessions', ascending=False)
                st.dataframe(player_stats, use_container_width=True)
        
        with col2:
            st.subheader("Training Details Distribution")
            if not df_recent.empty:
                type_stats = df_recent.groupby("Detail").size().reset_index(name='Sessions')
                type_stats = type_stats.sort_values('Sessions', ascending=False)
                st.dataframe(type_stats, use_container_width=True)
        
        # Coach performance
        st.subheader("Sessions by Coach (Last 30 Days)")
        if not df_recent.empty:
            coach_stats = df_recent.groupby("Coach").size().reset_index(name='Sessions')
            coach_stats = coach_stats.sort_values('Sessions', ascending=False)
            st.bar_chart(coach_stats.set_index('Coach')['Sessions'])
    
    else:
        # Individual player page
        if page.startswith("👤 "):
            player_name = page[2:]  # Remove the emoji prefix
            display_player_page(player_name, df)
    
    # Footer
    st.markdown("---")
    st.markdown("💡 **Tip:** The app automatically saves data to the Excel file")

if __name__ == "__main__":
    main()