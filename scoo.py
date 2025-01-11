"""
Things to add:
    - Add ability to change drawing color
    - Add eraser
    - Add ability to change size of drawing thingy
    - Add integrated way to create new vocabulary sets (while im at it, change "books" to "vocab sets" or something similar)
    - Add mac support to the menu; must have program detect which os is being used
    - Reorganize write game's interface
    - Add a way to skip animation after pressing "enter" in write game; automatically skip if "show answer" has been selected
    - Disable buttons when checking answers
    - Error handling
"""


from tkinter import *
from tkinter import ttk
from copy import deepcopy
import random
import time
import kanjis
from presets import presets

root = Tk()
root.title('Writing practice for Japanese')
mainframe = ttk.Frame(root, padding='3 3 12 12')
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
style = ttk.Style()
root.tk.call('lappend', 'auto_path', 'awthemes-10.4.0')
root.tk.call('package', 'require', 'awdark')

# set default theme to dark
theme = open('default_theme.txt', 'r', encoding='utf8')
themestr = theme.read()
if themestr == 'dark':
    style.theme_use('awdark')
theme.close()

class Preferences:
    def __init__(self):
        self.chapter_txt_var = StringVar()
        self.book_txt_var = StringVar()
        self.kanji_yn = BooleanVar(value=True)
        self.game_txt = StringVar()
        self.combed_dict = {}

    # Create book preference combo box
    def book_pref_combo(self):
        self.book_label = ttk.Label(mainframe, text='Vocabulary set')
        self.book_combo = ttk.Combobox(mainframe, textvariable=self.book_txt_var)
        self.book_combo.state(['readonly'])

        # Set values of combo box to books listed in Available_books.txt
        file = open('Available_books.txt', 'r', encoding='utf8')
        filestr = file.read()
        file_lst = filestr.split("\n")
        self.book_combo['values'] = file_lst
        file.close()

        self.book_combo.bind('<<ComboboxSelected>>', self.set_chapter_values)

    # Set chapter values based on selected book
    def set_chapter_values(self, event):
        file = open(f'book_{self.book_txt_var.get().lower()}/Available_Chapters.txt', 'r', encoding='utf8')
        filestr = file.read()
        file_lst = filestr.split('\n')
        self.chapter['values'] = file_lst
        file.close()

    # Create chapter preference combo box
    def chapter_pref_combo(self):
        self.chapter_label = ttk.Label(mainframe, text='Chapter')
        self.chapter = ttk.Combobox(mainframe, textvariable=self.chapter_txt_var)
        self.chapter['values'] = ['Select a vocabulary set']
        self.chapter.state(['readonly'])

        self.chapter.bind('<<ComboboxSelected>>', self.set_vocab_values)

    # Set values of vocab preference combobox when a chapter is selected
    def set_vocab_values(self, event):
        file = open(f'book_{self.book_txt_var.get().lower()}/chapter_{self.chapter_txt_var.get()}/vocab_types.txt', 'r', encoding='utf8')
        file_str = file.read()
        self.vocab_file_lst = file_str.split('\n')
        self.listvar.set(self.vocab_file_lst)
        file.close()

    # Create vocabulary type preferences list box; responds to create_chapter_pref
    def vocab_pref_lbox(self):
        self.vocab_label = ttk.Label(mainframe, text='Select Vocabulary Word Type', )
        self.listvar = StringVar(value=['Select a Chapter'])
        self.vocab_lbox = Listbox(mainframe, listvariable=self.listvar, height=10, selectmode='multiple')

    # create a checkbox to determine whether the user wants kanji in their study set, or just hiragana
    def create_kanji_checkbox(self):
        self.kanji = ttk.Checkbutton(mainframe, text='Study with Kanji?', variable=self.kanji_yn, onvalue=True, offvalue=False)

    # create combobox so user can input whether they want to play multiple choice or write
    def game_pref_combo(self):
        self.game_label = ttk.Label(mainframe, text='Select game.')
        self.game = ttk.Combobox(mainframe, textvariable=self.game_txt)
        self.game.state(['readonly'])
        self.game['values'] = ['Multiple Choice', 'Write', 'Type', 'Map']

    # create button for user to click when they are done with choosing their preferences.
    def pref_done_button(self):
        global pref_done
        pref_done = ttk.Button(mainframe, text='Finished!', command=self.start_main)
        self.pref_done = pref_done

    # All widgets will be grid
    def display(self):
        self.book_label.grid(column=1, row=1, sticky=W)
        self.book_combo.grid(column=1, row=2, sticky=W)
        self.chapter_label.grid(column=1, row=3, sticky=W)
        self.chapter.grid(column=1, row=4, sticky=W)
        self.game_label.grid(column=1, row=5, sticky=W)
        self.game.grid(column=1, row=6, sticky=W)
        self.vocab_label.grid(column=2, row=1, sticky=W)
        self.vocab_lbox.grid(column=2, row=2, sticky=W, rowspan=8)
        self.kanji.grid(column=1, row=7, sticky=W)
        self.pref_done.grid(column=1, row=8, sticky=W)

    # If user selects "All" during vocabulary selection, this function will be called
    def get_all_from_chap(self, chapter):
        full_dict = {}
        file = open(f'book_{self.book_txt_var.get().lower()}/Jpn_study_proj-main/chapter_{chapter}/vocab_types.txt', 'r', encoding='utf8')
        file_str = file.read()
        file_lst = file_str.split('\n')
        for i in file_lst[1:]:
            d = self.create_dict(chapter=chapter, vocab_type=i)
            full_dict.update(d)

        return full_dict

    # Given a chapter and vocabulary type, this function combines the associated txt files into an ordered dictionary
    def create_dict(self, chapter, vocab_type):
        d = {}
        eng_f = open(f'book_{self.book_txt_var.get().lower()}/chapter_{chapter}/{vocab_type}_Eng.txt', 'r', encoding='utf8')
        eng_f_str = eng_f.read()
        eng_f_lst = eng_f_str.split('\n')
        eng_f.close()

        if self.kanji_yn.get():
            try:
                jpn_f = open(f'book_{self.book_txt_var.get().lower()}/chapter_{chapter}/{vocab_type}_Jpn_Kanji.txt', 'r', encoding='utf8')
            except:
                jpn_f = open(f'book_{self.book_txt_var.get().lower()}/chapter_{chapter}/{vocab_type}_Jpn.txt', 'r', encoding='utf8')
        else:
            jpn_f = open(f'book_{self.book_txt_var.get().lower()}/chapter_{chapter}/{vocab_type}_Jpn.txt', 'r', encoding='utf8')
        jpn_f_str = jpn_f.read()
        jpn_f_lst = jpn_f_str.split('\n')
        jpn_f.close()

        for i in range(0, len(eng_f_lst)):
            d[eng_f_lst[i]] = jpn_f_lst[i]
        
        return d
    
    # Takes all selections from Listbox and creates their associated dictionaries, then combines them all into one dictionary
    def combine_dicts(self):
        selected_indices = self.vocab_lbox.curselection()
        selected_vocab_types = []
        for i in selected_indices:
            selected_vocab_types.append(self.vocab_file_lst[i])
        s = ''
        if selected_vocab_types[0] == 'All':
            self.combed_dict = self.get_all_from_chap(chapter=self.chapter_txt_var.get())
        else:
            for i in selected_vocab_types:
                foo = self.create_dict(chapter=self.chapter_txt_var.get(), vocab_type=i)
                self.combed_dict.update(foo)

    # function will open up the chosen files and combine them into a dictionary, then start the chosen study game
    def start_main(self):
        self.combine_dicts()

        if self.game_txt.get() == 'Multiple Choice':
            mc = MultipleChoice(referral_dict=self.combed_dict)
            mc.start_mc()
        elif self.game_txt.get() == 'Write':
            w = Write(reference_dict=self.combed_dict)
            w.choose_q()
        elif self.game_txt.get() == 'Type':
            t = Type(reference_dict=self.combed_dict)
            t.get_q_a()
        elif self.game_txt.get() == 'Map':
            k = MapAnimations(reference_dict=self.combed_dict)
            k.create()

    def set_presets(self):
        if presets['book'] != '':
            self.book_txt_var.set(presets['book'])
            if presets['chapter'] != '':
                self.chapter_txt_var.set(presets['chapter'])
                self.set_vocab_values(event=None)
        if presets['game'] != '':
            self.game_txt.set(presets['game'])

        self.kanji_yn.set(presets['kanji'])
        for i in presets['vocab']:
            self.vocab_lbox.selection_set(i)

    def run(self):
        self.book_pref_combo()
        self.chapter_pref_combo()
        self.vocab_pref_lbox()
        self.create_kanji_checkbox()
        self.game_pref_combo()
        self.pref_done_button()
        self.display()
        self.set_presets()


