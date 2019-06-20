from tkinter import *
from datetime import *
import random
import time
import threading
from tkinter import messagebox
import sqlite3
import tkinter.font
from functools import partial

#tester 회원번호 : 01012345678
#수업목록 페이지 : 현재시간에서 일주일 이내의 수업목록만 보여진다. 관리자 페이지에서 수업 등록 후 새로고침 버튼을 누르면 변경사항이 반영된다.
#test 수업 : 
#마이페이지 : 수업목록 페이지에서 수업 신청 후 refresh 버튼을 누르면 변경사항이 반영된다.
#관리자 비밀번호 : password

class MainClass(Tk):
    
    def __init__(self, temp_mnum, *args, **kwargs):
        self.mnum = temp_mnum
        
        Tk.__init__(self, *args, **kwargs)
        
        self.title("MMP")
        self.geometry("420x520")
        
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        for F in (ReservationPage, MyPage, ManagerLoginPage, ManagerPage):       
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_frame("ReservationPage")
        
    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

    def destroy_frame(self):
        global UPDATE
        UPDATE=-1
        self.destroy()
        LoginPage()

#-------------------------------------------------------------#       
#----------------- 수업조회 및 예약  페이지 ------------------#
#-------------------------------------------------------------# 
#UPDATE : 수업등록 후 업데이트 시 필요한 전역변수 (초기화)
UPDATE=-1

