from kivy.uix.screenmanager import Screen 
from kivy.lang import Builder 


kv='''
<HomePage>:
    MDNavigationLayout:

        ScreenManager:
            Screen:
                MDBoxLayout:
                    orientation: "vertical"
                    md_bg_color: 120/255, 120/255, 120/255, 1

                    # -------- Top App Bar --------
                    MDTopAppBar:
                        title: "CET/JEE Prep"
                        md_bg_color: 61/255, 61/255, 61/255, 1   # dark topbar
                        title_color: 1, 1, 1, 1   # white text
                        left_action_items: [["menu", lambda x: nav_bar.set_state("toggle")]]


                    # -------- Content Section --------
                    ScrollView:
                        MDBoxLayout:
                            orientation: "vertical"
                            md_bg_color: 120/255, 120/255, 120/255, 1
                            padding: dp(15)
                            adaptive_height: True

                            MDGridLayout:
                                cols: 2
                                spacing: dp(15)
                                adaptive_height: True

                                # -------- imp Card --------
                                MDCard:
                                    size_hint_y: None
                                    height: dp(200)
                                    radius: [20,]
                                    md_bg_color: 61/255, 61/255, 61/255, 1
                                    on_release: app.root.current = "reference"
                                    FitImage:
                                        source: "img/imp.jpg"
                                        radius: [20,]

                                # -------- Books Card --------
                                MDCard:
                                    size_hint_y: None
                                    height: dp(200)
                                    radius: [20,]
                                    md_bg_color: 61/255, 61/255, 61/255, 1
                                    on_release: app.root.current = "book"
                                    FitImage:
                                        source: "img/hsc.jpg"
                                        radius: [20,]

                                # -------- crash course card--------
                                MDCard:
                                    size_hint_y: None
                                    height: dp(200)
                                    radius: [20,]
                                    md_bg_color: 61/255, 61/255, 61/255, 1
                                    on_release: app.root.current = "CC"
                                    FitImage:
                                        source: "img/cc.jpg"
                                        radius: [20,]

                                # -------- mind map Card --------
                                MDCard:
                                    size_hint_y: None
                                    height: dp(200)
                                    radius: [20,]
                                    md_bg_color: 61/255, 61/255, 61/255, 1
                                    on_release: app.root.current = "mindm"
                                    FitImage:
                                        source: "img/mindmap.jpg"
                                        radius: [20,]

                                # -------- handbook Card --------
                                MDCard:
                                    size_hint_y: None
                                    height: dp(200)
                                    radius: [20,]
                                    md_bg_color: 61/255, 61/255, 61/255, 1
                                    on_release: app.root.current = "handbook"
                                    FitImage:
                                        source: "img/book.jpg"
                                        radius: [20,]

                                # -------- PYQs Card --------
                                MDCard:
                                    size_hint_y: None
                                    height: dp(200)
                                    radius: [20,]
                                    md_bg_color: 61/255, 61/255, 61/255, 1
                                    on_release: app.root.current = "pyqs"
                                    FitImage:
                                        source: "img/pyqs.jpg"
                                        radius: [20,]

                    # -------- Bottom Nav Bar --------
                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: dp(55)
                        md_bg_color: 61/255, 61/255, 61/255, 1

                        Widget:
                        MDIconButton:
                            icon: "home"
                            pos_hint: {"center_x": 0.5, "center_y": 0.5}
                            on_release:app.root.current ="home"
                        Widget:
                        MDIconButton:
                            icon: "checkbox-marked-circle-auto-outline"
                            pos_hint: {"center_x": 0.5, "center_y": 0.5}
                            on_release:app.root.current = "test"
                        Widget:
                        MDIconButton:
                            icon: "calendar-blank"
                            pos_hint: {"center_x": 0.5, "center_y": 0.5}
                            on_release:app.root.current="daily"
                        Widget:

        # -------- Navigation Drawer --------
        MDNavigationDrawer:
            id: nav_bar
            md_bg_color: 120/255, 120/255, 120/255, 1
            BoxLayout:
                orientation: "vertical"
                padding: dp(10)
                spacing: dp(10)
                md_bg_color: 120/255, 120/255, 120/255, 1
                
                Image:
                    source:"img/logo.png"
                    size_hint_y:None
                    halign:"left"
                    height:dp(180)
                MDList:
                    TwoLineIconListItem:
                        text:"by : Nivruti Hanumant Dhage"
                        secondary_text:"A small project"

                ScrollView:
                    MDList:
                        OneLineIconListItem:
                            text: "About us"
                            on_press:
                                nav_bar.set_state("close")
                                app.show_contact_dialog("About us", "This app is made for just practice purpose. This app is just a project by a student. There is no bad intention behind this")
                            IconLeftWidget:
                                icon: "home"

                        OneLineIconListItem:
                            text: "content us"
                            on_press:
                                nav_bar.set_state("close")
                                app.show_contact_dialog("Contact us", "Name : Nivruti Hanumant Dhage. No more Contact details")
                            IconLeftWidget:
                                icon: "book"
                                
                        OneLineIconListItem:
                            text: "Analysis"
                            on_press:
                                nav_bar.set_state("close")
                                app.root.current ="analysis"
                            IconLeftWidget:
                                icon: "google-analytics"

                        OneLineIconListItem:
                            text: "Settings"
                            on_press:
                                nav_bar.set_state("close")
                                app.show_contact_dialog("Settings", "There is no setting for now in this app")
                            IconLeftWidget:
                                icon: "book"
'''                                
Builder.load_string(kv)                               
class HomePage(Screen):
    def build(self):
        pass
                         