class MultipleChoice:
    def __init__(self, referral_dict):
        self.referral_dict = referral_dict
        self.main_dict = deepcopy(self.referral_dict)
        self.turn_count = 0
        self.amnt_correct = 0
        self.amnt_incorrect = 0
        self.mc_window = Toplevel(root)
        self.m_choice_mainframe = ttk.Frame(self.mc_window)
        self.end_subframe = ttk.Frame(self.m_choice_mainframe)
        self.turn_disp = StringVar()
        self.q_disp = StringVar()
        self.correct_status = StringVar()
        self.b1_txt, self.b2_txt, self.b3_txt, self.b4_txt = StringVar(), StringVar(), StringVar(), StringVar()
        self.b1 = ttk.Button(self.m_choice_mainframe, textvariable=self.b1_txt, command=lambda : self.check_button(self.b1_txt.get()))
        self.b2 = ttk.Button(self.m_choice_mainframe, textvariable=self.b2_txt, command=lambda : self.check_button(self.b2_txt.get()))
        self.b3 = ttk.Button(self.m_choice_mainframe, textvariable=self.b3_txt, command=lambda : self.check_button(self.b3_txt.get()))
        self.b4 = ttk.Button(self.m_choice_mainframe, textvariable=self.b4_txt, command=lambda : self.check_button(self.b4_txt.get()))
        self.turn_label = ttk.Label(self.m_choice_mainframe, textvariable=self.turn_disp)
        self.question_label = ttk.Label(self.m_choice_mainframe, textvariable=self.q_disp)
        self.correct_label = ttk.Label(self.m_choice_mainframe, textvariable=self.correct_status)
        self.uni_quit = ttk.Button(self.m_choice_mainframe, text='Quit multiple choice', command=self.destroy_mc)
        
        self.again_label_txt = StringVar()
        self.again_label = ttk.Label(self.end_subframe, textvariable=self.again_label_txt)
        self.end_b1 = ttk.Button(self.end_subframe, text='Yes', command=self.start_from_end)
        self.end_b2 = ttk.Button(self.end_subframe, text='No', command=self.destroy_mc)

        self.end_widget_lst = [self.again_label, self.end_b1, self.end_b2]
        self.cycle = True

    def start_mc(self):
        self.answer_dict = deepcopy(self.referral_dict)
        self.turn_count += 1

        self.q, self.a = random.choice(list(self.main_dict.items()))
        del self.main_dict[self.q]

        self.answer_lst = list(self.answer_dict.values())
        self.answer_lst.remove(self.a)
        wr1 = random.choice(self.answer_lst)
        self.answer_lst.remove(wr1)
        wr2 = random.choice(self.answer_lst)
        self.answer_lst.remove(wr2)
        wr3 = random.choice(self.answer_lst)
        self.answer_lst.remove(wr3)
        self.answer_lst = [self.a, wr1, wr2, wr3]
        random.shuffle(self.answer_lst)

        self.set_mc()

    def set_mc(self):
        self.turn_disp.set('You are on turn ' + str(self.turn_count))
        self.q_disp.set('Question: ' + self.q)
        self.b1_txt.set(self.answer_lst[0])
        self.b2_txt.set(self.answer_lst[1])
        self.b3_txt.set(self.answer_lst[2])
        self.b4_txt.set(self.answer_lst[3])
        try:
            self.b1.state(['!disabled'])
            self.b2.state(['!disabled'])
            self.b3.state(['!disabled'])
            self.b4.state(['!disabled'])
        except:
            pass

        if self.cycle:
            self.display_mc()
            self.cycle = False

    def display_mc(self):
        self.m_choice_mainframe.grid(column=1, row=5, columnspan=10, sticky=(W, E))

        self.question_label.grid(column=1, row=1, columnspan=10, sticky=W)
        self.b1.grid(column=1, row=2, sticky=W)
        self.b2.grid(column=2, row=2, padx=35, sticky=W)
        self.b3.grid(column=1, row=3, sticky=W)
        self.b4.grid(column=2, row=3, padx=35, sticky=W)
        self.turn_label.grid(column=1, row=4, sticky=W)
        self.correct_label.grid(column=2, row=4, columnspan=2, sticky=(W, E))
        self.uni_quit.grid(column=5, row=3, padx=100, sticky=E)
        self.end_subframe.grid(column=1, row=5, columnspan=10,sticky=W)

    def check_button(self, inp_a):
        if self.a == inp_a:
            self.amnt_correct += 1
            self.correct_status.set('Correct! :D')
            mainframe.update()
            time.sleep(1)
            self.correct_status.set(' ')
            mainframe.update()
        else:
            self.amnt_incorrect += 1
            self.correct_status.set(f'Incorrect :(. Correct answer is {self.a}')
            mainframe.update()
            time.sleep(3)
            self.correct_status.set(' ')
            mainframe.update()

        if len(self.main_dict) > 0:
            self.start_mc()
        else:
            self.b1.state(['disabled'])
            self.b2.state(['disabled'])
            self.b3.state(['disabled'])
            self.b4.state(['disabled'])

            self.again_label_txt.set(f'You are done!\nYou got {self.amnt_correct} question(s) correct and {self.amnt_incorrect} questions wrong with an accuracy of {(self.amnt_correct/len(self.referral_dict))*100}%!\nWould you like to play again?')
            self.again_label.grid(column=1, row=1, columnspan=4, sticky=W)
            self.end_b1.grid(column=2, row=2, sticky=W)
            self.end_b2.grid(column=3, row=2)

    def start_from_end(self):
        for i in self.end_widget_lst:
            i.grid_forget()
        self.main_dict = deepcopy(self.referral_dict)
        self.amnt_correct, self.amnt_incorrect, self.turn_count = 0, 0, 0
        self.start_mc()

    def destroy_mc(self):
        self.mc_window.destroy()