# DELETE : 마이페이지 업데이트 전 취소 개수
DELETE = 0
class ReservationPage(Frame):
    
    def __init__(self, parent, controller):
        
        Frame.__init__(self, parent)
        self.controller = controller

        # 프레임 전환 메뉴
        mb=Menu(self.controller)
        mb.add_command(label="수업조회", command=lambda: self.controller.show_frame("ReservationPage"))
        mb.add_command(label="마이페이지", command=lambda: self.controller.show_frame("MyPage"))
        mb.add_command(label="관리자페이지", command=lambda: self.controller.show_frame("ManagerLoginPage"))
        self.controller.config(menu=mb)
            
        #제목 label 설정
        fontText=tkinter.font.Font(size=15, weight="bold")
        label1 = Label(self, text="수업 예약 페이지 입니다." + "\n" + "예약/ 취소 하시려는 수업을 클릭 해 주세요!", font = fontText)
        label2 = Label (self, text= "(단, 예약은 1주일 이내의 수업만 가능합니다.)" , fg = "red")
        label3 = Label (self, text= "예약 가능한 수업 : 초록 / 이미  예악한 수업 : 하양 / 정원 초과 수업 : 빨강" ) 
        label1.grid(row=0 , column = 0,pady =10, padx =10)
        label2.grid(row=1 ,column = 0 ,pady =10, padx =10)
        label3.grid(row =2, column = 0)
        self.userNum = self.controller.mnum 

        #self.cvf / self.cv / self.sb : 수업목록 버튼 프레임/캔버스/스크롤바
        self.cvf = Frame(self)
        self.cvf.grid(row=3, column=0, pady = 20)
        self.cv = Canvas(self.cvf)
        self.cv.grid(row=0, column=0)
        self.sb = Scrollbar(self.cvf, orient="vertical", command=self.cv.yview)
        self.sb.grid(row=0, column=1, sticky='ns')
        self.cv.configure(yscrollcommand=self.sb.set)
        #self.classes : 업데이트 시 새로운 Frame 생성
        self.classes ={}
        self.i = 0
        #self.update : 수업목록 업데이트
        self.update()

        refreshBtn = Button(self, text="새로고침", command=self.update)
        refreshBtn.grid(row = 4, column =0)
        logoutBtn = Button(self, text = "로그아웃 하기",command=controller.destroy_frame)
        logoutBtn.grid(row = 5, column =0)

    #수업 예약, 취소 함
    def applyCancel(self, n):
        global UPDATE, DELETE
        
        classNum = str(self.cnum[n])
        now = int(self.nowNum[n])
        conn =sqlite3.connect("mmp.db")
        curs = conn.cursor()
        sql = "SELECT * FROM sugan where mnum = "+ str(self.userNum) +" and cnum ="+classNum+";"
        curs.execute(sql)
        rows = curs.fetchall()
        
        #사용자가  예약한 수업일 경우 취소 여부 묻고 실행
        if len(rows) :
            strInfo = self.name[n] + "를 취소하시겠습니까? \n" + "시간 : " + self.date[n]
            isCancel =  messagebox.askokcancel("취소 창", strInfo)
            if isCancel:
                sql = "delete from sugan where mnum = "+ str(self.userNum)+ " and cnum = " + classNum + ";"
                curs.execute(sql)
                conn.commit()
                UPDATE = -1
                DELETE += 1
                self.refresh()
                self.controller.show_frame("ReservationPage")
        #새로 예약하는 경우 
        else :
            #정원 체크
            sql ="select count(s.cnum) nowNum from class c left join sugan s  on c.cnum = s.cnum where c.cnum = "+classNum +" group by c.cnum"
            curs.execute(sql)
            row = curs.fetchone()
            now = row[0]
            sql ="select cmax from class where cnum = "+ classNum
            curs.execute(sql)
            row = curs.fetchone()
            maxNum = row[0]          

            if int(now)==int(maxNum): #정원이 초과한 경우 예약 불가능
                messagebox.showinfo("정원 초과", "정원이 초과했습니다. 다른 수업을 이용해 주시면 감사하겠습니다.")
                return
            strInfo = self.name[n] + "를 예약하시겠습니까? \n" + "시간 : " + self.date[n]
            isReserve = messagebox.askokcancel("예약 창", strInfo)
            if isReserve:
                sql = "insert into sugan  (mnum, cnum) values ("+str(self.userNum) +","+ classNum +");"
                curs.execute(sql)
                conn.commit()
                UPDATE = -1
                self.refresh()
                self.controller.show_frame("ReservationPage")
      
        # Connection 닫기
        conn.close()
        
    #내가 신청한 수업인지 아닌지 체크  
    def isMyClass(self, mnum, cnum):
        conn = sqlite3.connect("mmp.db")
        curs = conn.cursor()
        sql ="select c.cnum from class c, sugan s where c.cnum = s.cnum and c.cnum = "+str(cnum)+" and s.mnum = "+str(mnum)+" and  CAST(strftime('%s', c.ctime) AS integer ) > CAST(strftime('%s', datetime('now','localtime')) AS integer ) and CAST(strftime('%s', c.ctime) AS integer ) < CAST(strftime('%s', datetime('now','localtime','+7 day')) AS integer ) "
        curs.execute(sql)
        rows = curs.fetchall()
        conn.close()
        if len(rows) == 0:
            return False
        else:
            return True           

    #예약/취소후 화면을 새로 고침하는 함수   
    def refresh(self):
        conn =sqlite3.connect("mmp.db")
        curs = conn.cursor()
        sql = "select c.cnum , c.cname, c.ccontent, c.ctime, count(s.cnum) nowNum, c.cmax from class c left join sugan s  on c.cnum = s.cnum where CAST(strftime('%s', c.ctime) AS integer ) > CAST(strftime('%s', datetime('now','localtime')) AS integer ) and CAST(strftime('%s', c.ctime) AS integer ) < CAST(strftime('%s', datetime('now','localtime','+7 day')) AS integer )  group by c.cnum"
        curs.execute(sql)
        self.rows = curs.fetchall()

        for i in range(0,len(self.rows)):            
            nowNum = str(self.rows[i][4])
            maxNum = str(self.rows[i][5])
            strNum =  "신청 현황  \n" + nowNum + "/" + maxNum
            classNum = self.rows[i][0]
            if self.isMyClass(self.userNum, classNum):
                btnColor = "white"
            else:
                btnColor = "green"
            if nowNum == maxNum  :
               strColor = "red"
            else:
                strColor = "blue"
            #configure 이용해서 Button, Label 상태 update    
            self.numberLabel[i].configure(text = strNum, fg = strColor)
            self.btn[i].configure(bg = btnColor)
        conn.close()

        #update : 수업목록 업데이트
    def update(self):
        global UPDATE
        #수업목록이 변경이 있을 때 or 초기상태 일 때
        if(UPDATE!=0) :
            ##새로운 프레임 생성
            self.i += 1
            self.classes[self.i] = Frame(self.cv)
            self.cv.create_window((0, 0), window=self.classes[self.i], anchor='nw')
            #db 연결
            conn = sqlite3.connect("mmp.db")
            # Connection 으로부터 Cursor 생성
            curs = conn.cursor()
            # SQL문 실행 - 오늘로부터 예약 가능한 7일 이내의 수업 조회
            sql = "select c.cnum , c.cname, c.ccontent, c.ctime, count(s.cnum) nowNum, c.cmax from class c left join sugan s  on c.cnum = s.cnum where CAST(strftime('%s', c.ctime) AS integer ) > CAST(strftime('%s', datetime('now','localtime')) AS integer ) and CAST(strftime('%s', c.ctime) AS integer ) < CAST(strftime('%s', datetime('now','localtime','+7 day')) AS integer )  group by c.cnum"
            curs.execute(sql)
            # 데이타 Fetch
            self.rows = StringVar()
            self.rows = curs.fetchall()
            # Connection 닫기
            conn.close()
            #Label, Frame, Button 변수 초기화
            self.cnum = {}
            self.date = {}
            self.name = {}
            button_identities  =[]
            self.btn ={}
            self.nowNum = {}
            self.timeLabel = {}
            self.classFrame  = {}
            self.numberLabel ={}
            #db에서 select 결과의 갯수 만큼 실행 
            for i in range(0,len(self.rows)):
                #sql문 select 결과를 이용해서 화면에 출력해줄 형태로 변환
                index = i
                self.cnum[i] = self.rows[i][0]
                self.name[i] = self.rows[i][1]
                content = self.rows[i][2]
                self.date[i] = self.rows[i][3]
                self.nowNum[i] = str(self.rows[i][4])
                maxNum = str(self.rows[i][5])
                strTime =  "수업 시간: \n " + self.date[i] 
                strClass = "강좌 : " + self.name[i]+ "\n 내용 : " + content
                strNum =  "신청 현황  \n" + str(self.nowNum[i]) + "/" + maxNum
                if self.isMyClass(self.userNum , self.cnum[i]):
                    btnColor = "white"
                else:
                    btnColor = "green"
                if str(self.nowNum[i]) == maxNum  :
                   strColor = "red"
                else:
                    strColor = "blue" 
                #각 수업에 대한 Button, Label들 정의
                ##새로 생성한 프레임에 배치
                self.timeLabel[i] = Label (self.classes[self.i], text = strTime)
                self.timeLabel[i].grid(row=i, column=0)
                self.numberLabel[i] = Label (self.classes[self.i], text = strNum, fg = strColor)
                self.numberLabel[i].grid(row=i, column=2)
                ##버튼을 클릭했을 때 i값을 전달하면서 applyCancel() 함수 실행
                self.btn [i] = Button(self.classes[self.i], text = strClass, bg = btnColor, width = 25, height = 4, command = partial(self.applyCancel, i))
                self.btn [i].grid(row=i, column=1, padx = 10)
                ##스크롤바 업데이트
                self.classes[self.i].update_idletasks()
                self.cvf.config(width = self.btn[i].winfo_width() * i + self.sb.winfo_width(), height=self.btn[i].winfo_height()*i)
                self.cv.config(scrollregion = self.cv.bbox("all"))
            ##업데이트 완료
            UPDATE=0
