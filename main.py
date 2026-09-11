import customtkinter as ctk
import subprocess
import threading
import socket
import random
import re
import os
import sys
import queue


# ============================================================
# SETTINGS
# ============================================================

ctk.set_appearance_mode("dark")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BG = "#070B14"
PANEL = "#0D1422"
CARD = "#111A2C"
CARD_2 = "#172238"
BORDER = "#26344D"

WHITE = "#F8FAFC"
MUTED = "#94A3B8"

PURPLE = "#7C3AED"
PURPLE_HOVER = "#8B5CF6"

BLUE = "#2563EB"
BLUE_HOVER = "#3B82F6"

CYAN = "#0891B2"
CYAN_HOVER = "#06B6D4"

GREEN = "#16A34A"
GREEN_HOVER = "#22C55E"

RED = "#DC2626"
YELLOW = "#EAB308"


# ============================================================
# MAIN WINDOW
# ============================================================

class NumberGame(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("Number Guessing Game")
        self.geometry("1200x760")
        self.resizable(False, False)
        self.configure(fg_color=BG)

        # Original game process
        self.process = None
        self.reader_thread = None
        self.output_queue = queue.Queue()

        # Current mode
        self.current_file = None
        self.current_mode = None

        # GUI state
        self.round_number = 0
        self.current_turn = ""

        # Online
        self.online_socket = None
        self.online_server = None
        self.online_role = None
        self.online_connected = False
        self.online_player_number = None
        self.online_secret = None
        self.online_opponent_secret = None
        self.online_possible_numbers = []

        # Online turn state
        self.online_my_turn = False
        self.online_guess_ready = False
        self.online_last_guess = ""

        self.protocol(
            "WM_DELETE_WINDOW",
            self.close_app
        )

        self.show_home()


    # ========================================================
    # GENERAL
    # ========================================================

    def clear(self):

        for widget in self.winfo_children():
            widget.destroy()


    def stop_original_process(self):

        if self.process:

            try:
                if self.process.stdin:
                    self.process.stdin.close()
            except Exception:
                pass

            try:
                if self.process.poll() is None:
                    self.process.terminate()
            except Exception:
                pass

            self.process = None


    def close_online(self):

        try:
            if self.online_socket:
                self.online_socket.close()
        except Exception:
            pass

        try:
            if self.online_server:
                self.online_server.close()
        except Exception:
            pass

        self.online_socket = None
        self.online_server = None
        self.online_connected = False


    def stop_everything(self):

        self.stop_original_process()
        self.close_online()


    def close_app(self):

        self.stop_everything()
        self.destroy()


    # ========================================================
    # BUTTON
    # ========================================================

    def make_button(
        self,
        parent,
        text,
        command,
        color=PURPLE,
        hover=PURPLE_HOVER,
        width=180,
        height=48
    ):

        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            corner_radius=14,
            fg_color=color,
            hover_color=hover,
            font=("Segoe UI", 14, "bold"),
            text_color=WHITE,
            cursor="hand2"
        )


    # ========================================================
    # HOME
    # ========================================================

    def show_home(self):

        self.stop_everything()
        self.clear()

        # ---------------- HEADER ----------------

        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            padx=50,
            pady=(30, 0)
        )

        title_frame = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )

        title_frame.pack(
            side="left"
        )

        ctk.CTkLabel(
            title_frame,
            text="NUMBER",
            font=("Segoe UI", 48, "bold"),
            text_color=WHITE
        ).pack(
            anchor="w"
        )

        ctk.CTkLabel(
            title_frame,
            text="GUESSING GAME",
            font=("Segoe UI", 31, "bold"),
            text_color=PURPLE_HOVER
        ).pack(
            anchor="w"
        )

        ctk.CTkLabel(
            title_frame,
            text="Choose your game mode",
            font=("Segoe UI", 15),
            text_color=MUTED
        ).pack(
            anchor="w",
            pady=(5, 0)
        )

        ctk.CTkLabel(
            header,
            text="4 MODES",
            font=("Segoe UI", 13, "bold"),
            text_color="#475569"
        ).pack(
            side="right",
            pady=20
        )

        # ---------------- CARDS ----------------

        cards = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        cards.pack(
            fill="both",
            expand=True,
            padx=45,
            pady=30
        )

        cards.grid_columnconfigure(0, weight=1)
        cards.grid_columnconfigure(1, weight=1)
        cards.grid_rowconfigure(0, weight=1)
        cards.grid_rowconfigure(1, weight=1)

        self.create_mode_card(
            cards,
            0,
            0,
            "01",
            "PLAYER",
            "Classic single player",
            "Play the original Mode 1.",
            PURPLE,
            PURPLE_HOVER,
            "mood-1.py"
        )

        self.create_mode_card(
            cards,
            0,
            1,
            "02",
            "TWO PLAYERS",
            "Local multiplayer",
            "Two players take turns.",
            BLUE,
            BLUE_HOVER,
            "mood-2.py"
        )

        self.create_mode_card(
            cards,
            1,
            0,
            "03",
            "ONLINE",
            "Network multiplayer",
            "Create or join a room.",
            CYAN,
            CYAN_HOVER,
            "mood-3.py"
        )

        self.create_mode_card(
            cards,
            1,
            1,
            "04",
            "PLAYER VS PC",
            "Challenge computer",
            "Play against the original Mode 4.",
            GREEN,
            GREEN_HOVER,
            "mood-4.py"
        )

        ctk.CTkLabel(
            self,
            text="ORIGINAL GAME CODE • GUI ONLY",
            font=("Segoe UI", 11),
            text_color="#475569"
        ).pack(
            pady=(0, 12)
        )


    # ========================================================
    # MODE CARD
    # ========================================================

    def create_mode_card(
        self,
        parent,
        row,
        column,
        number,
        title,
        subtitle,
        description,
        color,
        hover,
        filename
    ):

        card = ctk.CTkFrame(
            parent,
            fg_color=CARD,
            corner_radius=24,
            border_width=1,
            border_color=BORDER
        )

        card.grid(
            row=row,
            column=column,
            padx=10,
            pady=10,
            sticky="nsew"
        )

        ctk.CTkLabel(
            card,
            text=number,
            font=("Segoe UI", 14, "bold"),
            text_color=color
        ).pack(
            anchor="w",
            padx=25,
            pady=(18, 3)
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI", 25, "bold"),
            text_color=WHITE
        ).pack(
            anchor="w",
            padx=25
        )

        ctk.CTkLabel(
            card,
            text=subtitle,
            font=("Segoe UI", 14, "bold"),
            text_color=color
        ).pack(
            anchor="w",
            padx=25,
            pady=(5, 2)
        )

        ctk.CTkLabel(
            card,
            text=description,
            font=("Segoe UI", 13),
            text_color=MUTED
        ).pack(
            anchor="w",
            padx=25
        )

        self.make_button(
            card,
            "START  →",
            lambda f=filename, n=number:
            self.start_mode(f, n),
            color,
            hover,
            175,
            45
        ).pack(
            anchor="w",
            padx=25,
            pady=18
        )


    # ========================================================
    # START MODE
    # ========================================================

    def start_mode(
        self,
        filename,
        mode
    ):

        self.stop_everything()

        self.current_file = filename
        self.current_mode = mode
        self.round_number = 0
        self.current_turn = ""

        if filename == "mood-3.py":

            self.show_online_setup()

        else:

            self.show_original_game()


    # ========================================================
    # ORIGINAL GAME SCREEN
    # ========================================================

    def show_original_game(self):

        self.clear()

        # HEADER

        header = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            height=82
        )

        header.pack(
            fill="x"
        )

        header.pack_propagate(False)

        title_frame = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )

        title_frame.pack(
            side="left",
            padx=30
        )

        ctk.CTkLabel(
            title_frame,
            text=f"MODE {self.current_mode}",
            font=("Segoe UI", 11, "bold"),
            text_color=PURPLE_HOVER
        ).pack(
            anchor="w"
        )

        title = {
            "mood-1.py": "PLAYER",
            "mood-2.py": "TWO PLAYERS",
            "mood-4.py": "PLAYER VS PC"
        }[self.current_file]

        ctk.CTkLabel(
            title_frame,
            text=title,
            font=("Segoe UI", 25, "bold"),
            text_color=WHITE
        ).pack(
            anchor="w"
        )

        self.make_button(
            header,
            "← MENU",
            self.show_home,
            "#1E293B",
            "#334155",
            120,
            42
        ).pack(
            side="right",
            padx=28
        )

        # BODY

        body = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        body.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=25
        )

        # LEFT

        left = ctk.CTkFrame(
            body,
            fg_color=PANEL,
            corner_radius=24,
            border_width=1,
            border_color=BORDER
        )

        left.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 12)
        )

        ctk.CTkLabel(
            left,
            text="GAME BOARD",
            font=("Segoe UI", 13, "bold"),
            text_color=MUTED
        ).pack(
            anchor="w",
            padx=25,
            pady=(20, 5)
        )

        self.status_label = ctk.CTkLabel(
            left,
            text="STARTING GAME...",
            font=("Segoe UI", 26, "bold"),
            text_color=WHITE
        )

        self.status_label.pack(
            anchor="w",
            padx=25,
            pady=(0, 12)
        )

        display = ctk.CTkFrame(
            left,
            fg_color=CARD,
            corner_radius=18
        )

        display.pack(
            fill="x",
            padx=25,
            pady=8
        )

        ctk.CTkLabel(
            display,
            text="YOUR GUESS",
            font=("Segoe UI", 10, "bold"),
            text_color=MUTED
        ).pack(
            pady=(12, 2)
        )

        self.guess_display = ctk.CTkLabel(
            display,
            text="—  —  —  —",
            font=("Consolas", 34, "bold"),
            text_color=WHITE
        )

        self.guess_display.pack(
            pady=(0, 12)
        )

        # INPUT

        input_frame = ctk.CTkFrame(
            left,
            fg_color="transparent"
        )

        input_frame.pack(
            fill="x",
            padx=25,
            pady=12
        )

        self.guess_entry = ctk.CTkEntry(
            input_frame,
            height=55,
            corner_radius=15,
            placeholder_text="Enter 4 different digits",
            font=("Segoe UI", 18),
            justify="center"
        )

        self.guess_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 10)
        )

        self.guess_button = self.make_button(
            input_frame,
            "GUESS  →",
            self.submit_original_guess,
            PURPLE,
            PURPLE_HOVER,
            145,
            55
        )

        self.guess_button.pack(
            side="right"
        )

        self.guess_entry.bind(
            "<KeyRelease>",
            self.update_guess_display
        )

        self.guess_entry.bind(
            "<Return>",
            lambda e: self.submit_original_guess()
        )

        # HISTORY

        ctk.CTkLabel(
            left,
            text="GAME HISTORY",
            font=("Segoe UI", 11, "bold"),
            text_color=MUTED
        ).pack(
            anchor="w",
            padx=25,
            pady=(5, 3)
        )

        self.history = ctk.CTkScrollableFrame(
            left,
            fg_color=CARD,
            corner_radius=15,
            height=150
        )

        self.history.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(0, 20)
        )

        # RIGHT

        right = ctk.CTkFrame(
            body,
            width=275,
            fg_color=PANEL,
            corner_radius=24,
            border_width=1,
            border_color=BORDER
        )

        right.pack(
            side="right",
            fill="y"
        )

        right.pack_propagate(False)

        ctk.CTkLabel(
            right,
            text="LIVE INFO",
            font=("Segoe UI", 18, "bold"),
            text_color=WHITE
        ).pack(
            pady=(25, 18)
        )

        self.round_info = self.info_box(
            right,
            "ROUND",
            "—"
        )

        self.stars_info = self.info_box(
            right,
            "STARS",
            "—"
        )

        self.points_info = self.info_box(
            right,
            "POINTS",
            "—"
        )

        if self.current_file == "mood-4.py":

            self.pc_info = self.info_box(
                right,
                "PC OPTIONS",
                "—"
            )

        else:

            self.pc_info = None

        self.secret_info = self.info_box(
            right,
            "SECRET",
            "HIDDEN"
        )

        self.start_original_file()


    # ========================================================
    # INFO BOX
    # ========================================================

    def info_box(
        self,
        parent,
        title,
        value
    ):

        box = ctk.CTkFrame(
            parent,
            fg_color=CARD,
            corner_radius=15
        )

        box.pack(
            fill="x",
            padx=18,
            pady=6
        )

        ctk.CTkLabel(
            box,
            text=title,
            font=("Segoe UI", 10, "bold"),
            text_color=MUTED
        ).pack(
            pady=(8, 0)
        )

        label = ctk.CTkLabel(
            box,
            text=value,
            font=("Segoe UI", 22, "bold"),
            text_color=WHITE
        )

        label.pack(
            pady=(1, 8)
        )

        return label


    # ========================================================
    # RUN ORIGINAL FILE
    # ========================================================

    def start_original_file(self):

        filepath = os.path.join(
            BASE_DIR,
            self.current_file
        )

        if not os.path.exists(filepath):

            self.status_label.configure(
                text="FILE NOT FOUND",
                text_color=RED
            )

            self.guess_button.configure(
                state="disabled"
            )

            return

        try:

            self.process = subprocess.Popen(
                [
                    sys.executable,
                    "-u",
                    filepath
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=BASE_DIR
            )

            self.reader_thread = threading.Thread(
                target=self.read_original_output,
                daemon=True
            )

            self.reader_thread.start()

            self.after(
                50,
                self.check_original_output
            )

        except Exception as error:

            self.status_label.configure(
                text="ERROR",
                text_color=RED
            )

            self.add_history(
                "ERROR",
                str(error),
                RED
            )


    # ========================================================
    # READ ORIGINAL OUTPUT
    # ========================================================

    def read_original_output(self):

        try:

            while self.process and self.process.stdout:

                char = self.process.stdout.read(1)

                if char == "":
                    break

                self.output_queue.put(char)

        except:

            pass


    def check_original_output(self):

        text = ""

        try:

            while True:

                text += self.output_queue.get_nowait()

        except queue.Empty:

            pass

        if text:

            self.parse_original_output(text)

        if self.process and self.process.poll() is None:

            self.after(
                60,
                self.check_original_output
            )


    # ========================================================
    # PARSE ORIGINAL OUTPUT
    # ========================================================

    def parse_original_output(
        self,
        text
    ):

        lower = text.lower()

        # SECRET

        match = re.search(
            r"player your number is\s*:\s*(\d{4})",
            text,
            re.IGNORECASE
        )

        if match:

            self.secret_info.configure(
                text=match.group(1)
            )

        match = re.search(
            r"player 1 your number is\s*:\s*(\d{4})",
            text,
            re.IGNORECASE
        )

        if match:

            self.secret_info.configure(
                text=match.group(1)
            )

        # RESULT

        match = re.search(
            r"result is\s*(\d+)\s*stars and\s*(\d+)\s*points",
            text,
            re.IGNORECASE
        )

        if match:

            stars = match.group(1)
            points = match.group(2)

            self.stars_info.configure(
                text=stars
            )

            self.points_info.configure(
                text=points
            )

            player = self.current_turn

            if not player:

                player = "PLAYER"

            self.add_history(
                player,
                f"{stars} ★     {points} ●",
                PURPLE_HOVER
            )

        # PC POSSIBLE NUMBERS

        match = re.search(
            r"computer possible numbers\s*:\s*(\d+)",
            text,
            re.IGNORECASE
        )

        if match and self.pc_info:

            self.pc_info.configure(
                text=match.group(1)
            )

        # MODE 2

        if (
            "player 1 your ruond" in lower
            or
            "player 1 your round" in lower
        ):

            self.current_turn = "PLAYER 1"

            self.status_label.configure(
                text="PLAYER 1 TURN",
                text_color=BLUE_HOVER
            )

            self.enable_original_input()

        elif (
            "player 2 your ruond" in lower
            or
            "player 2 your round" in lower
        ):

            self.current_turn = "PLAYER 2"

            self.status_label.configure(
                text="PLAYER 2 TURN",
                text_color=CYAN_HOVER
            )

            self.enable_original_input()

        # MODE 4

        elif (
            "your round" in lower
            and
            self.current_file == "mood-4.py"
        ):

            self.current_turn = "PLAYER"

            self.status_label.configure(
                text="YOUR TURN",
                text_color=GREEN_HOVER
            )

            self.enable_original_input()

        elif "computer round" in lower:

            self.current_turn = "COMPUTER"

            self.status_label.configure(
                text="COMPUTER THINKING...",
                text_color=PURPLE_HOVER
            )

            self.disable_original_input()

        # WIN

        if (
            "congratulations" in lower
            or
            "win the game" in lower
        ):

            self.status_label.configure(
                text="🏆 YOU WIN!",
                text_color=GREEN_HOVER
            )

            self.disable_original_input()

        # COMPUTER WIN

        if "computer win" in lower:

            self.status_label.configure(
                text="🤖 COMPUTER WINS",
                text_color=RED
            )

            self.disable_original_input()

        # LOSE

        if "you lose" in lower:

            self.status_label.configure(
                text="YOU LOSE",
                text_color=RED
            )

            self.disable_original_input()


    # ========================================================
    # ORIGINAL INPUT
    # ========================================================

    def enable_original_input(self):

        self.guess_entry.configure(
            state="normal"
        )

        self.guess_button.configure(
            state="normal"
        )

        self.guess_entry.focus()


    def disable_original_input(self):

        self.guess_entry.configure(
            state="disabled"
        )

        self.guess_button.configure(
            state="disabled"
        )


    def update_guess_display(
        self,
        event=None
    ):

        value = self.guess_entry.get()

        value = "".join(
            x for x in value
            if x.isdigit()
        )[:4]

        if value != self.guess_entry.get():

            self.guess_entry.delete(
                0,
                "end"
            )

            self.guess_entry.insert(
                0,
                value
            )

        if value:

            display = "  ".join(value)

            missing = 4 - len(value)

            if missing:

                display += "  " + "  ".join(
                    ["—"] * missing
                )

        else:

            display = "—  —  —  —"

        self.guess_display.configure(
            text=display
        )


    def submit_original_guess(self):

        if not self.process:
            return

        if self.process.poll() is not None:
            return

        value = self.guess_entry.get().strip()

        if not re.fullmatch(
            r"\d{4}",
            value
        ):

            self.status_label.configure(
                text="ENTER 4 DIGITS",
                text_color=YELLOW
            )

            return

        try:

            self.process.stdin.write(
                value + "\n"
            )

            self.process.stdin.flush()

        except:

            return

        self.round_number += 1

        self.round_info.configure(
            text=str(self.round_number)
        )

        self.guess_entry.delete(
            0,
            "end"
        )

        self.guess_display.configure(
            text="—  —  —  —"
        )

        self.guess_button.configure(
            state="disabled"
        )


    # ========================================================
    # ONLINE SETUP
    # ========================================================

    def show_online_setup(self):

        self.online_my_turn = False
        self.online_guess_ready = False
        self.online_last_guess = ""

        self.clear()

        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            padx=45,
            pady=(30, 0)
        )

        ctk.CTkLabel(
            header,
            text="MODE 03",
            font=("Segoe UI", 12, "bold"),
            text_color=CYAN_HOVER
        ).pack(
            anchor="w"
        )

        ctk.CTkLabel(
            header,
            text="ONLINE MULTIPLAYER",
            font=("Segoe UI", 34, "bold"),
            text_color=WHITE
        ).pack(
            anchor="w"
        )

        ctk.CTkLabel(
            header,
            text="Play with another computer on the same network.",
            font=("Segoe UI", 14),
            text_color=MUTED
        ).pack(
            anchor="w"
        )

        self.make_button(
            header,
            "← MENU",
            self.show_home,
            "#1E293B",
            "#334155",
            120,
            42
        ).pack(
            side="right",
            pady=8
        )

        center = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        center.pack(
            fill="both",
            expand=True,
            padx=75,
            pady=45
        )

        # CREATE

        create = ctk.CTkFrame(
            center,
            fg_color=PANEL,
            corner_radius=25,
            border_width=1,
            border_color=BORDER
        )

        create.pack(
            side="left",
            fill="both",
            expand=True,
            padx=12
        )

        ctk.CTkLabel(
            create,
            text="🌐",
            font=("Segoe UI", 46)
        ).pack(
            pady=(35, 8)
        )

        ctk.CTkLabel(
            create,
            text="CREATE ROOM",
            font=("Segoe UI", 24, "bold"),
            text_color=WHITE
        ).pack()

        ctk.CTkLabel(
            create,
            text="Create a room and share your\nIP address with Player 2.",
            font=("Segoe UI", 13),
            text_color=MUTED,
            justify="center"
        ).pack(
            pady=15
        )

        self.make_button(
            create,
            "CREATE ROOM",
            self.create_online_room,
            CYAN,
            CYAN_HOVER,
            210,
            52
        ).pack(
            pady=15
        )

        # JOIN

        join = ctk.CTkFrame(
            center,
            fg_color=PANEL,
            corner_radius=25,
            border_width=1,
            border_color=BORDER
        )

        join.pack(
            side="right",
            fill="both",
            expand=True,
            padx=12
        )

        ctk.CTkLabel(
            join,
            text="🔗",
            font=("Segoe UI", 46)
        ).pack(
            pady=(35, 8)
        )

        ctk.CTkLabel(
            join,
            text="JOIN ROOM",
            font=("Segoe UI", 24, "bold"),
            text_color=WHITE
        ).pack()

        ctk.CTkLabel(
            join,
            text="Enter Player 1's IP address.",
            font=("Segoe UI", 13),
            text_color=MUTED
        ).pack(
            pady=15
        )

        self.room_entry = ctk.CTkEntry(
            join,
            width=290,
            height=52,
            corner_radius=14,
            placeholder_text="Example: 192.168.1.5",
            justify="center",
            font=("Segoe UI", 16)
        )

        self.room_entry.pack(
            pady=8
        )

        self.make_button(
            join,
            "JOIN ROOM  →",
            self.join_online_room,
            BLUE,
            BLUE_HOVER,
            210,
            52
        ).pack(
            pady=15
        )


    # ========================================================
    # ONLINE GAME SCREEN
    # ========================================================

    def show_online_game(self):

        self.online_my_turn = False
        self.online_guess_ready = False
        self.online_last_guess = ""

        self.clear()

        header = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            height=82
        )

        header.pack(
            fill="x"
        )

        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="MODE 03  •  ONLINE",
            font=("Segoe UI", 25, "bold"),
            text_color=WHITE
        ).pack(
            side="left",
            padx=30
        )

        self.make_button(
            header,
            "← MENU",
            self.show_home,
            "#1E293B",
            "#334155",
            120,
            42
        ).pack(
            side="right",
            padx=28
        )

        body = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        body.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=25
        )

        # LEFT

        left = ctk.CTkFrame(
            body,
            fg_color=PANEL,
            corner_radius=24,
            border_width=1,
            border_color=BORDER
        )

        left.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 12)
        )

        ctk.CTkLabel(
            left,
            text="ONLINE GAME",
            font=("Segoe UI", 13, "bold"),
            text_color=MUTED
        ).pack(
            anchor="w",
            padx=25,
            pady=(22, 5)
        )

        self.online_status_label = ctk.CTkLabel(
            left,
            text="CONNECTING...",
            font=("Segoe UI", 26, "bold"),
            text_color=CYAN_HOVER
        )

        self.online_status_label.pack(
            anchor="w",
            padx=25,
            pady=(0, 15)
        )

        room_box = ctk.CTkFrame(
            left,
            fg_color=CARD,
            corner_radius=18
        )

        room_box.pack(
            fill="x",
            padx=25,
            pady=8
        )

        ctk.CTkLabel(
            room_box,
            text="ROOM",
            font=("Segoe UI", 10, "bold"),
            text_color=MUTED
        ).pack(
            pady=(10, 0)
        )

        self.online_room_label = ctk.CTkLabel(
            room_box,
            text="—",
            font=("Consolas", 27, "bold"),
            text_color=WHITE
        )

        self.online_room_label.pack(
            pady=(2, 10)
        )

        self.online_guess_entry = ctk.CTkEntry(
            left,
            height=55,
            corner_radius=15,
            placeholder_text="Enter 4 different digits",
            font=("Segoe UI", 18),
            justify="center"
        )

        self.online_guess_entry.pack(
            fill="x",
            padx=55,
            pady=(30, 10)
        )

        self.online_guess_button = self.make_button(
            left,
            "GUESS  →",
            self.submit_online_guess,
            CYAN,
            CYAN_HOVER,
            190,
            52
        )

        self.online_guess_button.pack()

        self.online_guess_entry.bind(
            "<Return>",
            lambda e: self.submit_online_guess()
        )

        # RIGHT

        right = ctk.CTkFrame(
            body,
            width=280,
            fg_color=PANEL,
            corner_radius=24,
            border_width=1,
            border_color=BORDER
        )

        right.pack(
            side="right",
            fill="y"
        )

        right.pack_propagate(False)

        ctk.CTkLabel(
            right,
            text="LIVE INFO",
            font=("Segoe UI", 18, "bold"),
            text_color=WHITE
        ).pack(
            pady=(25, 18)
        )

        self.online_round_info = self.info_box(
            right,
            "ROUND",
            "—"
        )

        self.online_stars_info = self.info_box(
            right,
            "STARS",
            "—"
        )

        self.online_points_info = self.info_box(
            right,
            "POINTS",
            "—"
        )

        self.online_history = ctk.CTkScrollableFrame(
            right,
            fg_color=CARD,
            corner_radius=15,
            height=220
        )

        self.online_history.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=15
        )


    # ========================================================
    # ONLINE VALID NUMBER
    # ========================================================

    def valid_number(self):

        while True:

            number = str(
                random.randint(
                    1000,
                    9999
                )
            )

            if len(set(number)) == 4:

                return number


    # ========================================================
    # ONLINE CALC
    #
    # Same calculation idea as tools.py.
    # Original files remain untouched.
    # ========================================================

    def calculate(
        self,
        guess,
        secret
    ):

        stars = 0
        points = 0

        for i in range(4):

            if guess[i] == secret[i]:

                stars += 1

        for i in range(4):

            for j in range(4):

                if i != j and guess[i] == secret[j]:

                    points += 1
                    break

        return stars, points


    # ========================================================
    # CREATE ROOM
    # ========================================================

    def create_online_room(self):

        self.online_role = "host"

        self.online_secret = self.valid_number()

        self.show_online_game()

        self.online_status_label.configure(
            text="CREATING ROOM...",
            text_color=CYAN_HOVER
        )

        thread = threading.Thread(
            target=self.host_server,
            daemon=True
        )

        thread.start()


    def host_server(self):

        try:

            server = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            server.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_REUSEADDR,
                1
            )

            server.bind(
                ("0.0.0.0", 5555)
            )

            server.listen(1)

            self.online_server = server

            local_ip = self.get_local_ip()

            self.after(
                0,
                lambda ip=local_ip:
                self.online_room_label.configure(
                    text=ip
                )
            )

            self.after(
                0,
                lambda:
                self.online_status_label.configure(
                    text="WAITING FOR PLAYER 2...",
                    text_color=YELLOW
                )
            )

            connection, address = server.accept()

            self.online_socket = connection
            self.online_connected = True

            # Same handshake concept as mood-3.py

            self.send_online(
                "Hello from Player 1!"
            )

            message = self.receive_online()

            if message is None:

                return

            self.after(
                0,
                lambda:
                self.online_status_label.configure(
                    text="PLAYER 2 CONNECTED • YOUR TURN",
                    text_color=GREEN_HOVER
                )
            )

            self.host_game_loop()

        except Exception as error:

            self.after(
                0,
                lambda e=error:
                self.online_status_label.configure(
                    text=f"CONNECTION ERROR",
                    text_color=RED
                )
            )

        finally:

            try:
                if self.online_server:
                    self.online_server.close()
            except:
                pass


    # ========================================================
    # JOIN ROOM
    # ========================================================

    def join_online_room(self):

        room = self.room_entry.get().strip()

        if not room:

            return

        self.online_role = "client"

        self.online_secret = self.valid_number()

        self.show_online_game()

        self.online_room_label.configure(
            text=room
        )

        self.online_status_label.configure(
            text="CONNECTING...",
            text_color=YELLOW
        )

        thread = threading.Thread(
            target=self.client_connect,
            args=(room,),
            daemon=True
        )

        thread.start()


    def client_connect(
        self,
        room
    ):

        try:

            client = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            client.settimeout(10)

            client.connect(
                (room, 5555)
            )

            client.settimeout(None)

            self.online_socket = client
            self.online_connected = True

            message = self.receive_online()

            if message is None:

                return

            self.send_online(
                "Hello from Player 2!"
            )

            self.after(
                0,
                lambda:
                self.online_status_label.configure(
                    text="WAITING FOR PLAYER 1...",
                    text_color=YELLOW
                )
            )

            self.disable_online_guess()

            # Wait for Player 1's first round

            message = self.receive_online()

            if message == "your round":

                self.after(
                    0,
                    self.enable_online_guess
                )

                self.client_game_loop()

        except Exception:

            self.after(
                0,
                lambda:
                self.online_status_label.configure(
                    text="CANNOT CONNECT",
                    text_color=RED
                )
            )


    # ========================================================
    # HOST LOOP
    # ========================================================

    def host_game_loop(self):

        while self.online_connected:

            self.after(
                0,
                self.enable_online_guess
            )

            # Wait until GUI submits a guess

            while self.online_connected:

                if getattr(
                    self,
                    "online_guess_ready",
                    False
                ):

                    self.online_guess_ready = False

                    guess = self.online_last_guess

                    break

                threading.Event().wait(0.05)

            else:

                return

            stars, points = self.calculate(
                guess,
                self.online_secret
            )

            self.after(
                0,
                lambda g=guess, s=stars, p=points:
                self.show_online_result(
                    "PLAYER 1",
                    g,
                    s,
                    p
                )
            )

            if stars == 4:

                self.send_online(
                    "YOU LOSE !"
                )

                self.after(
                    0,
                    lambda:
                    self.online_game_end(
                        "🏆 PLAYER 1 WINS!"
                    )
                )

                return

            self.send_online(
                "your round"
            )

            self.after(
                0,
                self.show_waiting_for_opponent
            )

            message = self.receive_online()

            if message == "YOU LOSE !":

                self.after(
                    0,
                    lambda:
                    self.online_game_end(
                        "PLAYER 2 WINS"
                    )
                )

                return


    # ========================================================
    # CLIENT LOOP
    # ========================================================

    def client_game_loop(self):

        while self.online_connected:

            self.after(
                0,
                self.enable_online_guess
            )

            while self.online_connected:

                if getattr(
                    self,
                    "online_guess_ready",
                    False
                ):

                    self.online_guess_ready = False

                    guess = self.online_last_guess

                    break

                threading.Event().wait(0.05)

            else:

                return

            stars, points = self.calculate(
                guess,
                self.online_secret
            )

            self.after(
                0,
                lambda g=guess, s=stars, p=points:
                self.show_online_result(
                    "PLAYER 2",
                    g,
                    s,
                    p
                )
            )

            if stars == 4:

                self.send_online(
                    "YOU LOSE !"
                )

                self.after(
                    0,
                    lambda:
                    self.online_game_end(
                        "🏆 PLAYER 2 WINS!"
                    )
                )

                return

            self.send_online(
                "your round"
            )

            self.after(
                0,
                self.show_waiting_for_opponent
            )

            message = self.receive_online()

            if message == "YOU LOSE !":

                self.after(
                    0,
                    lambda:
                    self.online_game_end(
                        "PLAYER 1 WINS"
                    )
                )

                return


    # ========================================================
    # ONLINE INPUT
    # ========================================================

    def enable_online_guess(self):

        self.online_my_turn = True

        self.online_guess_button.configure(
            state="normal"
        )

        self.online_guess_entry.configure(
            state="normal"
        )

        self.online_guess_entry.focus()

        player = (
            "PLAYER 1 • YOUR TURN"
            if self.online_role == "host"
            else
            "PLAYER 2 • YOUR TURN"
        )

        self.online_status_label.configure(
            text=player,
            text_color=GREEN_HOVER
        )


    def show_waiting_for_opponent(self):

        self.online_my_turn = False
        self.disable_online_guess()

        opponent = (
            "PLAYER 2"
            if self.online_role == "host"
            else
            "PLAYER 1"
        )

        self.online_status_label.configure(
            text=f"WAITING FOR {opponent}...",
            text_color=YELLOW
        )


    def disable_online_guess(self):

        self.online_my_turn = False

        self.online_guess_button.configure(
            state="disabled"
        )

        self.online_guess_entry.configure(
            state="disabled"
        )


    def submit_online_guess(self):

        if not self.online_my_turn:
            return

        value = self.online_guess_entry.get().strip()

        if not re.fullmatch(
            r"\d{4}",
            value
        ):

            self.online_status_label.configure(
                text="ENTER 4 DIGITS",
                text_color=YELLOW
            )

            return

        if len(set(value)) != 4:

            self.online_status_label.configure(
                text="DIGITS MUST BE DIFFERENT",
                text_color=YELLOW
            )

            return

        self.online_last_guess = value
        self.online_guess_ready = True

        self.online_round_info.configure(
            text=str(
                self.round_number + 1
            )
        )

        self.online_guess_entry.delete(
            0,
            "end"
        )

        # The guess was submitted. From this moment the opponent is playing.
        self.show_waiting_for_opponent()


    # ========================================================
    # ONLINE RESULT
    # ========================================================

    def show_online_result(
        self,
        player,
        guess,
        stars,
        points
    ):

        self.round_number += 1

        self.online_round_info.configure(
            text=str(
                self.round_number
            )
        )

        self.online_stars_info.configure(
            text=str(stars)
        )

        self.online_points_info.configure(
            text=str(points)
        )

        row = ctk.CTkFrame(
            self.online_history,
            fg_color=CARD_2,
            corner_radius=10
        )

        row.pack(
            fill="x",
            pady=4,
            padx=3
        )

        ctk.CTkLabel(
            row,
            text=player,
            font=("Segoe UI", 10, "bold"),
            text_color=CYAN_HOVER,
            width=75
        ).pack(
            side="left",
            padx=8,
            pady=8
        )

        ctk.CTkLabel(
            row,
            text=f"{guess}   ★ {stars}   ● {points}",
            font=("Segoe UI", 11, "bold"),
            text_color=WHITE
        ).pack(
            side="left",
            padx=5,
            pady=8
        )


    def online_game_end(
        self,
        text
    ):

        self.online_status_label.configure(
            text=text,
            text_color=GREEN_HOVER
            if "WIN" in text
            else RED
        )

        self.disable_online_guess()


    # ========================================================
    # SOCKET FUNCTIONS
    # ========================================================

    def send_online(
        self,
        data
    ):

        try:

            if self.online_socket:

                self.online_socket.sendall(
                    (data + "\n").encode("utf-8")
                )

        except:

            self.online_connected = False


    def receive_online(self):

        try:

            if not self.online_socket:

                return None

            # Read one complete protocol message.
            data = b""

            while not data.endswith(b"\n"):

                chunk = self.online_socket.recv(1)

                if not chunk:

                    self.online_connected = False
                    return None

                data += chunk

            return data.decode(
                "utf-8"
            ).strip()

        except:

            self.online_connected = False
            return None


    def get_local_ip(self):

        try:

            temp = socket.socket(
                socket.AF_INET,
                socket.SOCK_DGRAM
            )

            temp.connect(
                ("8.8.8.8", 80)
            )

            ip = temp.getsockname()[0]

            temp.close()

            return ip

        except:

            try:

                return socket.gethostbyname(
                    socket.gethostname()
                )

            except:

                return "127.0.0.1"


    # ========================================================
    # HISTORY
    # ========================================================

    def add_history(
        self,
        title,
        text,
        color
    ):

        if not hasattr(
            self,
            "history"
        ):

            return

        row = ctk.CTkFrame(
            self.history,
            fg_color=CARD_2,
            corner_radius=10
        )

        row.pack(
            fill="x",
            pady=4,
            padx=3
        )

        ctk.CTkLabel(
            row,
            text=title,
            width=90,
            anchor="w",
            font=("Segoe UI", 10, "bold"),
            text_color=color
        ).pack(
            side="left",
            padx=10,
            pady=8
        )

        ctk.CTkLabel(
            row,
            text=text,
            anchor="w",
            font=("Segoe UI", 11),
            text_color=WHITE
        ).pack(
            side="left",
            padx=4,
            pady=8
        )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    app = NumberGame()

    app.mainloop()