class Write:
    def __init__(self, reference_dict):
        self.write_window = Toplevel(root)
        self.write_frame = ttk.Frame(self.write_window, cursor="pencil")
        self.reference_dict = reference_dict
        self.animation_frame = ttk.Frame(self.write_frame)
        self.animation_frame['borderwidth'] = 5
        self.animation_frame['relief'] = 'sunken'
        self.animation_canvas = Canvas(self.animation_frame, width=500, height=400)
        self.canvas_frame = ttk.Frame(self.write_frame)
        self.canvas_frame['borderwidth'] = 5
        self.canvas_frame['relief'] = 'sunken'
        self.canvas = Canvas(self.canvas_frame, width=500, height=400)
        self.q_txt, self.a_txt = StringVar(), StringVar()
        self.q_label = ttk.Label(self.write_frame, textvariable=self.q_txt)
        self.a_label = ttk.Label(self.write_frame, textvariable=self.a_txt)
        self.fin_label = ttk.Label(self.write_frame, text="You've reached the end!\nWould you like to go again?")
        self.clear_button = ttk.Button(self.write_frame, text='Clear Canvas', command=self.clear_canv)
        self.undo_button = ttk.Button(self.write_frame, text='Undo', command=self.undo)
        self.enter_button = ttk.Button(self.write_frame, text='Enter', command=self.post_enter)
        self.quit_button = ttk.Button(self.write_frame, text='Quit write', command=self.destroy_write)
        self.show_ans_button = ttk.Button(self.write_frame, text='Show answer', command=self.draw)
        self.turn_count = 0
        self.main_d = {}
        self.buttonY = ttk.Button(self.write_frame, text='Play Again', command=self.choose_q)
        self.buttonN = ttk.Button(self.write_frame, text='Quit', command=self.destroy_write)
        self.undo_lst = []
        self.tag_num = 0
        self.tag = 'tag' + str(self.tag_num)
        self.end_widget_lst = []
        self.line_color = 'black'

        self.canvas.bind("<Button-1>", self.savePosn)
        self.canvas.bind("<B1-Motion>", self.addLine)
        self.canvas.bind('<ButtonRelease-1>', self.increase_tag)

    def choose_q(self):
        self.turn_count += 1
        if len(self.end_widget_lst) > 0:
            for i in self.end_widget_lst:
                i.grid_forget()
        if not self.main_d:
            self.main_d = deepcopy(self.reference_dict)
        
        self.q, self.a = random.choice(list(self.main_d.items()))
        del self.main_d[self.q]

        self.q_txt.set(self.q)

        if self.turn_count == 1:
            self.display_canv()

    def display_canv(self):
        self.write_frame.grid(column=1, row=5, columnspan=20, rowspan=11)
        self.q_label.grid(column=1, row=1, columnspan=2, sticky=W)
        self.canvas_frame.grid(column=1, row=3, columnspan=10, rowspan=10, sticky=W)
        self.canvas.grid(column=1, row=1, sticky=(N, W))
        self.animation_frame.grid(column=11, row=3, columnspan=10, rowspan=10, sticky=W)
        self.animation_canvas.grid(column=1, row=1, sticky=(N, W))
        self.clear_button.grid(column=1, row=2, sticky=W)
        self.undo_button.grid(column=2, row=2, sticky=E)
        self.enter_button.grid(column=3, row=2, sticky=W)
        self.quit_button.grid(column=5, row=2, sticky=E)
        self.show_ans_button.grid(column=4, row=2, sticky=W)
        self.theme()

    def theme(self):
        if style.theme_use() == 'awdark':
            self.canvas.configure(background='black')
            self.animation_canvas.configure(background='black')
            self.line_color = 'white'

    def clear_canv(self):
        self.canvas.delete('all')
        self.undo_lst = []
    
    def savePosn(self, event):
        self.lastx, self.lasty = event.x, event.y

    def addLine(self, event):
        self.canvas.create_line((self.lastx, self.lasty, event.x, event.y), tags=self.tag, smooth=True, width=1.5, fill=self.line_color)
        self.savePosn(event)

    def undo(self):
        to_undo = self.undo_lst[-1]
        for i in self.canvas.find_withtag(to_undo):
            self.canvas.delete(i)
        self.undo_lst.remove(to_undo)
    
    def increase_tag(self, event):
        self.undo_lst.append(self.tag)
        self.tag_num += 1
        self.tag = 'tag' + str(self.tag_num)

    def draw(self):
       self.animation_canvas.delete('all')
       for i in kanjis.encoded_kanjis[self.a]:
            self.animation_frame.update()
            time.sleep(0.25)
            for j in i:
                self.animation_canvas.create_line((j[0], j[1], j[2], j[3]), smooth=True, width=1.5, fill=self.line_color)
                self.animation_frame.update()
                # time.sleep(0.0001)

    def post_enter(self):
        try:
            self.draw()
            mainframe.update()
        except KeyError:
            pass
        time.sleep(2)
        # self.a_txt.set(' ')
        mainframe.update()
        self.clear_canv()
        self.animation_canvas.delete('all')
        if not self.main_d:
            self.fin_label.grid(column=1, row=9, columnspan=3, sticky=W)
            self.buttonY.grid(column=2, row=9, sticky=W)
            self.buttonN.grid(column=3, row=9, sticky=W)
            self.end_widget_lst = [self.fin_label, self.buttonY, self.buttonN]
        else:
            self.choose_q()

    def destroy_write(self):
        self.write_window.destroy()