#-------------------------------------------------------------

#-------------------------------------------------------------#       
#----------------------- 관리자  페이지 ----------------------#
#-------------------------------------------------------------# 
class ManagerLoginPage(Frame):    
    ##관리자 로그인 페이지 프레임
    def __init__(self, parent, controller):
        
        Frame.__init__(self, parent)
        self.controller = controller

        ###mngpw : 관리자 비밀번호
        self.mngpw="password"

        Label(self, text="관리자 비밀번호", padx=15, pady=10).grid(row=0, column=0, sticky="W")

        ###mngpwSV : 입력한 관리자 비밀번호
        self.mngpwSV = StringVar()
        ###mngpwE : 관리자 비밀번호 입력 Entry
        self.mngpwE = Entry(self, show="*", textvariable=self.mngpwSV)
        self.mngpwE.grid(padx=15, row=1, column=0)
        ###trymnglog : 관리자 로그인 초기화
        self.trymnglog=-1
        self.mngpwE.bind("<Return>", self.bemng)

        ###mnglogB : 관리자 로그인 버튼
        mnglogB = Button(self, text="입력", width=5, command=self.mnglog)
        mnglogB.grid(row=1, column=1)


    ##bemng : 관리자 로그인 시도(enter) 함수
    def bemng(self, event):
        ###관리자 로그인 시도 중
        self.trymnglog=0
        if(self.trymnglog==0):
            self.mnglog()
            ###trymnglog : 관리자 로그인 초기화
            self.trymnglog=-1

    ##mnglog : 관리자 로그인 함수
    def mnglog(self):
        ###관리자 비밀번호와 입력한 관리자 비밀번호가 같으면 로그인 성공
        if(self.mngpw==str(self.mngpwSV.get())):
            ####Entry에 입력한 내용 초기화
            self.mngpwE.delete(0,END)
            ####관리자 페이지 열기
            self.controller.show_frame("ManagerPage")
        ###로그인 실패
        else:
            ####실패 메세지박스 보이기
            messagebox.showinfo("information", "비밀번호가 틀렸습니다.")
            ####Entry에 입력한 내용 초기화
            self.mngpwE.delete(0,END)

