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

# File path for the Excel workbook
EXCEL_FILE = "MitchIDPs.xlsx"

def load_data():
    """Load data from Excel file, create sample data if file doesn't exist"""
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)

        df['Date'] = pd.to_datetime(df['Date'], format='mixed', dayfirst=False)
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
        
        return df

def save_data(df):
    """Save data to Excel file"""
    try:
        df.to_excel(EXCEL_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

def add_training_entry(player_name, training_type, training_detail, training_date, coach_name, notes):
    """Add a new training entry to the data - returns True/False for success"""
    df = load_data()
    
    new_entry = {
        "Player": player_name,
        "Type": training_type,
        "Detail": training_detail,
        "Date": training_date.strftime("%Y-%m-%d"),
        "Coach": coach_name,
        "Notes": notes
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

def create_calendar_heatmap(df_player):
    """Create a calendar heatmap showing training sessions by day"""
    # Convert Date to datetime
    df_player['Date'] = pd.to_datetime(df_player['Date'])
    
    # Count sessions per day
    daily_sessions = df_player.groupby(df_player['Date'].dt.date).size().reset_index()
    daily_sessions.columns = ['Date', 'Sessions']
    
    # Create a complete date range for the last 3 months
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=90)
    
    # Create all dates in range
    all_dates = pd.date_range(start=start_date, end=end_date, freq='D')
    df_calendar = pd.DataFrame({'Date': all_dates.date})
    
    # Merge with session counts
    df_calendar = df_calendar.merge(daily_sessions, on='Date', how='left')
    df_calendar['Sessions'] = df_calendar['Sessions'].fillna(0)
    
    # Add calendar information
    df_calendar['Date'] = pd.to_datetime(df_calendar['Date'])
    df_calendar['Day'] = df_calendar['Date'].dt.day
    df_calendar['Month'] = df_calendar['Date'].dt.month
    df_calendar['Year'] = df_calendar['Date'].dt.year
    df_calendar['Weekday'] = df_calendar['Date'].dt.dayofweek
    df_calendar['Week'] = df_calendar['Date'].dt.isocalendar().week
    
    # Create heatmap
    fig = px.density_heatmap(
        df_calendar,
        x='Week',
        y='Weekday',
        z='Sessions',
        title='Training Sessions Calendar (Last 3 Months)',
        labels={'Sessions': 'Sessions per Day', 'Weekday': 'Day of Week', 'Week': 'Week of Year'},
        color_continuous_scale='Blues'
    )
    
    # Update y-axis to show day names
    fig.update_yaxes(
        tickmode='array',
        tickvals=list(range(7)),
        ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    )
    
    return fig

def create_training_pie_chart(df_player):
    """Create a pie chart showing training type breakdown"""
    type_counts = df_player['Type'].value_counts()
    
    fig = px.pie(
        values=type_counts.values,
        names=type_counts.index,
        title='Training Types Distribution'
    )
    
    return fig

def display_player_page(player_name, df):
    """Display individual player's training page"""
    st.title(f"🏃‍♂️ {player_name}'s Training Profile")
    
    # Filter data for selected player
    df_player = df[df['Player'] == player_name].copy()
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
        unique_types = df_player['Type'].nunique()
        st.metric("Training Types", unique_types)
    
    with col4:
        last_session = df_player['Date'].max().strftime('%Y-%m-%d')
        st.metric("Last Session", last_session)
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart for training types
        pie_fig = create_training_pie_chart(df_player)
        st.plotly_chart(pie_fig, use_container_width=True)
    
    with col2:
        # Calendar heatmap
        calendar_fig = create_calendar_heatmap(df_player)
        st.plotly_chart(calendar_fig, use_container_width=True)
    
    # Recent sessions table
    st.subheader("Recent Training Sessions")
    
    # Date range filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", 
                                 value=datetime.now() - timedelta(days=30),
                                 key=f"start_{player_name}")
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

def main():
    st.title("Racing IDP Tracker")
    st.markdown("Track and monitor player training sessions")
    
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
    players = sorted(df["Player"].unique().tolist()) if not df.empty else []
    
    # Navigation options
    nav_options = ["Overview", "Add New Entry", "Remove Entry", "Analytics"] + [f"👤 {player}" for player in players]
    page = st.sidebar.selectbox("Select Page", nav_options)
    
    # Show success/error messages at the top
    if st.session_state.show_success:
        st.success(st.session_state.success_message)
        st.session_state.show_success = False
    
    if st.session_state.show_error:
        st.error(st.session_state.error_message)
        st.session_state.show_error = False
    
    if page == "Overview":
        st.header("Training Sessions Overview")
        
        # Player selection
        players_filter = ["All Players"] + players
        selected_player = st.selectbox("Select Player", players_filter)
        
        # Date range filter
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", 
                                     value=datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", 
                                   value=datetime.now())
        
        # Filter data
        df_filtered = df.copy()
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
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Sessions", len(df_filtered))
            with col2:
                st.metric("Players", df_filtered["Player"].nunique())
            with col3:
                st.metric("Training Types", df_filtered["Type"].nunique())
            with col4:
                st.metric("Coaches", df_filtered["Coach"].nunique())
        
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
        existing_players = sorted(df["Player"].unique().tolist()) if not df.empty else []
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
        
        # Recent data (last 30 days)
        recent_cutoff = datetime.now() - timedelta(days=30)
        df_recent = df_analysis[df_analysis['Date'] >= recent_cutoff]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Sessions by Player (Last 30 Days)")
            if not df_recent.empty:
                player_stats = df_recent.groupby("Player").size().reset_index(name='Sessions')
                player_stats = player_stats.sort_values('Sessions', ascending=False)
                st.dataframe(player_stats, use_container_width=True)
        
        with col2:
            st.subheader("Training Types Distribution")
            if not df_recent.empty:
                type_stats = df_recent.groupby("Type").size().reset_index(name='Sessions')
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