class Type:
    def __init__(self, reference_dict):
        self.reference_dict = reference_dict
        self.main_dict = deepcopy(self.reference_dict)
        self.type_window = Toplevel(root)
        self.type_frame = ttk.Frame(self.type_window)
        self.end_subframe = ttk.Frame(self.type_frame)
        self.question_txt, self.entry_txt, self.correct_status_txt, self.turn_txt = StringVar(), StringVar(), StringVar(value=' '), StringVar()
        self.question_label = ttk.Label(self.type_frame, textvariable=self.question_txt)
        self.entry = ttk.Entry(self.type_frame, textvariable=self.entry_txt)
        self.correct_status = ttk.Label(self.type_frame, textvariable=self.correct_status_txt)
        self.turn_label = ttk.Label(self.type_frame, textvariable=self.turn_txt)
        self.quit = ttk.Button(self.type_frame, text='Quit Type.', command=self.destroy_type)
        self.enter_button = ttk.Button(self.type_frame, text='Enter', command=self.check_ans)
        self.turns = 0
        self.q, self.a = None, None
        self.amnt_correct, self.amnt_incorrect = 0, 0
        self.post_game_label_txt = StringVar()
        self.post_game_label = ttk.Label(self.end_subframe, textvariable=self.post_game_label_txt)
        self.play_again = ttk.Button(self.end_subframe, text='Yes', command=self.start_from_end)
        self.dont_play_again = ttk.Button(self.end_subframe, text='No', command=self.destroy_type)
        self.cycle = True
        root.bind('<Return>', lambda e: self.enter_button.invoke())

        self.post_game_lst = [self.post_game_label, self.play_again, self.dont_play_again]

    def display_widgets(self):
        self.type_frame.grid(column=1, row=5, columnspan=10, sticky=(W, E))
        self.turn_label.grid(column=1, row=1, sticky=W)
        self.question_label.grid(column=2, row=1, columnspan=2, sticky=W)
        self.entry.grid(column=2, row=2, sticky=W)
        self.correct_status.grid(column=3, row=3, columnspan=2, rowspan=2, sticky=(N, W))
        self.quit.grid(column=5, row=1, sticky=E)
        self.enter_button.grid(column=3, row=2, sticky=W)
        self.end_subframe.grid(column=1, row=4, columnspan=10, sticky=W)

    def get_q_a(self):
        self.turns += 1
        self.turn_txt.set('You are on turn ' + str(self.turns))

        self.q, self.a = random.choice(list(self.main_dict.items()))
        del self.main_dict[self.q]

        self.question_txt.set('Question: ' + self.q)

        if self.cycle:
            self.display_widgets()
            self.cycle = False



    def check_ans(self):
        self.enter_button.state(['disabled'])
        if self.entry_txt.get() == self.a:
            self.amnt_correct += 1
            self.correct_status_txt.set('Correct! :D')
            mainframe.update()
            time.sleep(1)
            self.correct_status_txt.set(' ')
            self.entry.delete(0, 'end')
            mainframe.update()
        else:
            self.amnt_incorrect += 1
            self.correct_status_txt.set(f'Sorry but wrong :(\nCorrect answer is {self.a}')
            mainframe.update()
            time.sleep(2)
            self.correct_status_txt.set(' ')
            self.entry.delete(0, 'end')
            mainframe.update()
        
        if len(self.main_dict) == 0:
            self.post_game_label_txt.set(f'You are done!\nYou got {self.amnt_correct} question(s) correct and {self.amnt_incorrect} questions wrong with an accuracy of {(self.amnt_correct/len(self.reference_dict))*100}%!\nWould you like to play again?')
            self.post_game_label.grid(column=1, row=1, columnspan=5, rowspan=3, sticky=(N, W))
            self.play_again.grid(column=1, row=4, sticky=W)
            self.dont_play_again.grid(column=2, row=4, sticky=W)
        else:
            self.enter_button.state(['!disabled'])
            self.get_q_a()

    def start_from_end(self):
        for i in self.post_game_lst:
            i.grid_forget()
        
        self.amnt_correct = 0
        self.amnt_incorrect = 0
        self.turns = 0
        self.main_dict = deepcopy(self.reference_dict)
        self.enter_button.state(['!disabled'])
        self.get_q_a()
        

    def destroy_type(self):
        self.type_window.destroy()