class ManagerPage(Frame):
    ##관리자 페이지 프레임
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        ###addcF : 수업등록 프레임
        self.addcF = LabelFrame(self, text="수업등록")
        self.addcF.pack(fill="both", expand="yes")

        ###cName : 수업이름
        Label(self.addcF, text="이　름", padx=20).grid(row=1, column=0)
        self.cName = Entry(self.addcF)
        self.cName.grid(row=1, column=1)

        ###cDate : 수업날짜
        Label(self.addcF, text="날　짜", padx=20).grid(row=2, column=0)
        Label(self.addcF, text="          /").grid(row=2, column=1,sticky="W")
        self.cDate1 = Entry(self.addcF, width=5)
        self.cDate1.grid(row=2, column=1, sticky="W")
        self.cDate2 = Entry(self.addcF, width=5)
        self.cDate2.grid(row=2, column=1)
        Label(self.addcF, text="/          ").grid(row=2, column=1,sticky="E")
        self.cDate3 = Entry(self.addcF, width=5)
        self.cDate3.grid(row=2, column=1, sticky="E")
        Label(self.addcF, text="      H").grid(row=2, column=2, sticky="W")
        self.cDate4 = Entry(self.addcF, width=2)
        self.cDate4.grid(row=2, column=2, padx=5, sticky="W")

        ###mLimit : 수업인원
        Label(self.addcF, text="인　원", padx=20).grid(row=3, column=0)
        self.mLimit = Entry(self.addcF)
        self.mLimit.grid(row=3, column=1)

        ###mText : 수업내용
        Label(self.addcF, text="내　용", padx=20).grid(row=4, column=0, sticky="N")
        self.cText = Text(self.addcF, width=20, height=7)
        self.cText.grid(row=4, column=1)

        ###addcB : 수업등록 버튼
        addcB = Button(self.addcF, text="등록", command=self.addClass, width=5)
        addcB.grid(row=5, column=1, sticky="E", pady=5)

        ###addmF : 회원등록 프레임
        self.addmF = LabelFrame(self, text="회원등록")
        self.addmF.pack(fill="both", expand="yes")

        ###mbNae : 회원이름
        Label(self.addmF, text="이　름", padx=20).grid(row=1, column=0)
        self.mbName = Entry(self.addmF)
        self.mbName.grid(row=1, column=1)

        ###mbNum : 회원번호
        Label(self.addmF, text="번　호", padx=20).grid(row=2, column=0)
        Label(self.addmF, text="          -").grid(row=2, column=1,sticky="W")
        self.mbNum1 = Entry(self.addmF, width=5)
        self.mbNum1.grid(row=2, column=1, sticky="W")
        self.mbNum2 = Entry(self.addmF, width=5)
        self.mbNum2.grid(row=2, column=1)
        Label(self.addmF, text="-          ").grid(row=2, column=1,sticky="E")
        self.mbNum3 = Entry(self.addmF, width=5)
        self.mbNum3.grid(row=2, column=1, sticky="E")

        ###addmB : 회원등록 버튼
        addmB = Button(self.addmF, text="등록", command=self.addMember, width=5)
        addmB.grid(row=3, column=1, sticky="E", pady=5)

        ###mnglogoutB : 관리자 로그아웃 버튼
        mnglogoutB = Button(self, text="관리자 로그아웃", command=self.mnglogout)
        mnglogoutB.pack(pady=5)

    ##addClass : 수업등록 함수
    def addClass(self):
        ###등록 질문 메세지박스
        if (messagebox.askokcancel("Redirecting", "등록하시겠습니까?")):
            ###확인 버튼 클릭 시
            ####데이터베이스 연결
            self.conn=sqlite3.connect("mmp.db")
            self.cur = self.conn.cursor()
            ####입력 내용 오류 확인
            if(len(self.cDate1.get())!=4 or (int(self.cDate2.get())<1 or int(self.cDate2.get())>12) or (int(self.cDate3.get())<1 or int(self.cDate3.get())>31) or (int(self.cDate4.get())<0 or int(self.cDate4.get())>24) or len(self.cText.get(1.0,END).strip())>100) :
                messagebox.showinfo("information","등록 실패")
            ###수업등록
            else:
                try :
                    global UPDATE
                    date = str(self.cDate1.get()) + "-" + str(self.cDate2.get()).zfill(2) + "-" + str(self.cDate3.get()).zfill(2) + " " + str(self.cDate4.get()).zfill(2) + ":00"
                    sql = """INSERT INTO class (cname, ctime, cmax, ccontent) VALUES(?, ?, ?, ?)"""
                    val = (str(self.cName.get()), date, int(str(self.mLimit.get())), str(self.cText.get(1.0,END)).strip())
                    self.cur.execute(sql, val)
                    self.conn.commit()
                    messagebox.showinfo("information","등록 완료")
                    ####Entry에 입력한 내용 초기화
                    self.resetmn()
                    ####수업조회 업데이트 필요
                    UPDATE=1
                except :
                    self.conn.rollback()
                    messagebox.showinfo("information","등록 실패")
            ####데이터베이스 닫기
            self.conn.close()

    ##addMember : 회원등록 함수
    def addMember(self):
        ###등록 질문 메세지박스
        if (messagebox.askokcancel("Redirecting", "등록하시겠습니까?")):
            ###확인 버튼 클릭 시
            ####데이터베이스 연결
            self.conn=sqlite3.connect("mmp.db")
            self.cur = self.conn.cursor()
            ####입력 내용 오류 확인
            if(str(self.mbNum1.get())!="010" or (len(self.mbNum2.get()) and len(self.mbNum3.get()))!=4) :
                messagebox.showinfo("information","등록 실패")
            ###회원등록
            else:
                try :
                    sql = """INSERT INTO member (mname, mphone) VALUES (?, ?)"""
                    val = (str(self.mbName.get()), str(self.mbNum1.get())+str(self.mbNum2.get())+str(self.mbNum3.get()))
                    self.cur.execute(sql, val)
                    self.conn.commit()
                    messagebox.showinfo("information","등록 완료")
                    ####Entry에 입력한 내용 초기화
                    self.resetmn()
                ####데이터 입력 실패
                except :
                    self.conn.rollback()
                    messagebox.showinfo("information","등록 실패")
            ####데이터베이스 닫기
            self.conn.close()
        
    ## resetmn : 관리자 페이지 초기화
    def resetmn(self):
        self.cName.delete(0,END)
        self.cDate1.delete(0,END)
        self.cDate2.delete(0,END)
        self.cDate3.delete(0,END)
        self.cDate4.delete(0,END)
        self.mLimit.delete(0,END)
        self.cText.delete(1.0,END)
        self.mbName.delete(0,END)
        self.mbNum1.delete(0,END)
        self.mbNum2.delete(0,END)
        self.mbNum3.delete(0,END)
        
    ##mnglogout : 관리자 페이지 로그아웃 함수
    def mnglogout(self):
        ###프레임 초기화
        self.resetmn()
        ###페이지 이동
        self.controller.show_frame("ReservationPage")
