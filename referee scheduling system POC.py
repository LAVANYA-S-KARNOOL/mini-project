import pandas as pd
import os
import streamlit as st

class RefereeScheduler:
    def _init_(self):
        self.load_data()

    def load_data(self):
        # Load or initialize referees DataFrame
        if os.path.exists('referees.json'):
            self.referee_df = pd.read_json('referees.json')
        else:
            self.referee_df = pd.DataFrame(columns=['Name', 'Expertise', 'Availability'])
        
        # Load or initialize games DataFrame
        if os.path.exists('games.json'):
            self.game_df = pd.read_json('games.json')
            if 'Game ID' not in self.game_df.columns:
                self.game_df['Game ID'] = pd.Series(dtype=str)
        else:
            self.game_df = pd.DataFrame(columns=['Game ID', 'Game Name', 'Assigned Referees'])
        
        # Ensure 'Game ID' is of string type
        self.game_df['Game ID'] = self.game_df['Game ID'].astype(str)
        
        # Load or initialize feedback DataFrame
        if os.path.exists('feedback.json'):
            self.feedback_df = pd.read_json('feedback.json')
        else:
            self.feedback_df = pd.DataFrame(columns=['Game ID', 'Referee Name', 'Performance'])

    def save_data(self):
        self.referee_df.to_json('referees.json', orient='records')
        self.game_df.to_json('games.json', orient='records')
        self.feedback_df.to_json('feedback.json', orient='records')

    def add_referee(self, name, expertise):
        new_referee = pd.DataFrame({'Name': [name], 'Expertise': [expertise], 'Availability': [True]})
        self.referee_df = pd.concat([self.referee_df, new_referee], ignore_index=True)
        self.save_data()

    def add_game(self, game_id, game_name):
        new_game = pd.DataFrame({'Game ID': [game_id], 'Game Name': [game_name], 'Assigned Referees': [[]]})
        self.game_df = pd.concat([self.game_df, new_game], ignore_index=True)
        self.save_data()

    def assign_referee_to_game(self, game_id, referee_name):
        if referee_name not in self.referee_df['Name'].values or game_id not in self.game_df['Game ID'].values:
            return False, "Referee not found or Game not found"
        game_idx = self.game_df[self.game_df['Game ID'] == game_id].index[0]
        assigned_referees = self.game_df.at[game_idx, 'Assigned Referees']
        assigned_referees.append(referee_name)
        self.game_df.at[game_idx, 'Assigned Referees'] = assigned_referees
        self.save_data()
        return True, "Referee assigned successfully"

    def add_feedback(self, game_id, referee_name, performance):
        if not (referee_name in self.referee_df['Name'].values and game_id in self.game_df['Game ID'].values):
            return False, "Invalid referee name or game ID."
        new_feedback = pd.DataFrame({'Game ID': [game_id], 'Referee Name': [referee_name], 'Performance': [performance]})
        self.feedback_df = pd.concat([self.feedback_df, new_feedback], ignore_index=True)
        self.save_data()
        return True, "Feedback added successfully."

    def remove_referee(self, name):
        if name in self.referee_df['Name'].values:
            self.referee_df = self.referee_df[self.referee_df['Name'] != name]
            self.save_data()
            return True, "Referee removed successfully."
        return False, "Referee not found."

    def remove_game(self, game_id):
        game_id = str(game_id)
        if game_id in self.game_df['Game ID'].values:
            self.game_df = self.game_df[self.game_df['Game ID'] != game_id]
            self.save_data()
            return True, "Game removed successfully."
        return False, "Game not found."

scheduler = RefereeScheduler()

def main():
    st.title("Referee Scheduling System")
    menu = ["Add Referee", "Add Game", "Assign Referee to Game", "Add Feedback", "Remove Referee", "Remove Game", "Display Referees", "Display Games", "Display Feedback", "Exit"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Add Referee":
        with st.form("Add Referee Form"):
            name = st.text_input("Referee Name")
            expertise = st.text_input("Referee Expertise")
            submitted = st.form_submit_button("Add Referee")
            if submitted:
                scheduler.add_referee(name, expertise)
                st.success("Referee added successfully.")

    elif choice == "Add Game":
        with st.form("Add Game Form"):
            game_id = st.text_input("Game ID")
            game_name = st.text_input("Game Name")
            submitted = st.form_submit_button("Add Game")
            if submitted:
                scheduler.add_game(game_id, game_name)
                st.success("Game added successfully.")

    elif choice == "Assign Referee to Game":
        with st.form("Assign Referee Form"):
            game_id = st.text_input("Game ID")
            referee_name = st.text_input("Referee Name")
            submitted = st.form_submit_button("Assign Referee")
            if submitted:
                success, message = scheduler.assign_referee_to_game(game_id, referee_name)
                if success:
                    st.success(message)
                else:
                    st.error(message)

    elif choice == "Add Feedback":
        with st.form("Add Feedback Form"):
            game_id = st.text_input("Game ID")
            referee_name = st.text_input("Referee Name")
            performance = st.text_area("Performance Feedback")
            submitted = st.form_submit_button("Submit Feedback")
            if submitted:
                success, message = scheduler.add_feedback(game_id, referee_name, performance)
                if success:
                    st.success(message)
                else:
                    st.error(message)

    elif choice == "Remove Referee":
        with st.form("Remove Referee Form"):
            name = st.text_input("Referee Name to Remove")
            submitted = st.form_submit_button("Remove Referee")
            if submitted:
                success, message = scheduler.remove_referee(name)
                if success:
                    st.success(message)
                else:
                    st.error(message)

    elif choice == "Remove Game":
        with st.form("Remove Game Form"):
            game_id = st.text_input("Game ID to Remove")
            submitted = st.form_submit_button("Remove Game")
            if submitted:
                success, message = scheduler.remove_game(game_id)
                if success:
                    st.success(message)
                else:
                    st.error(message)

    elif choice == "Display Referees":
        st.subheader("List of Referees")
        st.dataframe(scheduler.referee_df)

    elif choice == "Display Games":
        st.subheader("List of Games")
        st.dataframe(scheduler.game_df)

    elif choice == "Display Feedback":
        st.subheader("Feedback")
        st.dataframe(scheduler.feedback_df)

    elif choice == "Exit":
        st.stop()

if _name_ == "_main_":
    main()
