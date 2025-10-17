import json
import os
import platform
from datetime import datetime, timedelta
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Line, Rectangle
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import ListProperty, StringProperty, ObjectProperty
from kivy.lang import Builder

# KivyMD imports
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.app import MDApp

# KV language string for better layout management
KV = '''
<AnalysisScreen>:
    canvas.before:
        Color:
            rgba: root.MAIN_BG
        Rectangle:
            pos: self.pos
            size: self.size
'''

Builder.load_string(KV)

# --- Graph Widget ---

class GraphWidget(MDFloatLayout):
    data_points = ListProperty([])
    graph_title = StringProperty("")
    theme_color = ListProperty([0.2, 0.6, 0.8, 1])
    x_axis_type = StringProperty("sessions")  # sessions, dates
    y_axis_type = StringProperty("accuracy")  # accuracy, marks, total_marks

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)
        self.bind(pos=self.update_graph, size=self.update_graph)
        self.title_label = MDLabel(
            text=self.graph_title,
            size_hint=(1, None),
            height=dp(30),
            halign="center",
            font_style="Subtitle2"
        )
        self.add_widget(self.title_label)
        self.bind(graph_title=lambda instance, value: setattr(self.title_label, 'text', value))

    def _update_title_pos(self, *args):
        self.title_label.pos = (self.x, self.top - self.title_label.height)

    def update_graph(self, *args):
        self.canvas.after.clear()
        
        app = MDApp.get_running_app()
        text_color = app.theme_cls.text_color
        
        if not self.data_points:
            return

        with self.canvas.after:
            # Draw graph background
            Color(*AnalysisScreen.CARD_BG)
            Rectangle(pos=self.pos, size=self.size)

            # Draw grid lines
            Color(0.5, 0.5, 0.5, 0.3) 
            grid_spacing_x = self.width / 6
            grid_spacing_y = self.height / 6

            for i in range(1, 6):
                Line(points=[self.x + i * grid_spacing_x, self.y,
                           self.x + i * grid_spacing_x, self.y + self.height * 0.9],
                     width=1)
                Line(points=[self.x, self.y + i * grid_spacing_y,
                           self.x + self.width, self.y + i * grid_spacing_y],
                     width=1)

            # Calculate min and max values based on y_axis_type
            if self.y_axis_type == "accuracy":
                values = [point[1] for point in self.data_points]
                min_val = 0
                max_val = 100
            elif self.y_axis_type == "marks":
                values = [point[1] for point in self.data_points]
                min_val = min(values) if values else 0
                max_val = max(values) if values else 100
            else:  # total_marks
                values = [point[1] for point in self.data_points]
                min_val = min(values) if values else 0
                max_val = max(values) if values else 100
                
            value_range = max_val - min_val if max_val != min_val else 100
            
            Color(*self.theme_color) 
            points = []
            data_count = len(self.data_points)
            divisor = data_count - 1 if data_count > 1 else 1
            graph_height_area = self.height * 0.85 
            graph_y_offset = self.height * 0.1

            for i, (label, value) in enumerate(self.data_points):
                if data_count > 1:
                    x = self.x + (i / divisor) * self.width
                else:
                    x = self.x + self.width / 2

                normalized_value = ((value - min_val) / value_range) * graph_height_area
                y = self.y + normalized_value + graph_y_offset
                points.extend([x, y])

                Color(1, 0.5, 0.5, 1)
                Line(circle=(x, y, dp(4)), width=dp(2))
                Color(*self.theme_color) 

                Color(*text_color)
                Line(points=[x, self.y + dp(5), x, self.y + dp(1)], width=dp(1)) 

            if data_count >= 2:
                Line(points=points, width=dp(2))

# --- Analysis Screen Class ---

