from tkinter import *
from tkinter import ttk
from copy import deepcopy
import random
import time
import kanjis

root = Tk()
root.title('Writing practice for Japanese')
mainframe = ttk.Frame(root, padding='3 3 12 12')
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

class Preferences:
    def __init__(self):
        self.chapter_txt_var = StringVar()
        self.vocab_txt_var = StringVar()
        self.kanji_yn = BooleanVar(value=True)
        self.game_txt = StringVar()
        self.combed_dict = {}
        self.widget_lst = []
        self.added_dicts = []
        self.added_dicts_txt = StringVar()

    # Create chapter preference combo box
    def chapter_pref_combo(self):
        self.chapter_label = ttk.Label(mainframe, text='Select Chapter')
        self.chapter = ttk.Combobox(mainframe, textvariable=self.chapter_txt_var)
        file = open('Available_Chapters.txt', 'r', encoding='utf8')
        filestr = file.read()
        file_lst = filestr.split('\n')
        self.chapter['values'] = file_lst
        file.close()
        self.chapter.state(['readonly'])
        self.chapter.bind('<<ComboboxSelected>>', self.set_vocab_values)
        self.widget_lst.extend([self.chapter_label, self.chapter])

    # Create vocabulary type preferences combo box; responds to create_chapter_pref
    def vocab_pref_combo(self):
        self.vocab_label = ttk.Label(mainframe, text='Select Vocabulary Word Type')
        self.vocab = ttk.Combobox(mainframe, textvariable=self.vocab_txt_var)
        self.vocab.state(['readonly'])
        self.vocab['values'] = ['Please choose a chapter first.']
        self.widget_lst.extend([self.vocab_label, self.vocab])

    # create a checkbox to determine whether the user wants kanji in their study set, or just hiragana
    def create_kanji_checkbox(self):
        self.kanji = ttk.Checkbutton(mainframe, text='Study with Kanji?', variable=self.kanji_yn, onvalue=True, offvalue=False)
        self.widget_lst.append(self.kanji)

    # create combobox so user can input whether they want to play multiple choice or write
    def game_pref_combo(self):
        self.game_label = ttk.Label(mainframe, text='Choose multiple choice or write.')
        self.game = ttk.Combobox(mainframe, textvariable=self.game_txt)
        self.game.state(['readonly'])
        self.game['values'] = ['Multiple Choice', 'Write', 'Type', 'Map']
        self.widget_lst.extend([self.game_label, self.game])

    # create button for user to click when they are done with choosing their preferences.
    def pref_done_button(self):
        global pref_done, add_dict, delete_dict_button
        pref_done = ttk.Button(mainframe, text='Finished!', command=self.start_main)
        add_dict = ttk.Button(mainframe, text='Add!', command=self.combine_dicts)
        delete_dict_button = ttk.Button(mainframe, text='Delete!', command=self.delete_dict)
        self.display_added_dicts = ttk.Label(mainframe, textvariable=self.added_dicts_txt)
        self.delete_dict_button = delete_dict_button
        self.add_dict = add_dict
        self.pref_done = pref_done
        self.widget_lst.extend([self.pref_done, self.add_dict, self.delete_dict])

    # Set values of vocab preference combobox when a chapter is selected
    def set_vocab_values(self, event):
        file = open(f'chapter_{self.chapter_txt_var.get()}/vocab_types.txt', 'r', encoding='utf8')
        file_str = file.read()
        file_lst = file_str.split('\n')
        self.vocab['values'] = file_lst
        file.close()

    def display(self):
        self.chapter_label.grid(column=1, row=1, sticky=W)
        self.chapter.grid(column=1, row=2, sticky=W)
        self.vocab_label.grid(column=2, row=1, sticky=W)
        self.vocab.grid(column=2, row=2, sticky=W)
        self.kanji.grid(column=1, row=3, sticky=W)
        self.game_label.grid(column=3, row=1, sticky=W)
        self.game.grid(column=3, row=2, sticky=W)
        self.pref_done.grid(column=4, row=3, sticky=W)
        self.add_dict.grid(column=2, row=3, sticky=W)
        self.delete_dict_button.grid(column=3, row=3, sticky=W)
        self.display_added_dicts.grid(column=2, row=4, columnspan=10, sticky=W)


    def get_all_from_chap(self, chapter):
        full_dict = {}
        file = open(f'Jpn_study_proj-main/chapter_{chapter}/vocab_types.txt', 'r', encoding='utf8')
        file_str = file.read()
        file_lst = file_str.split('\n')
        for i in file_lst[1:]:
            d = self.create_dict(chapter=chapter, vocab_type=i)
            full_dict.update(d)

        return full_dict

    def get_all_chaps(self): # useless for the time being
        full_dict = {}
        file = open('Jpn_study_proj-main/Available_Chapters.txt', 'r', encoding='utf8')
        file_str = file.read()
        file_lst = file_str.split('\n')

        for i in file_lst[1:]:
            if self.vocab_txt_var.get() == 'All':
                d = self.get_all_from_chap(chapter=i)
                full_dict.update(d)
            else:
                d = self.create_dict(chapter=i, vocab_type=self.vocab_txt_var.get())
                full_dict.update(d)
        
        return full_dict

    def create_dict(self, chapter, vocab_type):
        d = {}
        eng_f = open(f'chapter_{chapter}/{vocab_type}_Eng.txt', 'r', encoding='utf8')
        eng_f_str = eng_f.read()
        eng_f_lst = eng_f_str.split('\n')
        eng_f.close()

        if self.kanji_yn.get():
            try:
                jpn_f = open(f'chapter_{chapter}/{vocab_type}_Jpn_Kanji.txt', 'r', encoding='utf8')
            except:
                jpn_f = open(f'chapter_{chapter}/{vocab_type}_Jpn.txt', 'r', encoding='utf8')
        else:
            jpn_f = open(f'chapter_{chapter}/{vocab_type}_Jpn.txt', 'r', encoding='utf8')
        jpn_f_str = jpn_f.read()
        jpn_f_lst = jpn_f_str.split('\n')
        jpn_f.close()

        for i in range(0, len(eng_f_lst)):
            d[eng_f_lst[i]] = jpn_f_lst[i]
        
        return d
    
    def combine_dicts(self):
        s = ''
        if self.vocab_txt_var.get() == 'All':
            self.combed_dict = self.get_all_from_chap(chapter=self.chapter_txt_var.get())
            f = open(f'chapter_{self.chapter_txt_var.get()}/vocab_types.txt', 'r', encoding='utf8')
            f_str = f.read()
            f_lst = f_str.split('\n')
            self.added_dicts.extend(f_lst[1:])
        else:
            foo = self.create_dict(chapter=self.chapter_txt_var.get(), vocab_type=self.vocab_txt_var.get())
            self.combed_dict.update(foo)
            self.added_dicts.append(self.vocab_txt_var.get())

        for i in range(0, len(self.added_dicts) - 1):
            s += self.added_dicts[i] + ', '
        s += self.added_dicts[-1]
        self.added_dicts_txt.set(s)
        mainframe.update()

    def delete_dict(self):
        s = ''
        if self.vocab_txt_var.get() == 'All':
            foo = self.get_all_from_chap(chapter=self.chapter_txt_var.get())
            for i in foo:
                del self.combed_dict[i]
            f = open(f'chapter_{self.chapter_txt_var.get()}/vocab_types.txt', 'r', encoding='utf8')
            f_str = f.read()
            f_lst = f_str.split('\n')
            for i in f_lst[1:]:
                self.added_dicts.remove(i)
        else:
            foo = self.create_dict(chapter=self.chapter_txt_var.get(), vocab_type=self.vocab_txt_var.get())
            for i in foo:
                del self.combed_dict[i]
            self.added_dicts.remove(self.vocab_txt_var.get())

        for i in range(0, len(self.added_dicts) - 1):
            s += self.added_dicts[i] + ', '
        s += self.added_dicts[-1]
        self.added_dicts_txt.set(s)
        mainframe.update()

    # function will open up the chosen files and combine them into a dictionary, then start the chosen study game
    def start_main(self):
        self.pref_done.state(['disabled'])
        self.add_dict.state(['disabled'])
        self.delete_dict_button.state(['disabled'])

        if self.game_txt.get() == 'Multiple Choice':
            mc = MultipleChoice(referral_dict=self.combed_dict)
            mc.start_mc()
            # self.destroy_pref()
        elif self.game_txt.get() == 'Write':
            w = Write(reference_dict=self.combed_dict)
            w.choose_q()
            # self.destroy_pref()
        elif self.game_txt.get() == 'Type':
            t = Type(reference_dict=self.combed_dict)
            t.get_q_a()
        elif self.game_txt.get() == 'Map':
            k = MapAnimations(reference_dict=self.combed_dict)
            k.create()

    def run(self):
        self.chapter_pref_combo()
        self.vocab_pref_combo()
        self.create_kanji_checkbox()
        self.game_pref_combo()
        self.pref_done_button()
        self.display()