class MapAnimations:
    def __init__(self, reference_dict):
        self.reference_dict = reference_dict
        self.current_dict_index = 0
        self.map_window = Toplevel(root)
        self.canvas_frame = ttk.Frame(self.map_window)
        self.canvas_frame['borderwidth'] = 5
        self.canvas_frame['relief'] = 'sunken'
        self.canvas = Canvas(self.canvas_frame, width=500, height=400)
        self.q_txt = StringVar()
        self.q_label = ttk.Label(self.canvas_frame, textvariable=self.q_txt)
        self.redo_button = ttk.Button(self.canvas_frame, text="Redo.", command=self.redo)
        self.undo_button = ttk.Button(self.canvas_frame, text='Undo', command=self.undo)
        self.enter_button = ttk.Button(self.canvas_frame, text='Enter', command=self.enter)
        self.sure_label = ttk.Label(self.canvas_frame, text='Are you sure?')
        self.sure_button = ttk.Button(self.canvas_frame, text='yes', command=self.yes)
        self.not_sure_button = ttk.Button(self.canvas_frame, text='no', command=self.no)
        self.quit_button = ttk.Button(self.canvas_frame, text='Quit', command=self.quit)
        self.skip_button = ttk.Button(self.canvas_frame, text="Skip", command=self.skip)
        self.undo_lst = []
        self.tag_num = 0
        self.tag = 'tag' + str(self.tag_num)
        self.canvas.bind('<Button-1>', self.savePosn)
        self.canvas.bind("<B1-Motion>", self.addLine)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        self.encoded_lst = []
        self.radical_lst = []

    def create(self):
        self.canvas_frame.grid(column=1, row=8, columnspan=10, rowspan=10, sticky=W)
        self.q_label.grid(column=1, row=1, sticky=W)
        self.redo_button.grid(column=2, row=1, sticky=W)
        self.undo_button.grid(column=3, row=1, sticky=W)
        self.skip_button.grid(column=4, row=1, sticky=W)
        self.enter_button.grid(column=5, row=1, sticky=E)
        self.canvas.grid(column=1, row=2, columnspan=10, rowspan=10, sticky=(N, W))
        self.quit_button.grid(column=6, row=1, sticky=E)
        self.start()

    def start(self):
        self.q_txt.set(list(self.reference_dict.values())[self.current_dict_index])
        mainframe.update()
        self.current_dict_index += 1

    def savePosn(self, event):
        self.lastx, self.lasty = event.x, event.y

    def addLine(self, event):
        self.canvas.create_line((self.lastx, self.lasty, event.x, event.y), tags=self.tag, smooth=True, width=1.5)
        self.radical_lst.append([self.lastx, self.lasty, event.x, event.y])
        self.savePosn(event)

    def on_release(self, event):
        self.undo_lst.append(self.tag)
        self.tag_num += 1
        self.tag = 'tag' + str(self.tag_num)
        self.encoded_lst.append(self.radical_lst)
        self.radical_lst = []

    def redo(self):
        self.canvas.delete('all')
        self.undo_lst = []
        self.encoded_lst = []
    
    def undo(self):
        to_undo = self.undo_lst[-1]
        for i in self.canvas.find_withtag(to_undo):
            self.canvas.delete(i)
        self.undo_lst.remove(to_undo)
        self.encoded_lst.remove(self.encoded_lst[-1])

    def draw(self):
        for i in self.encoded_lst:
            mainframe.update()
            time.sleep(0.25)
            for j in i:
                self.canvas.create_line((j[0], j[1], j[2], j[3]), smooth=True, width=1.5)
                mainframe.update()
                time.sleep(0.001)

    def enter(self):
        self.canvas.delete('all')
        self.draw()
        self.sure_label.grid(column=1, row=13, sticky=W)
        self.sure_button.grid(column=1, row=14, sticky=W)
        self.not_sure_button.grid(column=2, row=14, sticky=E)

    def yes(self):
        kanjis.encoded_kanjis[self.q_txt.get()] = self.encoded_lst
        file = open('kanji_dump.txt', 'w', encoding='utf8')
        file.write("encoded_kanjis = " + str(kanjis.encoded_kanjis))
        file.close()
        self.redo()
        self.sure_label.grid_forget()
        self.sure_button.grid_forget()
        self.not_sure_button.grid_forget()
        self.start()

    def no(self):
        self.redo()
        self.current_dict_index -= 1
        self.sure_label.grid_forget()
        self.sure_button.grid_forget()
        self.not_sure_button.grid_forget()
        self.start()

    def quit(self):
        self.map_window.destroy()

    def skip(self):
        self.encoded_lst = []
        self.canvas.delete('all')
        self.start()