#-------------------------------------------------------------

#-------------------------------------------------------------#       
#------------------------- 마이페이지 ------------------------#
#-------------------------------------------------------------# 
class MyPage(Frame):
    
    def __init__(self, parent, controller):
        
        Frame.__init__(self, parent)
        self.controller = controller

        # DB 연결
        conn = sqlite3.connect("mmp.db")
        
        # Connection 으로부터 Cursor 생성
        curs = conn.cursor()
 
        # SQL문 실행
        sql = "select mname from member where mnum = " + str(self.controller.mnum) + ";"
        curs.execute(sql)
 
        # 데이타 Fetch
        rows = curs.fetchall()

        # Connection 닫기
        conn.close()

        # 처음으로 MyPage 프레임 생성
        self.first = 0

        # 'XX님의 페이지'라는 라벨 출력
        font1 = tkinter.font.Font(size=15, weight="bold")
        label = Label(self, text="This is " + rows[0][0] + "'s Page", font=font1)
        label.grid(row=0, column=0, pady=10)

        # bottomWindow라는 프레임 객체 생성
        self.bottomWindow = Frame(self)
        self.bottomWindow.grid(row = 1)

        # Canvas/Scrollbar 생성
        self.cv = Canvas(self.bottomWindow)
        self.cv.grid(row=0, column=0)
        self.sb = Scrollbar(self.bottomWindow, orient="vertical", command=self.cv.yview)
        self.sb.grid(row=0, column=1, sticky='ns')
        self.cv.configure(yscrollcommand=self.sb.set)

        #self.classes : 업데이트 시 새로운 Frame 생성
        self.classes ={}
        self.i = 0

        # 강좌명 출력
        self.mypage()

        # 버튼
        refreshBtn = Button(self, text="새로고침",command=self.mypage)
        logoutBtn = Button(self, text = "로그아웃 하기",command=controller.destroy_frame)
        
        refreshBtn.grid(row=2, column=0)
        logoutBtn.grid(row=3, column=0)


    # 강좌명 bottomWindow 프레임에 출력
    def mypage(self):
        global UPDATE, DELETE

        if (self.first != 1 or UPDATE != 0):
            # DB 연결
            conn = sqlite3.connect("mmp.db")
        
            # Connection 으로부터 Cursor 생성
            curs = conn.cursor()
 
            # SQL문 실행
            sql = "select c.cname, c.ccontent, strftime('%Y-%m-%d %H:%M', c.ctime), count(s.cnum) nowNum, c.cmax from class c inner join sugan s on c.cnum = s.cnum where c.cnum in(select s.cnum from sugan s where s.mnum =" + str(self.controller.mnum) + ") group by c.cnum order by c.ctime desc"
            curs.execute(sql)
        
              
            # 데이타 Fetch
            self.rows = curs.fetchall()

            # Connection 닫기
            conn.close()

            while (DELETE > 0):
                self.classes[self.i].destroy()
                self.i -= 1
                DELETE -= 1

            ##새로운 프레임 생성
            self.i += 1
            self.classes[self.i] = Frame(self.cv)
            self.cv.create_window((0, 0), window=self.classes[self.i], anchor='nw')

            now = datetime.now()

            self.label = {}
    
            # 내가 듣는 수업 출력
            for i in range(0, len(self.rows)):
                if (self.rows[i][2] > str(now)):
                    strColor = "blue"
                    font2 = tkinter.font.Font(size=10, overstrike=False)
                else:
                    strColor = "black"
                    font2 = tkinter.font.Font(size=10, overstrike=True)
                date = self.rows[i][2]
                name = self.rows[i][0]
                content = self.rows[i][1]
                nowNum = self.rows[i][3]
                max = self.rows[i][4]

                text1 = date.split(' ')[0] + "\n" + date.split(' ')[1]
                text2 = "강좌명: " + name
                text3 = "신청 현황: " + str(nowNum) + "/" + str(max)
                
                self.label[i] = Label(self.classes[self.i], text=text1, font=font2, fg=strColor)
                self.label[i].grid(row=i, column=0, padx=25, pady=10)
                Label(self.classes[self.i], text=text2, font=font2, fg=strColor).grid(row=i, column=1, padx=20, pady=10)
                Label(self.classes[self.i], text=text3, font=font2, fg=strColor).grid(row=i, column=2, padx=20, pady=10)
            
                # 스크롤바 업데이트
                self.classes[self.i].update_idletasks()
                self.bottomWindow.config(width = self.label[i].winfo_width() * i + self.sb.winfo_width(), height=self.label[i].winfo_height() * i)
                self.cv.config(scrollregion = self.cv.bbox("all"))

            # 업데이트 완료
            self.first = 1
            UPDATE = 0
            DELETE = 0