class MultipleChoice:
    def __init__(self, referral_dict):
        self.referral_dict = referral_dict
        self.main_dict = deepcopy(self.referral_dict)
        self.turn_count = 0
        self.amnt_correct = 0
        self.amnt_incorrect = 0
        self.m_choice_mainframe = ttk.Frame(mainframe)
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
        self.m_choice_mainframe.destroy()
        pref_done.state(['!disabled'])
        add_dict.state(['!disabled'])
        delete_dict_button.state(['!disabled'])


class Write:
    def __init__(self, reference_dict):
        self.write_frame = ttk.Frame(mainframe, cursor="pencil")
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

    def clear_canv(self):
        self.canvas.delete('all')
        self.undo_lst = []
    
    def savePosn(self, event):
        self.lastx, self.lasty = event.x, event.y

    def addLine(self, event):
        self.canvas.create_line((self.lastx, self.lasty, event.x, event.y), tags=self.tag, smooth=True, width=1.5)
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
                self.animation_canvas.create_line((j[0], j[1], j[2], j[3]))
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
        self.write_frame.destroy()
        pref_done.state(['!disabled'])
        add_dict.state(['!disabled'])
        delete_dict_button.state(['!disabled'])


class Type:
    def __init__(self, reference_dict):
        self.reference_dict = reference_dict
        self.main_dict = deepcopy(self.reference_dict)
        self.type_frame = ttk.Frame(mainframe)
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
        self.type_frame.destroy()
        pref_done.state(['!disabled'])
        add_dict.state(['!disabled'])
        delete_dict_button.state(['!disabled'])


class MapAnimations:
    def __init__(self, reference_dict):
        self.reference_dict = reference_dict
        self.current_dict_index = 0
        self.canvas_frame = ttk.Frame(mainframe)
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
        self.canvas.create_line((self.lastx, self.lasty, event.x, event.y), tags=self.tag, smooth=True)
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
                self.canvas.create_line((j[0], j[1], j[2], j[3]))
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
        self.canvas_frame.destroy()
        pref_done.state(['!disabled'])
        add_dict.state(['!disabled'])
        delete_dict_button.state(['!disabled'])

    def skip(self):
        self.encoded_lst = []
        self.canvas.delete('all')
        self.start()


Preferences().run()

root.mainloop()