preferences = Preferences()

root.option_add('*tearOff', 0)

# Start menu code
menubar = Menu(root)
root.config(menu=menubar)

menu_look = Menu(menubar)
menubar.add_cascade(menu=menu_look, label='Preferences')
dark_mode = BooleanVar()
if style.theme_use() == 'awdark':
    dark_mode.set(True)
menu_look.add_checkbutton(label='Dark Mode', variable=dark_mode, onvalue=1, offvalue=0)

def default_theme():
    file = open("default_theme.txt", "w", encoding="utf8")
    if dark_mode.get():
        file.write('dark')
    elif not dark_mode.get():
        file.write('')
    file.close()

menu_look.add_command(label='Made current default.', command=default_theme)

def to_dark(arg_one, arg_two, arg_three):
    if dark_mode.get():
        style.theme_use("awdark")
    elif not dark_mode.get():
        style.theme_use('vista')

dark_mode.trace_add('write', to_dark)

menu_presets = Menu(menubar)
menubar.add_cascade(menu=menu_presets, label='Presets')
    
def new_preset():
    dictstr = "presets = {\n'book' : '" + preferences.book_txt_var.get() + "', \n'chapter' : '" + preferences.chapter_txt_var.get() + "', \n'game' :'" + preferences.game_txt.get() + "', \n'kanji' : " +  str(preferences.kanji_yn.get()) + ", \n'vocab' : ["
    for i in preferences.vocab_lbox.curselection():
        dictstr += str(i) + ','
    dictstr += '] }'

    file = open('presets.py', 'w', encoding='utf8')
    file.write(dictstr)
    file.close()

def reset_preset():
    file = open('presets.py', 'w', encoding='utf8')
    file.write("presets = {'book' : '',\n 'chapter' : '', \n'game' :'', \n'kanji' : True, \n'vocab' : [] }")
    file.close()

menu_presets.add_command(label='Set preset', command=new_preset)
menu_presets.add_command(label='Reset preset', command=reset_preset)
# End menu code

preferences.run()

root.mainloop()