#---------------------------------------------------------
            
#---------------------------------------------------------#       
#--------------------- 로그인페이지 ----------------------#
#---------------------------------------------------------# 
class LoginPage(Tk):

    def __init__(self):
        self.temp_mnum = 0

        Tk.__init__(self)
        self.title("login")

        # DB 연결
        conn = sqlite3.connect("mmp.db")
        
        # Connection 으로부터 Cursor 생성
        curs = conn.cursor()
 
        # SQL문 실행
        sql = "select * from member"
        curs.execute(sql)
 
        # 데이타 Fetch
        self.rows = curs.fetchall()

        # Connection 닫기
        conn.close()

        self.name = StringVar()

        # 회원번호를 입력해 달라는 Label
        Label(self, text="회원번호를 입력해주세요.").grid(row=1, padx=10, pady=10)


        #이미지
        photo = PhotoImage(file = "./health.PNG")
        w = Label(self, image = photo)
        w.photo = photo
        w.grid(row=0)
         
        # 회원번호 입력 Entry
        logID = Entry(self, textvariable=self.name)
        logID.bind("<Return>", self.login)   # 엔터 키
        logID.grid(row=2, padx=10, pady=10)
            
        # 로그인 Button
        btnLogin = Button(self, text="로그인", command=self.login)
        btnLogin.grid(row=3, padx=10, pady=10)


    # 회원번호가 db에 있는지 확인
    def login(self, event=None):
        for i in range(0, len(self.rows)):
            if (str(self.name.get()) == str(self.rows[i][2])):
                self.temp_mnum = self.rows[i][0]
                self.destroy()
                MainClass(self.temp_mnum).mainloop()
                break;
            elif (len(self.rows) - 1 == i):
                messagebox.showwarning("안내", "로그인에 실패하였습니다.")
#---------------------------------------------------------
                
if __name__ == "__main__":
    #초기 로그인 사용자 추가
    LoginPage()    