class AnalysisScreen(Screen):
    selected_time_period = StringProperty("7 days") 
    selected_subject = StringProperty("All Subjects")
    graph_x_axis = StringProperty("sessions")  # sessions, dates
    graph_y_axis = StringProperty("accuracy")  # accuracy, marks, total_marks
    
    # Custom Dark Theme Colors
    MAIN_BG = [0.15, 0.15, 0.2, 1]      # Darkest background
    CARD_BG = [0.2, 0.2, 0.25, 1]       # Card background
    INNER_CARD_BG = [0.25, 0.25, 0.3, 1] # Inner card background

    SUBJECT_COLORS = {
        "Maths": [0.3, 0.7, 1, 1],
        "Physics": [0.9, 0.3, 0.3, 1],
        "Chemistry": [0.2, 0.9, 0.4, 1],
        "Biology": [1, 0.7, 0.3, 1],
        "Unknown Subject": [0.6, 0.6, 0.6, 1],
        "All Subjects": [1, 1, 0.4, 1],
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "analysis"
        self.dialog = None
        self.app = MDApp.get_running_app()
        Clock.schedule_once(self.setup_ui)
        self.bind(
            selected_time_period=self.on_filter_change,
            selected_subject=self.on_filter_change,
            graph_x_axis=self.on_filter_change,
            graph_y_axis=self.on_filter_change
        )

    def on_filter_change(self, *args):
        self.run_analysis(None)

    def setup_ui(self, dt):
        self.clear_widgets()

        # Main layout
        main_layout = MDBoxLayout(orientation="vertical")

        # Top App Bar
        self.top_app_bar = MDTopAppBar(
            title="Performance Analytics",
            elevation=4,
            md_bg_color=self.app.theme_cls.primary_color,
            specific_text_color=[1, 1, 1, 1],
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[["filter-variant", lambda x: self.show_settings()]]
        )
        main_layout.add_widget(self.top_app_bar)

        # Main ScrollView
        main_scroll = MDScrollView()
        
        # Main content layout
        main_content = MDBoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(15),
            size_hint_y=None,
            adaptive_height=True
        )
        
        # Filter Section
        filter_section = self._create_filter_section()
        main_content.add_widget(filter_section)
        
        # Subject Graphs Section
        subject_section = self._create_subject_section()
        main_content.add_widget(subject_section)
        
        # Daily Practice Section
        daily_section = self._create_daily_section()
        main_content.add_widget(daily_section)
        
        # Statistics Section
        stats_section = self._create_stats_section()
        main_content.add_widget(stats_section)
        
        # Insights Section
        insights_section = self._create_insights_section()
        main_content.add_widget(insights_section)

        main_scroll.add_widget(main_content)
        main_layout.add_widget(main_scroll)
        self.add_widget(main_layout)

        Clock.schedule_once(lambda dt: self.run_analysis(None), 0.5)

    def _create_filter_section(self):
        """Create filter display and refresh button section"""
        filter_layout = MDBoxLayout(
            orientation="vertical", 
            spacing=dp(5), 
            size_hint_y=None, 
            height=dp(100),
        )
        
        self.filter_display_label = MDLabel(
            text=f"Period: {self.selected_time_period} | Subject: {self.selected_subject}",
            halign="center",
            theme_text_color="Secondary",
            size_hint_y=None, 
            height=dp(25)
        )
        filter_layout.add_widget(self.filter_display_label)
        
        self.graph_display_label = MDLabel(
            text=f"Graph: X={self.graph_x_axis} | Y={self.graph_y_axis}",
            halign="center",
            theme_text_color="Secondary",
            size_hint_y=None, 
            height=dp(25)
        )
        filter_layout.add_widget(self.graph_display_label)

        analyze_btn = MDRaisedButton(
            text="Refresh Analysis",
            size_hint=(0.8, None),
            height=dp(40),
            pos_hint={"center_x": 0.5},
            on_release=self.run_analysis
        )
        filter_layout.add_widget(analyze_btn)
        return filter_layout

    def _create_subject_section(self):
        """Create subject graphs section"""
        subject_card = MDCard(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(500),
            elevation=2,
            md_bg_color=self.CARD_BG
        )

        subject_card.add_widget(MDLabel(
            text="📚 Subject-wise Performance",
            theme_text_color="Primary",
            font_style="H6",
            size_hint_y=None,
            height=dp(40)
        ))

        self.subject_graphs_container = MDBoxLayout(
            orientation="vertical", 
            spacing=dp(15),
            size_hint_y=None,
            adaptive_height=True
        )
        
        subject_scroll = MDScrollView(size_hint_y=1)
        subject_scroll.add_widget(self.subject_graphs_container)
        subject_card.add_widget(subject_scroll)
        
        return subject_card

    def _create_daily_section(self):
        """Create daily practice section"""
        daily_card = MDCard(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(400),
            elevation=2,
            md_bg_color=self.CARD_BG
        )

        daily_card.add_widget(MDLabel(
            text="📅 Daily Practice Trend",
            theme_text_color="Primary",
            font_style="H6",
            size_hint_y=None,
            height=dp(40)
        ))

        self.daily_graph = GraphWidget(
            size_hint_y=1,
            theme_color=self.SUBJECT_COLORS["Chemistry"]
        )
        daily_card.add_widget(self.daily_graph)
        
        return daily_card

    def _create_stats_section(self):
        """Create statistics section"""
        stats_card = MDCard(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(400),
            elevation=2,
            md_bg_color=self.CARD_BG
        )

        stats_card.add_widget(MDLabel(
            text="📊 Performance Statistics", 
            theme_text_color="Primary", 
            font_style="H6", 
            size_hint_y=None, 
            height=dp(40)
        ))
        
        stats_content = MDBoxLayout(orientation="horizontal", spacing=dp(10))

        # Left stats column
        self.left_stats_card = MDCard(
            orientation="vertical", 
            padding=dp(15), 
            size_hint=(0.5, 1), 
            elevation=1,
            md_bg_color=self.INNER_CARD_BG
        )
        stats_content.add_widget(self.left_stats_card)

        # Right stats column
        self.right_stats_card = MDCard(
            orientation="vertical", 
            padding=dp(15), 
            size_hint=(0.5, 1), 
            elevation=1,
            md_bg_color=self.INNER_CARD_BG
        )
        stats_content.add_widget(self.right_stats_card)

        stats_card.add_widget(stats_content)
        return stats_card

    def _create_insights_section(self):
        """Create insights section"""
        insights_card = MDCard(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(250),
            elevation=2,
            md_bg_color=self.CARD_BG
        )

        insights_card.add_widget(MDLabel(
            text="💡 Insights & Recommendations", 
            theme_text_color="Primary", 
            font_style="H6", 
            size_hint_y=None, 
            height=dp(40)
        ))

        self.insights_label = MDLabel(
            text="Run analysis to get personalized insights...",
            theme_text_color="Secondary",
            size_hint_y=1
        )
        insights_card.add_widget(self.insights_label)
        return insights_card

    def show_settings(self, instance=None):
        content = MDBoxLayout(
            orientation="vertical", 
            spacing=dp(15), 
            padding=dp(10), 
            size_hint_y=None, 
            height=dp(500)
        )
        
        # Subject Filter Section
        subject_label = MDLabel(text="Select Subject Filter:", font_style="Subtitle1", theme_text_color="Primary")
        content.add_widget(subject_label)

        subject_layout = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(40))
        subjects = ["All Subjects", "Maths", "Physics", "Chemistry", "Biology"]
        for subject in subjects:
            btn = MDFlatButton(
                text=subject.split()[0],
                size_hint=(None, None),
                size=(dp(70), dp(30)),
                md_bg_color=self.app.theme_cls.primary_color if self.selected_subject == subject else self.INNER_CARD_BG,
                text_color=[1, 1, 1, 1]
            )
            btn.bind(on_release=lambda x, p=subject: self.set_subject_period(p))
            subject_layout.add_widget(btn)
        content.add_widget(subject_layout)
        
        # Time Period Filter Section
        time_label = MDLabel(text="Select Time Period Filter:", font_style="Subtitle1", theme_text_color="Primary")
        content.add_widget(time_label)

        time_layout = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(40))
        periods = ["7 days", "30 days", "All time"]
        for period in periods:
            btn = MDFlatButton(
                text=period,
                size_hint=(None, None),
                size=(dp(80), dp(30)),
                md_bg_color=self.app.theme_cls.primary_color if self.selected_time_period == period else self.INNER_CARD_BG,
                text_color=[1, 1, 1, 1]
            )
            btn.bind(on_release=lambda x, p=period: self.set_time_period(p))
            time_layout.add_widget(btn)
        content.add_widget(time_layout)
        
        # Graph X-Axis Options
        x_axis_label = MDLabel(text="Select X-Axis:", font_style="Subtitle1", theme_text_color="Primary")
        content.add_widget(x_axis_label)

        x_axis_layout = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(40))
        x_options = ["sessions", "dates"]
        for option in x_options:
            btn = MDFlatButton(
                text=option,
                size_hint=(None, None),
                size=(dp(80), dp(30)),
                md_bg_color=self.app.theme_cls.primary_color if self.graph_x_axis == option else self.INNER_CARD_BG,
                text_color=[1, 1, 1, 1]
            )
            btn.bind(on_release=lambda x, p=option: self.set_x_axis(p))
            x_axis_layout.add_widget(btn)
        content.add_widget(x_axis_layout)
        
        # Graph Y-Axis Options
        y_axis_label = MDLabel(text="Select Y-Axis:", font_style="Subtitle1", theme_text_color="Primary")
        content.add_widget(y_axis_label)

        y_axis_layout = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(40))
        y_options = ["accuracy", "marks", "total_marks"]
        for option in y_options:
            btn = MDFlatButton(
                text=option.replace("_", " "),
                size_hint=(None, None),
                size=(dp(90), dp(30)),
                md_bg_color=self.app.theme_cls.primary_color if self.graph_y_axis == option else self.INNER_CARD_BG,
                text_color=[1, 1, 1, 1]
            )
            btn.bind(on_release=lambda x, p=option: self.set_y_axis(p))
            y_axis_layout.add_widget(btn)
        content.add_widget(y_axis_layout)

        close_btn = MDRaisedButton(
            text="Close & Apply Filters",
            pos_hint={"center_x": 0.5},
            on_release=lambda x: self.dialog.dismiss()
        )
        content.add_widget(close_btn)

        self.dialog = MDDialog(
            title="Analysis Filters",
            type="custom",
            content_cls=content,
            md_bg_color=self.CARD_BG,
            buttons=[],
        )
        self.dialog.open()

    def set_subject_period(self, subject):
        self.selected_subject = subject
        self.filter_display_label.text = f"Period: {self.selected_time_period} | Subject: {self.selected_subject}"

    def set_time_period(self, period):
        self.selected_time_period = period
        self.filter_display_label.text = f"Period: {self.selected_time_period} | Subject: {self.selected_subject}"

    def set_x_axis(self, x_axis):
        self.graph_x_axis = x_axis
        self.graph_display_label.text = f"Graph: X={self.graph_x_axis} | Y={self.graph_y_axis}"

    def set_y_axis(self, y_axis):
        self.graph_y_axis = y_axis
        self.graph_display_label.text = f"Graph: X={self.graph_x_axis} | Y={self.graph_y_axis}"

    def go_back(self, instance=None):
        self.manager.current = "home"

    def get_storage_path(self):
        try:
            from kivy import platform as kivy_platform
            if kivy_platform == 'android':
                from android.storage import primary_external_storage_path
                base_path = primary_external_storage_path()
                storage_dir = os.path.join(base_path, 'Documents', 'cetapp')
                os.makedirs(storage_dir, exist_ok=True)
                return storage_dir
            else:
                storage_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'cetapp')
                os.makedirs(storage_dir, exist_ok=True)
                return storage_dir
        except Exception as e:
            storage_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'cetapp')
            os.makedirs(storage_dir, exist_ok=True)
            return storage_dir

    def run_analysis(self, instance):
        try:
            storage_dir = self.get_storage_path()
            file_path = os.path.join(storage_dir, 'user_performance.json')

            if not os.path.exists(file_path):
                self.show_no_data_message()
                return

            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            filtered_data = self._apply_time_filter(data)
            
            self.filter_display_label.text = f"Period: {self.selected_time_period} | Subject: {self.selected_subject}"
            self.graph_display_label.text = f"Graph: X={self.graph_x_axis} | Y={self.graph_y_axis}"

            self.update_subject_graphs(filtered_data)
            self.update_daily_graph(filtered_data)
            self.update_statistics(filtered_data)
            self.update_insights(filtered_data)

        except Exception as e:
            self.show_error_message(str(e))

    def _apply_time_filter(self, data):
        period = self.selected_time_period
        now = datetime.now()
        filtered_data = {'practice': [], 'daily_practice': data.get('daily_practice', [])}
        practice_data = data.get('practice', [])
        
        if period == "All time":
            filtered_data['practice'] = practice_data
            return filtered_data

        if period == "7 days":
            delta = timedelta(days=7)
        elif period == "30 days":
            delta = timedelta(days=30)
        else:
            filtered_data['practice'] = practice_data
            return filtered_data

        min_date = now - delta

        for session in practice_data:
            session_date_str = session.get('date')
            try:
                session_dt = datetime.strptime(session_date_str, '%Y-%m-%d')
                if session_dt >= min_date:
                    filtered_data['practice'].append(session)
            except (ValueError, TypeError):
                pass 

        filtered_daily = []
        for session in data.get('daily_practice', []):
            session_date_str = session.get('date')
            try:
                session_dt = datetime.strptime(session_date_str, '%Y-%m-%d')
                if session_dt >= min_date:
                    filtered_daily.append(session)
            except (ValueError, TypeError):
                pass
        filtered_data['daily_practice'] = filtered_daily
        
        return filtered_data

    def update_subject_graphs(self, data):
        practice_data = data.get('practice', [])
        self.subject_graphs_container.clear_widgets()

        subject_sessions = {}
        for session in practice_data:
            subject = session.get('subject', 'Unknown Subject')
            if subject not in subject_sessions:
                subject_sessions[subject] = []
            subject_sessions[subject].append(session)

        # Fix: Show all subjects when "All Subjects" is selected
        if self.selected_subject == "All Subjects":
            subjects_to_plot = list(subject_sessions.keys())
        else:
            subjects_to_plot = [self.selected_subject]
            
        if not subjects_to_plot:
            no_data_label = MDLabel(
                text=f"No data for selected filters.", 
                halign='center', 
                theme_text_color="Secondary",
                size_hint_y=None, 
                height=dp(300)
            )
            self.subject_graphs_container.add_widget(no_data_label)
            return
        
        for subject in subjects_to_plot:
            sessions = subject_sessions.get(subject, [])
            if not sessions:
                no_data_label = MDLabel(
                    text=f"No data for {subject} in the selected period.", 
                    halign='center', 
                    theme_text_color="Secondary",
                    size_hint_y=None, 
                    height=dp(300)
                )
                self.subject_graphs_container.add_widget(no_data_label)
                continue
                
            sessions_to_plot = sessions[-10:]  # Show last 10 sessions
            graph_data = []

            for i, session in enumerate(sessions_to_plot):
                # Calculate value based on y_axis_type
                if self.graph_y_axis == "accuracy":
                    correct = session.get('correct_questions', 0)
                    total = session.get('total_questions', 0)
                    value = (correct / total) * 100 if total > 0 else 0
                elif self.graph_y_axis == "marks":
                    value = session.get('correct_questions', 0)
                else:  # total_marks
                    value = session.get('total_questions', 0)
                
                # Set label based on x_axis_type
                if self.graph_x_axis == "sessions":
                    session_index = len(sessions) - len(sessions_to_plot) + i + 1
                    label = f"S{session_index}"
                else:  # dates
                    date_str = session.get('date', '')
                    label = date_str.split('-')[-1] if '-' in date_str else date_str
                    
                graph_data.append((label, value))

            color = self.SUBJECT_COLORS.get(subject, self.SUBJECT_COLORS["Unknown Subject"])

            subject_label = MDLabel(
                text=f"Subject: {subject}",
                theme_text_color="Primary",
                font_style="Subtitle1",
                size_hint_y=None, 
                height=dp(30),
                padding=[dp(10), 0]
            )
            self.subject_graphs_container.add_widget(subject_label)

            graph_card = MDCard(
                size_hint_y=None, 
                height=dp(300), 
                padding=dp(10),
                elevation=1,
                md_bg_color=self.INNER_CARD_BG
            )
            
            subject_graph_widget = GraphWidget(
                size_hint_y=1,
                theme_color=color,
                x_axis_type=self.graph_x_axis,
                y_axis_type=self.graph_y_axis
            )
            subject_graph_widget.data_points = graph_data
            
            # Set appropriate graph title based on axis types
            y_title = self.graph_y_axis.replace("_", " ").title()
            subject_graph_widget.graph_title = f"{y_title} Trend ({len(sessions_to_plot)} Sessions)"
            
            graph_card.add_widget(subject_graph_widget)
            self.subject_graphs_container.add_widget(graph_card)

    def update_daily_graph(self, data):
        daily_data = data.get('daily_practice', [])
        valid_daily = [session for session in daily_data if session.get('total_questions', 0) > 0]

        if not valid_daily:
            self.daily_graph.data_points = []
            self.daily_graph.graph_title = "No Daily Practice Data"
            self.daily_graph.update_graph()
            return

        daily_stats = {}
        for session in valid_daily:
            date = session.get('date', '')
            correct = session.get('correct_questions', 0)
            total = session.get('total_questions', 0)

            if date not in daily_stats:
                daily_stats[date] = {'correct': 0, 'total': 0}

            daily_stats[date]['correct'] += correct
            daily_stats[date]['total'] += total

        sorted_dates = sorted(daily_stats.keys())
        last_7_dates = sorted_dates[-7:]

        graph_data = []
        for date in last_7_dates:
            stats = daily_stats[date]
            
            # Calculate value based on y_axis_type
            if self.graph_y_axis == "accuracy":
                value = (stats['correct'] / stats['total']) * 100 if stats['total'] > 0 else 0
            elif self.graph_y_axis == "marks":
                value = stats['correct']
            else:  # total_marks
                value = stats['total']
                
            short_date = date.split('-')[-1] if '-' in date else date
            graph_data.append((short_date, value))

        self.daily_graph.data_points = graph_data
        self.daily_graph.x_axis_type = "dates"
        self.daily_graph.y_axis_type = self.graph_y_axis
        
        y_title = self.graph_y_axis.replace("_", " ").title()
        self.daily_graph.graph_title = f"Daily {y_title} Trend (Last 7 Days)"
        self.daily_graph.update_graph()

    def update_statistics(self, data):
        practice_data = data.get('practice', [])
        daily_data = data.get('daily_practice', [])
        valid_daily = [session for session in daily_data if session.get('total_questions', 0) > 0]

        self.left_stats_card.clear_widgets()
        self.right_stats_card.clear_widgets()

        left_title = MDLabel(
            text="📚 Practice Stats", 
            theme_text_color="Primary", 
            font_style="H6", 
            size_hint_y=None, 
            height=dp(30)
        )
        self.left_stats_card.add_widget(left_title)

        if practice_data:
            filtered_practice = practice_data
            if self.selected_subject != "All Subjects":
                filtered_practice = [s for s in practice_data if s.get('subject') == self.selected_subject]

            total_sessions = len(filtered_practice)
            total_questions = sum(s.get('total_questions', 0) for s in filtered_practice)
            total_correct = sum(s.get('correct_questions', 0) for s in filtered_practice)
            avg_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0

            stats_text = f"""Sessions: {total_sessions}
Questions: {total_questions}
Correct: {total_correct}
Accuracy: {avg_accuracy:.1f}%

Best Session: {self.get_best_session(filtered_practice)}
Weakest Area: {self.get_weakest_subject(filtered_practice)}"""

        else:
            stats_text = "No practice data available"

        left_stats = MDLabel(text=stats_text, theme_text_color="Secondary", size_hint_y=1)
        self.left_stats_card.add_widget(left_stats)

        right_title = MDLabel(
            text="📅 Daily Stats", 
            theme_text_color="Primary", 
            font_style="H6", 
            size_hint_y=None, 
            height=dp(30)
        )
        self.right_stats_card.add_widget(right_title)

        if valid_daily:
            total_daily_sessions = len(valid_daily)
            total_daily_questions = sum(s.get('total_questions', 0) for s in valid_daily)
            total_daily_correct = sum(s.get('correct_questions', 0) for s in valid_daily)
            daily_accuracy = (total_daily_correct / total_daily_questions * 100) if total_daily_questions > 0 else 0

            daily_text = f"""Sessions: {total_daily_sessions}
Questions: {total_daily_questions}
Correct: {total_daily_correct}
Accuracy: {daily_accuracy:.1f}%

Activity: {len(valid_daily)} days in period"""

        else:
            daily_text = "No daily practice data"

        right_stats = MDLabel(text=daily_text, theme_text_color="Secondary", size_hint_y=1)
        self.right_stats_card.add_widget(right_stats)

    def update_insights(self, data):
        insights = self.generate_insights(data)
        insights_text = "\n".join([f"• {insight}" for insight in insights])
        self.insights_label.text = insights_text

    def get_best_session(self, practice_data):
        if not practice_data: 
            return "N/A"
        best_session = max(practice_data, key=lambda x: (x.get('correct_questions', 0) / x.get('total_questions', 1)) if x.get('total_questions', 0) > 0 else 0)
        accuracy = (best_session.get('correct_questions', 0) / best_session.get('total_questions', 1)) * 100
        return f"{accuracy:.1f}%"

    def get_weakest_subject(self, practice_data):
        if not practice_data: 
            return "N/A"
        subject_stats = {}
        for session in practice_data:
            subject = session.get('subject', 'Unknown')
            if subject not in subject_stats:
                subject_stats[subject] = {'correct': 0, 'total': 0}
            subject_stats[subject]['correct'] += session.get('correct_questions', 0)
            subject_stats[subject]['total'] += session.get('total_questions', 0)
        
        valid_subjects = {k: v for k, v in subject_stats.items() if v['total'] > 0}
        if not valid_subjects: 
            return "N/A"
        
        weakest_subject = min(valid_subjects.items(), key=lambda x: (x[1]['correct'] / x[1]['total']) if x[1]['total'] > 0 else 0)
        return f"{weakest_subject[0]}"

    def generate_insights(self, data):
        insights = []
        practice_data = data.get('practice', [])
        daily_data = data.get('daily_practice', [])

        if not practice_data and not daily_data:
            return ["Start practicing to get personalized insights!"]

        insights.append("Continue regular practice for better results")
        insights.append("Focus on your weakest subjects")
        insights.append("Try to maintain daily practice consistency")
        
        return insights

    def show_no_data_message(self):
        self.subject_graphs_container.clear_widgets()
        self.daily_graph.data_points = []
        self.daily_graph.graph_title = "No Data Available"
        self.daily_graph.update_graph()

        self.subject_graphs_container.add_widget(MDLabel(
            text="No practice data found in selected period/subject.", 
            halign="center", 
            theme_text_color="Secondary", 
            size_hint_y=None, 
            height=dp(300)
        ))
        
        self.left_stats_card.clear_widgets()
        self.right_stats_card.clear_widgets()
        self.insights_label.text = "• Complete some practice sessions to see insights\n• Try both practice and daily practice modes\n• Check if the selected time period or subject has data"

    def show_error_message(self, error):
        self.subject_graphs_container.clear_widgets()
        self.daily_graph.data_points = []
        self.daily_graph.graph_title = "Error Loading Data"
        self.daily_graph.update_graph()

        self.subject_graphs_container.add_widget(MDLabel(
            text="Error loading data", 
            halign="center", 
            theme_text_color="Error", 
            size_hint_y=None, 
            height=dp(300)
        ))
        self.insights_label.text = f"Error: {error}\n\nPlease check if the data file exists and is valid."